"""
Chord mapping system for FrogPad one-handed keyboard layout.
Maps characters to matrix positions and layers for LED highlighting.
"""

from typing import Dict, List, Tuple, Optional, Set
import time

# QMK Keycode constants (basic keycodes)
KC_A = 0x04
KC_B = 0x05
KC_C = 0x06
KC_D = 0x07
KC_E = 0x08
KC_F = 0x09
KC_G = 0x0A
KC_H = 0x0B
KC_I = 0x0C
KC_J = 0x0D
KC_K = 0x0E
KC_L = 0x0F
KC_M = 0x10
KC_N = 0x11
KC_O = 0x12
KC_P = 0x13
KC_Q = 0x14
KC_R = 0x15
KC_S = 0x16
KC_T = 0x17
KC_U = 0x18
KC_V = 0x19
KC_W = 0x1A
KC_X = 0x1B
KC_Y = 0x1C
KC_Z = 0x1D

KC_1 = 0x1E
KC_2 = 0x1F
KC_3 = 0x20
KC_4 = 0x21
KC_5 = 0x22
KC_6 = 0x23
KC_7 = 0x24
KC_8 = 0x25
KC_9 = 0x26
KC_0 = 0x27

KC_SPACE = 0x2C
KC_ENTER = 0x28
KC_TAB = 0x2B
KC_BACKSPACE = 0x2A

# Layer tap and modifier keycodes (example ranges)
QK_LAYER_TAP = 0x4000
QK_MOD_TAP = 0x6000
QK_MOMENTARY = 0x5100

def get_via_device():
    """Import here to avoid circular imports."""
    from .hid_comm import get_via_device
    return get_via_device()

def get_matrix_to_led_map(device):
    """Import here to avoid circular imports.""" 
    from .hid_comm import get_matrix_to_led_map
    return get_matrix_to_led_map(device)

def scan_full_keymap(device):
    """Import here to avoid circular imports."""
    from .hid_comm import scan_full_keymap
    return scan_full_keymap(device)

def extract_base_keycode(keycode: int) -> int:
    """Extract base keycode from modified keycodes (layer tap, mod tap, etc)."""
    if keycode >= QK_LAYER_TAP and keycode < (QK_LAYER_TAP + 0x1000):
        return keycode & 0xFF  # Layer tap - base keycode in lower 8 bits
    elif keycode >= QK_MOD_TAP and keycode < (QK_MOD_TAP + 0x1000): 
        return keycode & 0xFF  # Mod tap - base keycode in lower 8 bits
    elif keycode >= QK_MOMENTARY and keycode < (QK_MOMENTARY + 0x100):
        return 0  # Momentary layer - no base keycode
    else:
        return keycode  # Regular keycode

# FrogPad chord definitions based on authentic FrogPad layout
# Format: character -> [(row, col, layer), ...]
# Note: These are example positions - actual positions will be discovered from device keymap
FROGPAD_CHORDS = {
    # Single letters (most common positions)
    'a': [(2, 1)],  # A key position
    'e': [(1, 3)],  # E key position  
    'i': [(1, 8)],  # I key position
    'o': [(1, 9)],  # O key position
    'u': [(1, 7)],  # U key position
    
    't': [(1, 4)],  # T key position
    'n': [(3, 8)],  # N key position
    's': [(2, 2)],  # S key position
    'r': [(1, 4)],  # R key position
    'l': [(2, 9)],  # L key position
    
    # Two-key chords
    'h': [(2, 1), (2, 2)],      # A+S
    'd': [(1, 3), (2, 2)],      # E+S
    'c': [(2, 1), (1, 3)],      # A+E
    'f': [(2, 2), (1, 4)],      # S+T
    'p': [(1, 8), (1, 9)],      # I+O
    'b': [(2, 1), (1, 7)],      # A+U
    'v': [(2, 1), (1, 8)],      # A+I
    'k': [(1, 8), (2, 9)],      # I+L
    'j': [(1, 7), (1, 8)],      # U+I
    'w': [(1, 3), (1, 7)],      # E+U
    'g': [(1, 3), (1, 8)],      # E+I
    'm': [(1, 7), (1, 9)],      # U+O
    'y': [(1, 4), (1, 7)],      # T+U
    'x': [(2, 1), (2, 9)],      # A+L
    'z': [(2, 2), (2, 9)],      # S+L
    'q': [(1, 4), (1, 9)],      # T+O
    
    # Three-key chords for less common letters
    
    # Numbers (using layer switching)
    '1': [(0, 1)],   # Number row
    '2': [(0, 2)],
    '3': [(0, 3)], 
    '4': [(0, 4)],
    '5': [(0, 5)],
    '6': [(0, 6)],
    '7': [(0, 7)],
    '8': [(0, 8)],
    '9': [(0, 9)],
    '0': [(0, 0)],
    
    # Common punctuation
    ' ': [(4, 3)],   # Space
    '.': [(3, 11)],  # Period
    ',': [(3, 10)],  # Comma
    '?': [(2, 1), (3, 11)],      # A + period
    '!': [(1, 3), (3, 11)],      # E + period
    
    # Uppercase letters (same positions but with shift layer)
    'A': [(2, 1)],   # Will be handled by layer detection
    'E': [(1, 3)],
    'I': [(1, 8)],
    'O': [(1, 9)],
    'U': [(1, 7)],
    'T': [(1, 4)],
    'N': [(3, 8)],
    'S': [(2, 2)],
    'R': [(1, 4)],
    'L': [(2, 9)],
}

class ChordMapper:
    """Maps characters to keyboard matrix positions using device keymap analysis."""
    
    def __init__(self, device=None):
        self.device = device
        self.matrix_to_led_map: Dict[Tuple[int, int], int] = {}
        self.keymap: Dict[int, Dict[Tuple[int, int], int]] = {}
        self.char_to_positions: Dict[str, List[Tuple[int, int, int]]] = {}
        self.keycode_to_positions: Dict[int, List[Tuple[int, int, int]]] = {}
        
    def load_from_device(self, device=None):
        """Load keymap and LED mapping from connected device."""
        if device:
            self.device = device
        
        if not self.device:
            raise RuntimeError("No device connected")
        
        # Load mappings from device
        self.matrix_to_led_map = get_matrix_to_led_map(self.device)
        self.keymap = scan_full_keymap(self.device)
        
        # Build reverse mapping: keycode -> [(layer, row, col), ...]
        self._build_keycode_mapping()
        
        # Build character mapping using discovered positions
        self._build_character_mapping()
    
    def _build_keycode_mapping(self):
        """Build mapping from keycodes to their positions in the keymap."""
        self.keycode_to_positions.clear()
        
        for layer, layer_map in self.keymap.items():
            for (row, col), keycode in layer_map.items():
                base_keycode = extract_base_keycode(keycode)
                
                if base_keycode not in self.keycode_to_positions:
                    self.keycode_to_positions[base_keycode] = []
                
                self.keycode_to_positions[base_keycode].append((layer, row, col))
    
    def _build_character_mapping(self):
        """Build character to matrix position mapping using actual device keymap."""
        self.char_to_positions.clear()
        
        # Basic letter mapping
        letter_keycodes = {
            'a': KC_A, 'b': KC_B, 'c': KC_C, 'd': KC_D, 'e': KC_E, 'f': KC_F,
            'g': KC_G, 'h': KC_H, 'i': KC_I, 'j': KC_J, 'k': KC_K, 'l': KC_L,
            'm': KC_M, 'n': KC_N, 'o': KC_O, 'p': KC_P, 'q': KC_Q, 'r': KC_R,
            's': KC_S, 't': KC_T, 'u': KC_U, 'v': KC_V, 'w': KC_W, 'x': KC_X,
            'y': KC_Y, 'z': KC_Z,
        }
        
        # Map letters to their actual positions
        for char, keycode in letter_keycodes.items():
            if keycode in self.keycode_to_positions:
                self.char_to_positions[char] = self.keycode_to_positions[keycode]
                # Also map uppercase
                self.char_to_positions[char.upper()] = self.keycode_to_positions[keycode]
        
        # Number mapping
        number_keycodes = {
            '0': KC_0, '1': KC_1, '2': KC_2, '3': KC_3, '4': KC_4,
            '5': KC_5, '6': KC_6, '7': KC_7, '8': KC_8, '9': KC_9,
        }
        
        for char, keycode in number_keycodes.items():
            if keycode in self.keycode_to_positions:
                self.char_to_positions[char] = self.keycode_to_positions[keycode]
        
        # Special characters
        special_keycodes = {
            ' ': KC_SPACE,
            '\n': KC_ENTER,
            '\t': KC_TAB,
        }
        
        for char, keycode in special_keycodes.items():
            if keycode in self.keycode_to_positions:
                self.char_to_positions[char] = self.keycode_to_positions[keycode]
    
    def char_to_leds_with_layers(
        self, 
        char: str, 
        layer_colors: Dict[int, Tuple[int, int, int]]
    ) -> List[Tuple[int, Tuple[int, int, int]]]:
        """
        Map character to LED indexes with layer-specific colors.
        Returns list of (led_index, (r, g, b)) tuples.
        """
        if char not in self.char_to_positions:
            return []
        
        led_info = []
        
        for layer, row, col in self.char_to_positions[char]:
            # Get LED index for this matrix position
            if (row, col) in self.matrix_to_led_map:
                led_idx = self.matrix_to_led_map[(row, col)]
                color = layer_colors.get(layer, (255, 255, 255))  # Default white
                led_info.append((led_idx, color))
        
        return led_info
    
    def get_positions_for_char(self, char: str) -> List[Tuple[int, int, int]]:
        """Get matrix positions (layer, row, col) for a character."""
        return self.char_to_positions.get(char, [])
    
    def get_available_characters(self) -> Set[str]:
        """Get all characters that can be mapped."""
        return set(self.char_to_positions.keys())
    
    def print_mapping_summary(self):
        """Print a summary of the discovered character mappings."""
        print(f"Device Keymap Analysis:")
        print(f"  Total layers: {len(self.keymap)}")
        print(f"  LED mappings: {len(self.matrix_to_led_map)}")
        print(f"  Character mappings: {len(self.char_to_positions)}")
        
        print(f"\\nAvailable characters:")
        chars = sorted(self.get_available_characters())
        for i in range(0, len(chars), 20):
            print(f"  {''.join(chars[i:i+20])}")
    
    def validate_chord_definitions(self) -> Dict[str, List[str]]:
        """Validate FrogPad chord definitions against discovered keymap."""
        issues = {}
        
        for char, positions in FROGPAD_CHORDS.items():
            char_issues = []
            
            # Check if character exists in discovered mapping
            if char not in self.char_to_positions:
                char_issues.append(f"Character '{char}' not found in device keymap")
            
            # Check if chord positions are valid matrix positions
            for pos in positions:
                if len(pos) == 2:  # (row, col) format
                    row, col = pos
                    found = False
                    for layer_map in self.keymap.values():
                        if (row, col) in layer_map:
                            found = True
                            break
                    if not found:
                        char_issues.append(f"Position ({row}, {col}) not found in keymap")
            
            if char_issues:
                issues[char] = char_issues
        
        return issues