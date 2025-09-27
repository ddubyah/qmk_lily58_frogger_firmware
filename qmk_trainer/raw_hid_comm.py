"""
Raw HID Communication module for QMK keyboards.
This bypasses VIA and communicates directly with Raw HID endpoint.
"""

import hid
from typing import List, Tuple, Dict, Optional
import struct
import time

# QMK Raw HID Constants (different from VIA)
RAW_VENDOR_ID = 0x7171    # Same as VIA
RAW_PRODUCT_ID = 0x0002   # Same as VIA
RAW_USAGE_PAGE = 0xFF60   # Same as VIA
RAW_USAGE = 0x61          # Raw HID usage (different from VIA)

# Our Custom Commands (same as before)
CMD_GET_LED_MAP = 0x01
CMD_HIGHLIGHT_LEDS = 0x02
CMD_TRAINER_BEGIN = 0x03
CMD_TRAINER_END = 0x04
CMD_OLED_TEXT = 0x10
CMD_GET_FIRMWARE_INFO = 0x20

def get_raw_hid_device():
    """Find and connect to Raw HID device endpoint."""
    devices = hid.enumerate(RAW_VENDOR_ID, RAW_PRODUCT_ID)

    # Look for Raw HID interface specifically
    raw_hid_devices = []
    for d in devices:
        if d['usage_page'] == RAW_USAGE_PAGE and d['usage'] == RAW_USAGE:
            raw_hid_devices.append(d)

    if not raw_hid_devices:
        raise RuntimeError(
            f"No Raw HID device found. Expected VID:PID {RAW_VENDOR_ID:04X}:{RAW_PRODUCT_ID:04X} "
            f"with usage page {RAW_USAGE_PAGE:04X} and usage {RAW_USAGE:02X}"
        )

    device_info = raw_hid_devices[0]
    device = hid.device()
    device.open_path(device_info['path'])

    return device

def send_raw_hid_command(device, command: int, payload: bytes = b"") -> bytes:
    """Send Raw HID command and receive response."""
    # Raw HID uses 32-byte reports (no report ID prefix)
    report = bytearray(32)
    report[0] = command

    if payload:
        payload_len = min(len(payload), 31)  # Max 31 bytes payload
        report[1:1+payload_len] = payload[:payload_len]

    device.write(bytes(report))
    response = device.read(32, timeout=1000)
    return bytes(response)

def get_matrix_to_led_map_raw(device) -> Dict[Tuple[int, int], int]:
    """Retrieve matrix position to LED index mapping via Raw HID."""
    response = send_raw_hid_command(device, CMD_GET_LED_MAP)

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

def highlight_leds_with_color_raw(
    device,
    led_indexes: List[int],
    color_rgb: Tuple[int, int, int],
    duration_ms: int
) -> bool:
    """Highlight specified LEDs with given color and duration via Raw HID."""
    r, g, b = color_rgb

    # Payload: [count, led1, led2, ..., r, g, b, duration_low, duration_high]
    payload = bytearray()
    payload.append(len(led_indexes))
    payload.extend(led_indexes[:20])  # Limit to 20 LEDs max
    payload.extend([r, g, b])
    payload.extend(struct.pack('<H', duration_ms))  # Little-endian 16-bit

    response = send_raw_hid_command(device, CMD_HIGHLIGHT_LEDS, bytes(payload))

    # Check for acknowledgment
    return len(response) >= 2 and response[0] == CMD_HIGHLIGHT_LEDS and response[1] == 0x01

def send_trainer_begin_raw(device) -> bool:
    """Start trainer mode via Raw HID."""
    response = send_raw_hid_command(device, CMD_TRAINER_BEGIN)
    return len(response) >= 2 and response[0] == CMD_TRAINER_BEGIN and response[1] == 0x01

def send_trainer_end_raw(device) -> bool:
    """End trainer mode via Raw HID."""
    response = send_raw_hid_command(device, CMD_TRAINER_END)
    return len(response) >= 2 and response[0] == CMD_TRAINER_END and response[1] == 0x01

def send_oled_text_raw(device, text: str) -> bool:
    """Send text to display on OLED via Raw HID."""
    text_bytes = text.encode('utf-8')[:31]  # Limit to 31 bytes
    response = send_raw_hid_command(device, CMD_OLED_TEXT, text_bytes)
    return len(response) >= 2 and response[0] == CMD_OLED_TEXT and response[1] == 0x01

def get_firmware_info_raw(device) -> Dict[str, str]:
    """Get firmware build information via Raw HID."""
    try:
        response = send_raw_hid_command(device, CMD_GET_FIRMWARE_INFO)

        if response[0] == CMD_GET_FIRMWARE_INFO:
            # Parse version and timestamp from response
            version_end = 1
            while version_end < len(response) and response[version_end] != 0:
                version_end += 1

            version = bytes(response[1:version_end]).decode('utf-8', errors='ignore')
            timestamp = bytes(response[version_end+1:]).decode('utf-8', errors='ignore').rstrip('\\x00')

            return {
                "firmware_version": version,
                "build_timestamp": timestamp,
                "trainer_enabled": "Yes (Raw HID)",
                "communication": "Raw HID"
            }
        else:
            return {"error": "Invalid firmware info response"}
    except Exception as e:
        return {"error": str(e)}

class RawHIDDevice:
    """Context manager for Raw HID device connections."""

    def __init__(self):
        self.device = None
        self.matrix_to_led_map: Dict[Tuple[int, int], int] = {}

    def __enter__(self):
        self.device = get_raw_hid_device()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.device:
            # Always end trainer mode on exit
            try:
                send_trainer_end_raw(self.device)
            except:
                pass  # Best effort cleanup
            self.device.close()

    def load_mappings(self):
        """Load LED mapping from device."""
        if not self.device:
            raise RuntimeError("Device not connected")

        self.matrix_to_led_map = get_matrix_to_led_map_raw(self.device)

    def highlight_keys(self, positions: List[Tuple[int, int]], color: Tuple[int, int, int], duration: int) -> bool:
        """Highlight keys at given matrix positions."""
        if not self.device or not self.matrix_to_led_map:
            raise RuntimeError("Device not connected or mappings not loaded")

        led_indexes = []
        for pos in positions:
            if pos in self.matrix_to_led_map:
                led_indexes.append(self.matrix_to_led_map[pos])

        if led_indexes:
            return highlight_leds_with_color_raw(self.device, led_indexes, color, duration)
        return False