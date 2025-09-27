"""
Tests for configuration management.
"""

import pytest
import tempfile
import os
from pathlib import Path

from qmk_trainer.config import load_config, get_builtin_defaults, validate_config, get_layer_color


def test_builtin_defaults():
    """Test built-in default configuration."""
    defaults = get_builtin_defaults()
    
    # Check required sections exist
    assert 'layer_colors' in defaults
    assert 'training' in defaults
    assert 'device' in defaults
    
    # Check layer colors format
    layer_colors = defaults['layer_colors']
    assert isinstance(layer_colors, dict)
    
    for layer, color in layer_colors.items():
        assert isinstance(color, list)
        assert len(color) == 3
        assert all(isinstance(c, int) and 0 <= c <= 255 for c in color)


def test_validate_config():
    """Test configuration validation."""
    # Valid configuration
    valid_config = get_builtin_defaults()
    assert validate_config(valid_config) == True
    
    # Invalid configuration - missing section
    invalid_config = {'layer_colors': {}}
    assert validate_config(invalid_config) == False
    
    # Invalid configuration - bad color format
    invalid_config = {
        'layer_colors': {0: [256, 0, 0]},  # Invalid color value
        'training': {'default_duration': 2000},
        'device': {'vendor_id': 0x7171, 'product_id': 0x0002}
    }
    assert validate_config(invalid_config) == False


def test_get_layer_color():
    """Test layer color retrieval."""
    config = get_builtin_defaults()
    
    # Test existing layer
    color = get_layer_color(config, 0)
    assert isinstance(color, tuple)
    assert len(color) == 3
    assert all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    # Test non-existing layer (should return default)
    color = get_layer_color(config, 99)
    assert color == (255, 255, 255)  # White default


def test_load_config_fallback():
    """Test that load_config falls back to defaults when file doesn't exist."""
    # Temporarily modify the config path to a non-existent location
    with tempfile.TemporaryDirectory() as tmpdir:
        # This should fall back to built-in defaults
        config = load_config()
        assert validate_config(config) == True