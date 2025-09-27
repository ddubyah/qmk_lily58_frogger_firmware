"""
Configuration management for QMK Trainer CLI.
Handles default config installation and loading.
"""

import sys
from pathlib import Path
import shutil
from typing import Dict, Any

# Handle Python version differences for TOML parsing
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError("tomli package is required for Python < 3.11")

def get_config_path() -> Path:
    """Get path to user configuration file."""
    return Path.home() / ".config" / "qmk_trainer" / "config.toml"

def get_default_config_path() -> Path:
    """Get path to default configuration file in package."""
    return Path(__file__).parent / "default_config.toml"

def install_default_config() -> None:
    """Install default configuration file if it doesn't exist."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not config_path.exists():
        default_config_path = get_default_config_path()
        if default_config_path.exists():
            shutil.copy2(default_config_path, config_path)
        else:
            # Create inline default if package file not found
            create_default_config_inline(config_path)

def create_default_config_inline(config_path: Path) -> None:
    """Create default configuration file inline."""
    default_content = '''# QMK Trainer CLI Configuration

[layer_colors]
# RGB values (0-255) for each layer
0 = [0, 255, 0]      # Layer 0: Green
1 = [255, 165, 0]    # Layer 1: Orange  
2 = [255, 0, 0]      # Layer 2: Red
3 = [0, 0, 255]      # Layer 3: Blue
4 = [255, 0, 255]    # Layer 4: Magenta

[training]
default_duration = 2000  # Default highlight duration in ms
show_progress = true     # Show training progress bar

[device]
# USB VID/PID for device detection
vendor_id = 0x7171
product_id = 0x0002

[advanced]
# Advanced settings - modify with care
led_timeout = 5000      # LED highlight timeout in ms
max_leds_per_chord = 20 # Maximum LEDs per chord highlight
oled_timeout = 3000     # OLED message timeout in ms
'''
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(default_content)

def load_config() -> Dict[str, Any]:
    """Load configuration from file, installing defaults if needed."""
    config_path = get_config_path()
    
    if not config_path.exists():
        install_default_config()
    
    try:
        with open(config_path, 'rb') as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}")
        print("Using built-in defaults...")
        return get_builtin_defaults()

def get_builtin_defaults() -> Dict[str, Any]:
    """Get built-in default configuration."""
    return {
        'layer_colors': {
            0: [0, 255, 0],      # Green
            1: [255, 165, 0],    # Orange
            2: [255, 0, 0],      # Red
            3: [0, 0, 255],      # Blue
            4: [255, 0, 255],    # Magenta
        },
        'training': {
            'default_duration': 2000,
            'show_progress': True,
        },
        'device': {
            'vendor_id': 0x7171,
            'product_id': 0x0002,
        },
        'advanced': {
            'led_timeout': 5000,
            'max_leds_per_chord': 20,
            'oled_timeout': 3000,
        },
    }

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure and values."""
    required_sections = ['layer_colors', 'training', 'device']
    
    for section in required_sections:
        if section not in config:
            print(f"Warning: Missing configuration section '{section}'")
            return False
    
    # Validate layer colors
    layer_colors = config.get('layer_colors', {})
    for layer, color in layer_colors.items():
        if not isinstance(color, list) or len(color) != 3:
            print(f"Warning: Invalid color format for layer {layer}: {color}")
            return False
        
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            print(f"Warning: Color values must be integers 0-255 for layer {layer}: {color}")
            return False
    
    # Validate training settings
    training = config.get('training', {})
    if 'default_duration' in training:
        duration = training['default_duration']
        if not isinstance(duration, int) or duration <= 0:
            print(f"Warning: Invalid default_duration: {duration}")
            return False
    
    # Validate device settings
    device = config.get('device', {})
    for key in ['vendor_id', 'product_id']:
        if key in device:
            value = device[key]
            if not isinstance(value, int) or value <= 0:
                print(f"Warning: Invalid {key}: {value}")
                return False
    
    return True

def get_layer_color(config: Dict[str, Any], layer: int) -> tuple[int, int, int]:
    """Get RGB color tuple for a specific layer."""
    layer_colors = config.get('layer_colors', {})
    
    # Try to get color for specific layer
    if layer in layer_colors:
        color = layer_colors[layer]
        return tuple(color)
    
    # Try string key (TOML may use string keys)
    if str(layer) in layer_colors:
        color = layer_colors[str(layer)]
        return tuple(color)
    
    # Default colors for common layers
    default_colors = {
        0: (0, 255, 0),      # Green
        1: (255, 165, 0),    # Orange
        2: (255, 0, 0),      # Red
        3: (0, 0, 255),      # Blue
        4: (255, 0, 255),    # Magenta
    }
    
    return default_colors.get(layer, (255, 255, 255))  # White default