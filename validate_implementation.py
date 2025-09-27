#!/usr/bin/env python3
"""
Validation script for QMK Trainer CLI implementation.
Checks basic functionality without requiring hardware connection.
"""

import sys
import importlib
from pathlib import Path

def validate_imports():
    """Test that all modules can be imported without errors."""
    print("Testing module imports...")
    
    try:
        # Add qmk_trainer to path
        sys.path.insert(0, str(Path("qmk_trainer").absolute()))
        
        # Test imports
        import qmk_trainer
        from qmk_trainer import config, chord_mapper, hid_comm, trainer
        from qmk_trainer.cli import app
        
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def validate_config():
    """Test configuration system."""
    print("Testing configuration system...")
    
    try:
        from qmk_trainer.config import get_builtin_defaults, validate_config, get_layer_color
        
        # Test defaults
        defaults = get_builtin_defaults()
        assert 'layer_colors' in defaults
        assert 'training' in defaults
        assert 'device' in defaults
        
        # Test validation
        assert validate_config(defaults) == True
        
        # Test layer colors
        color = get_layer_color(defaults, 0)
        assert isinstance(color, tuple)
        assert len(color) == 3
        
        print("✓ Configuration system working")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def validate_chord_mapper():
    """Test chord mapping system."""
    print("Testing chord mapping system...")
    
    try:
        from qmk_trainer.chord_mapper import ChordMapper, extract_base_keycode, FROGPAD_CHORDS, KC_A
        
        # Test keycode extraction
        assert extract_base_keycode(KC_A) == KC_A
        
        # Test chord definitions format
        for char, positions in FROGPAD_CHORDS.items():
            assert isinstance(char, str)
            assert len(char) == 1
            assert isinstance(positions, list)
            assert len(positions) > 0
        
        # Test mapper initialization
        mapper = ChordMapper()
        assert mapper.device is None
        assert len(mapper.char_to_positions) == 0
        
        print("✓ Chord mapping system working")
        return True
    except Exception as e:
        print(f"✗ Chord mapper error: {e}")
        return False

def validate_hid_comm():
    """Test HID communication module."""
    print("Testing HID communication module...")
    
    try:
        from qmk_trainer.hid_comm import VIADevice, CMD_GET_LED_MAP, CMD_HIGHLIGHT_LEDS
        
        # Test constants
        assert isinstance(CMD_GET_LED_MAP, int)
        assert isinstance(CMD_HIGHLIGHT_LEDS, int)
        
        # Test VIADevice class
        via = VIADevice()
        assert via.device is None
        assert len(via.matrix_to_led_map) == 0
        assert len(via.keymap) == 0
        
        print("✓ HID communication module working")
        return True
    except Exception as e:
        print(f"✗ HID communication error: {e}")
        return False

def validate_cli():
    """Test CLI interface."""
    print("Testing CLI interface...")
    
    try:
        from qmk_trainer.cli import app
        import typer
        
        # Test that app is a Typer instance
        assert isinstance(app, typer.Typer)
        
        # Test that commands are registered
        commands = [cmd.name for cmd in app.registered_commands.values()]
        expected_commands = ['train', 'drill', 'test', 'highlight', 'config', 'info']
        
        for cmd in expected_commands:
            assert cmd in commands, f"Command '{cmd}' not found"
        
        print("✓ CLI interface working")
        return True
    except Exception as e:
        print(f"✗ CLI error: {e}")
        return False

def validate_project_structure():
    """Validate project structure and files."""
    print("Testing project structure...")
    
    try:
        required_files = [
            "qmk_trainer/__init__.py",
            "qmk_trainer/cli.py", 
            "qmk_trainer/config.py",
            "qmk_trainer/hid_comm.py",
            "qmk_trainer/chord_mapper.py",
            "qmk_trainer/trainer.py",
            "qmk_trainer/default_config.toml",
            "qmk_trainer/pyproject.toml",
            "qmk_trainer/README.md",
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            assert path.exists(), f"Missing file: {file_path}"
            assert path.stat().st_size > 0, f"Empty file: {file_path}"
        
        print("✓ Project structure complete")
        return True
    except Exception as e:
        print(f"✗ Project structure error: {e}")
        return False

def validate_firmware():
    """Validate firmware build."""
    print("Testing firmware build...")
    
    try:
        firmware_path = Path(".build/lily58_frogger_frogger_rgb_via_rp2040_ce.uf2")
        
        if firmware_path.exists():
            size = firmware_path.stat().st_size
            print(f"✓ Firmware built successfully ({size} bytes)")
            return True
        else:
            print("⚠ Firmware not built (run ./build.sh frogger_rgb_via)")
            return False
    except Exception as e:
        print(f"✗ Firmware validation error: {e}")
        return False

def main():
    """Run all validation tests."""
    print("QMK Trainer CLI Implementation Validation")
    print("=" * 50)
    
    tests = [
        validate_project_structure,
        validate_imports,
        validate_config, 
        validate_chord_mapper,
        validate_hid_comm,
        validate_cli,
        validate_firmware,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
        print()
    
    print("=" * 50)
    print(f"Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed! Implementation complete.")
        return True
    else:
        print("❌ Some validation tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)