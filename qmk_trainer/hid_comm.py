"""
HID Communication module for VIA-compatible keyboards.
Handles device detection, keymap reading, and trainer commands.
"""

import hid
from typing import List, Tuple, Dict, Optional
import struct
import time

# VIA Protocol Constants
VIA_VENDOR_ID = 0x7171
VIA_PRODUCT_ID = 0x0002
VIA_USAGE_PAGE = 0xFF60

# VIA Command IDs (from VIA protocol specification)
VIA_COMMAND_GET_PROTOCOL_VERSION = 0x01
VIA_COMMAND_GET_KEYBOARD_VALUE = 0x02
VIA_COMMAND_SET_KEYBOARD_VALUE = 0x03
VIA_COMMAND_DYNAMIC_KEYMAP_GET_KEYCODE = 0x04
VIA_COMMAND_DYNAMIC_KEYMAP_SET_KEYCODE = 0x05
VIA_COMMAND_DYNAMIC_KEYMAP_RESET = 0x06
VIA_COMMAND_CUSTOM_VALUE = 0x07
VIA_COMMAND_CUSTOM_GET_VALUE = 0x08
VIA_COMMAND_CUSTOM_SET_VALUE = 0x09
VIA_COMMAND_CUSTOM_SAVE = 0x0A
VIA_COMMAND_EEPROM_RESET = 0x0B
VIA_COMMAND_BOOTLOADER_JUMP = 0x0C

# Our Custom Commands (added to firmware)
CMD_GET_LED_MAP = 0x01
CMD_HIGHLIGHT_LEDS = 0x02
CMD_TRAINER_BEGIN = 0x03
CMD_TRAINER_END = 0x04
CMD_OLED_TEXT = 0x10
CMD_GET_FIRMWARE_INFO = 0x20

def get_via_device():
    """Find and connect to VIA-compatible device."""
    devices = hid.enumerate(VIA_VENDOR_ID, VIA_PRODUCT_ID)
    via_devices = [d for d in devices if d['usage_page'] == VIA_USAGE_PAGE]

    if not via_devices:
        raise RuntimeError(
            f"No VIA device found. Expected VID:PID {VIA_VENDOR_ID:04X}:{VIA_PRODUCT_ID:04X} "
            f"with usage page {VIA_USAGE_PAGE:04X}"
        )

    device_info = via_devices[0]
    device = hid.device()
    device.open_path(device_info['path'])

    # Verify protocol version
    try:
        version = get_protocol_version(device)
        if version < 7:  # Minimum VIA protocol version
            print(f"Warning: VIA protocol version {version} may not support all features")
    except Exception as e:
        print(f"Warning: Could not verify VIA protocol version: {e}")

    return device

def get_protocol_version(device) -> int:
    """Get VIA protocol version from device."""
    response = send_via_command(device, VIA_COMMAND_GET_PROTOCOL_VERSION)
    return struct.unpack('>H', response[1:3])[0]

def send_via_command(device, command: int, payload: bytes = b"") -> bytes:
    """Send VIA command and receive response."""
    # VIA uses 32-byte reports
    report = bytearray(33)  # Report ID + 32 bytes
    report[0] = 0x00  # Report ID
    report[1] = command

    if payload:
        payload_len = min(len(payload), 30)  # Max 30 bytes payload
        report[2:2+payload_len] = payload[:payload_len]

    device.write(bytes(report))
    response = device.read(32)
    return bytes(response)

def send_custom_command(device, command: int, payload: bytes = b"") -> bytes:
    """Send custom command via VIA_COMMAND_CUSTOM_VALUE."""
    # Custom commands are sent as VIA_COMMAND_CUSTOM_VALUE with our command as first payload byte
    custom_payload = bytes([command]) + payload
    return send_via_command(device, VIA_COMMAND_CUSTOM_VALUE, custom_payload)

def get_matrix_to_led_map(device) -> Dict[Tuple[int, int], int]:
    """Retrieve matrix position to LED index mapping from device."""
    response = send_custom_command(device, CMD_GET_LED_MAP)
    
    matrix_to_led = {}
    
    # Parse response: [cmd_echo, row, col, led_idx, row, col, led_idx, ...]
    if response[0] == CMD_GET_LED_MAP:
        idx = 1
        while idx + 2 < len(response) and response[idx] != 0:
            row = response[idx]
            col = response[idx + 1] 
            led_idx = response[idx + 2]
            
            if row < 255 and col < 255 and led_idx < 255:  # Valid entries
                matrix_to_led[(row, col)] = led_idx
            
            idx += 3
    
    return matrix_to_led

def get_keycode_at_location(device, layer: int, row: int, col: int) -> int:
    """Get keycode at specific matrix location and layer."""
    payload = struct.pack('BBB', layer, row, col)
    response = send_via_command(device, VIA_COMMAND_DYNAMIC_KEYMAP_GET_KEYCODE, payload)
    
    # Response format: [layer, row, col, keycode_low, keycode_high]  
    if len(response) >= 5 and response[0] == layer and response[1] == row and response[2] == col:
        keycode = struct.unpack('<H', response[3:5])[0]  # Little-endian 16-bit
        return keycode
    
    return 0  # KC_NO

def scan_full_keymap(device, layers: int = 5, rows: int = 5, cols: int = 6) -> Dict[int, Dict[Tuple[int, int], int]]:
    """Scan the complete keymap from the device.
    
    Returns a dictionary mapping layer -> {(row, col): keycode}
    This eliminates the need for manual keymap export from VIA.
    """
    keymap = {}
    
    for layer in range(layers):
        keymap[layer] = {}
        for row in range(rows):
            for col in range(cols):
                try:
                    keycode = get_keycode_at_location(device, layer, row, col)
                    if keycode != 0:  # Skip empty positions
                        keymap[layer][(row, col)] = keycode
                    time.sleep(0.001)  # Small delay to avoid overwhelming device
                except Exception as e:
                    print(f"Warning: Could not read keycode at layer {layer}, row {row}, col {col}: {e}")
    
    return keymap

def highlight_leds_with_color(
    device, 
    led_indexes: List[int], 
    color_rgb: Tuple[int, int, int], 
    duration_ms: int
) -> None:
    """Highlight specified LEDs with given color and duration."""
    r, g, b = color_rgb
    
    # Payload: [count, led1, led2, ..., r, g, b, duration_low, duration_high]
    payload = bytearray()
    payload.append(len(led_indexes))
    payload.extend(led_indexes[:20])  # Limit to 20 LEDs max
    payload.extend([r, g, b])
    payload.extend(struct.pack('<H', duration_ms))  # Little-endian 16-bit
    
    send_custom_command(device, CMD_HIGHLIGHT_LEDS, bytes(payload))

def send_trainer_begin(device) -> None:
    """Start trainer mode - saves RGB state and sets backdrop."""
    send_custom_command(device, CMD_TRAINER_BEGIN)

def send_trainer_end(device) -> None:
    """End trainer mode - restores RGB state."""
    send_custom_command(device, CMD_TRAINER_END)

def send_oled_text(device, text: str) -> None:
    """Send text to display on OLED."""
    text_bytes = text.encode('utf-8')[:30]  # Limit to 30 bytes
    send_custom_command(device, CMD_OLED_TEXT, text_bytes)

def get_firmware_info(device) -> Dict[str, str]:
    """Get firmware build information."""
    try:
        response = send_custom_command(device, CMD_GET_FIRMWARE_INFO)

        if response[0] == CMD_GET_FIRMWARE_INFO:
            # Parse version and timestamp from response
            version_end = 1
            while version_end < len(response) and response[version_end] != 0:
                version_end += 1

            version = bytes(response[1:version_end]).decode('utf-8', errors='ignore')
            timestamp = bytes(response[version_end+1:]).decode('utf-8', errors='ignore').rstrip('\x00')

            return {
                "firmware_version": version,
                "build_timestamp": timestamp,
                "trainer_enabled": "Yes"
            }
        else:
            return {"error": "Invalid firmware info response"}
    except Exception as e:
        return {"error": str(e)}

def get_device_info(device) -> Dict[str, str]:
    """Get basic device information for debugging."""
    try:
        # Get some basic keyboard values for identification
        basic_info = {
            "protocol_version": str(get_protocol_version(device)),
            "connected": "Yes",
        }

        # Add firmware info if available
        firmware_info = get_firmware_info(device)
        basic_info.update(firmware_info)

        return basic_info
    except Exception as e:
        return {
            "error": str(e),
            "connected": "Unknown"
        }

class VIADevice:
    """Context manager for VIA device connections."""
    
    def __init__(self):
        self.device = None
        self.matrix_to_led_map: Dict[Tuple[int, int], int] = {}
        self.keymap: Dict[int, Dict[Tuple[int, int], int]] = {}
    
    def __enter__(self):
        self.device = get_via_device()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.device:
            # Always end trainer mode on exit
            try:
                send_trainer_end(self.device)
            except:
                pass  # Best effort cleanup
            self.device.close()
    
    def load_mappings(self):
        """Load LED mapping and keymap from device."""
        if not self.device:
            raise RuntimeError("Device not connected")
        
        self.matrix_to_led_map = get_matrix_to_led_map(self.device)
        self.keymap = scan_full_keymap(self.device)
    
    def highlight_keys(self, positions: List[Tuple[int, int]], color: Tuple[int, int, int], duration: int):
        """Highlight keys at given matrix positions."""
        if not self.device or not self.matrix_to_led_map:
            raise RuntimeError("Device not connected or mappings not loaded")
        
        led_indexes = []
        for pos in positions:
            if pos in self.matrix_to_led_map:
                led_indexes.append(self.matrix_to_led_map[pos])
        
        if led_indexes:
            highlight_leds_with_color(self.device, led_indexes, color, duration)