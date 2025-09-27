# QMK Trainer CLI

A one-handed keyboard training CLI with LED highlighting and OLED feedback for VIA-compatible QMK keyboards.

## Features

- **Automatic Keymap Reading**: Reads keymap directly from keyboard via VIA protocol (no manual export needed)
- **LED Highlighting**: Highlights keys with layer-specific colors during training
- **OLED Feedback**: Shows character prompts on keyboard OLED display
- **Multiple Training Modes**: Sequential training, drill mode, and individual character testing
- **Layer-Aware**: Supports multi-layer keymaps with different colors per layer
- **VIA Compatible**: Works with any VIA-enabled QMK keyboard

## Installation

### Prerequisites

- Python 3.8 or higher
- QMK keyboard with VIA support and custom trainer firmware
- uv package manager (recommended) or pip

### Install with uv

```bash
# Install from source (development)
git clone <repository>
cd qmk_trainer
uv sync
uv tool install --editable .
```

### Install with pip

```bash
pip install qmk_trainer  # When published to PyPI
# or from source:
git clone <repository>
cd qmk_trainer
pip install -e .
```

## Firmware Setup

The trainer requires custom firmware with VIA trainer commands. Flash the provided firmware:

1. Build firmware: `./build.sh frogger_rgb_via`
2. Put keyboard in bootloader mode
3. Flash: drag `.build/lily58_frogger_frogger_rgb_via_rp2040_ce.uf2` to RPI-RP2 drive

## Quick Start

### 1. Test Connection

```bash
qmk_trainer info
```

Shows device information and capabilities.

### 2. Test LED Highlighting

```bash
# Test specific character
qmk_trainer test a

# Test LED indexes directly
qmk_trainer highlight --keys 0,1,2 --duration 2000 --color 255,0,0
```

### 3. Training Mode

```bash
# Train a word
qmk_trainer train "hello"

# Train with custom duration and validation
qmk_trainer train "hello world" --duration 1500 --validate
```

### 4. Drill Mode

```bash
# Interactive practice with default words
qmk_trainer drill

# Custom word list
qmk_trainer drill --words "cat,dog,bird,fish"
```

## Commands

### `qmk_trainer train <text>`

Sequential training mode that highlights keys for each character in sequence.

**Options:**
- `--duration, -d`: LED highlight duration in milliseconds (default: 2000)
- `--validate`: Validate setup before starting training

**Example:**
```bash
qmk_trainer train "hello world" --duration 1500 --validate
```

### `qmk_trainer drill`

Interactive practice mode with word prompts.

**Options:**
- `--words, -w`: Comma-separated word list
- `--duration, -d`: LED highlight duration (default: 1500)

**Example:**
```bash
qmk_trainer drill --words "hello,world,qmk,keyboard" --duration 2000
```

### `qmk_trainer test <character>`

Test LED highlighting for a specific character.

**Example:**
```bash
qmk_trainer test a --duration 3000
```

### `qmk_trainer highlight`

Debug tool for testing specific LED positions.

**Options:**
- `--keys, -k`: Comma-separated LED indexes
- `--duration, -d`: Duration in milliseconds (default: 2000)
- `--color, -c`: RGB color as "r,g,b" (default: "255,0,0")

**Example:**
```bash
qmk_trainer highlight --keys 0,1,2,10,11 --color 0,255,0 --duration 3000
```

### `qmk_trainer config`

Configuration management.

**Options:**
- `--show, -s`: Show current configuration
- `--edit, -e`: Edit configuration file

### `qmk_trainer info`

Show device information and connection status.

## Configuration

Configuration is stored in `~/.config/qmk_trainer/config.toml` and created automatically on first run.

### Layer Colors

Customize colors for each layer:

```toml
[layer_colors]
0 = [0, 255, 0]      # Layer 0: Green
1 = [255, 165, 0]    # Layer 1: Orange  
2 = [255, 0, 0]      # Layer 2: Red
3 = [0, 0, 255]      # Layer 3: Blue
4 = [255, 0, 255]    # Layer 4: Magenta
```

### Training Settings

```toml
[training]
default_duration = 2000  # Default LED highlight duration in ms
show_progress = true     # Show training progress bar
prompt_delay = 500       # Delay between character prompts in ms
```

### Device Settings

```toml
[device]
vendor_id = 0x7171      # USB Vendor ID
product_id = 0x0002     # USB Product ID
```

## How It Works

### Keymap Reading

The trainer automatically reads your keyboard's keymap using VIA's dynamic keymap protocol. No manual keymap export is needed.

1. Connects to VIA-compatible device
2. Scans all layers using `DYNAMIC_KEYMAP_GET_KEYCODE` commands
3. Builds character-to-position mapping
4. Retrieves LED matrix mapping from firmware

### LED Highlighting

Characters are highlighted using layer-specific colors:

1. Character → matrix positions (with layers)
2. Matrix positions → LED indexes  
3. LED indexes + layer colors → highlight commands
4. Firmware displays highlights with timer-based duration

### Training Flow

1. **Setup**: Load keymap and LED mappings from device
2. **Begin**: Enter trainer mode (saves RGB state, sets backdrop)
3. **Train**: For each character:
   - Show OLED prompt ("Press: a")
   - Highlight corresponding LEDs with layer colors
   - Wait for duration + prompt delay
4. **End**: Restore original RGB settings

## Troubleshooting

### Device Not Found

- Check USB connection
- Ensure keyboard has VIA-enabled firmware with trainer extensions
- Verify VID:PID in config matches your device

### No LED Highlighting

- Confirm firmware includes trainer command handlers
- Test with `qmk_trainer test a`
- Check if RGB matrix is enabled

### Character Not Found

- Run `qmk_trainer info` to see available characters
- Use `qmk_trainer train --validate` to check setup
- Character may not be mapped on any layer

### Permission Issues

- On Linux, you may need udev rules for HID access
- Try running with `sudo` (not recommended for regular use)

## Development

### Running Tests

```bash
# With uv
uv run pytest tests/ -v

# With pip
pytest tests/ -v --cov=qmk_trainer
```

### Code Quality

```bash
# Linting
uv run ruff check --fix .

# Type checking
uv run mypy . --ignore-missing-imports
```

## Architecture

- **CLI Interface**: Typer-based command line interface
- **HID Communication**: VIA protocol over USB HID for device communication
- **Keymap Analysis**: Automatic keymap reading using VIA dynamic keymap commands
- **Chord Mapping**: Character-to-matrix position mapping with layer support
- **Training Engine**: Session management with progress tracking and LED control
- **Configuration**: TOML-based configuration with user customization

## License

GPL-2.0 or later (compatible with QMK)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request