"""
Tests for chord mapping system.
"""

import pytest
from qmk_trainer.chord_mapper import ChordMapper, extract_base_keycode, FROGPAD_CHORDS, KC_A, KC_SPACE


def test_extract_base_keycode():
    """Test keycode extraction from modified keycodes."""
    # Regular keycode
    assert extract_base_keycode(KC_A) == KC_A
    
    # Layer tap keycode (example)
    layer_tap_a = 0x4000 | KC_A  # QK_LAYER_TAP + KC_A
    assert extract_base_keycode(layer_tap_a) == KC_A
    
    # Mod tap keycode (example)  
    mod_tap_a = 0x6000 | KC_A  # QK_MOD_TAP + KC_A
    assert extract_base_keycode(mod_tap_a) == KC_A


def test_frogpad_chord_definitions():
    """Test that FrogPad chord definitions are properly formatted."""
    for char, positions in FROGPAD_CHORDS.items():
        assert isinstance(char, str)
        assert len(char) == 1  # Single character
        assert isinstance(positions, list)
        assert len(positions) > 0  # At least one position
        
        for pos in positions:
            assert isinstance(pos, tuple)
            assert len(pos) == 2  # (row, col) format
            assert isinstance(pos[0], int) and pos[0] >= 0  # Valid row
            assert isinstance(pos[1], int) and pos[1] >= 0  # Valid col


def test_chord_mapper_initialization():
    """Test ChordMapper initialization."""
    mapper = ChordMapper()
    
    # Check initial state
    assert mapper.device is None
    assert len(mapper.matrix_to_led_map) == 0
    assert len(mapper.keymap) == 0
    assert len(mapper.char_to_positions) == 0
    assert len(mapper.keycode_to_positions) == 0


def test_chord_mapper_without_device():
    """Test ChordMapper methods when no device is connected."""
    mapper = ChordMapper()
    
    # Should raise error when trying to load from device
    with pytest.raises(RuntimeError):
        mapper.load_from_device()


def test_build_character_mapping():
    """Test character mapping building with mock keymap."""
    mapper = ChordMapper()
    
    # Mock keymap data
    mapper.keymap = {
        0: {
            (2, 1): KC_A,     # 'a' key at row 2, col 1
            (4, 3): KC_SPACE, # space key at row 4, col 3
        }
    }
    
    mapper.matrix_to_led_map = {
        (2, 1): 10,  # LED index 10
        (4, 3): 25,  # LED index 25
    }
    
    # Build mappings
    mapper._build_keycode_mapping()
    mapper._build_character_mapping()
    
    # Check that 'a' and 'A' are mapped
    assert 'a' in mapper.char_to_positions
    assert 'A' in mapper.char_to_positions
    assert ' ' in mapper.char_to_positions  # space
    
    # Check positions
    assert mapper.char_to_positions['a'] == [(0, 2, 1)]
    assert mapper.char_to_positions[' '] == [(0, 4, 3)]


def test_get_available_characters():
    """Test getting available characters."""
    mapper = ChordMapper()
    mapper.char_to_positions = {'a': [(0, 2, 1)], 'b': [(0, 3, 1)], ' ': [(0, 4, 3)]}
    
    chars = mapper.get_available_characters()
    assert chars == {'a', 'b', ' '}


def test_char_to_leds_with_layers():
    """Test character to LED conversion with layer colors."""
    mapper = ChordMapper()
    mapper.char_to_positions = {'a': [(0, 2, 1), (1, 2, 1)]}  # 'a' on layers 0 and 1
    mapper.matrix_to_led_map = {(2, 1): 10}  # LED index 10
    
    layer_colors = {0: (0, 255, 0), 1: (255, 0, 0)}  # Green and red
    
    led_info = mapper.char_to_leds_with_layers('a', layer_colors)
    
    # Should return 2 entries (one for each layer)
    assert len(led_info) == 2
    assert (10, (0, 255, 0)) in led_info   # Layer 0 - green
    assert (10, (255, 0, 0)) in led_info   # Layer 1 - red