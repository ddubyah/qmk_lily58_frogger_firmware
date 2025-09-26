# Lily58 Frogger Firmware

A clean, standalone QMK firmware project for the Lily58 split keyboard with custom "frogger" variant featuring RGB matrix support and VIA compatibility.

## Features

- **Custom Lily58 Pro Variant**: Enhanced lily58 configuration with full RGB matrix support
- **5-Layer Layout**: QWERTY base layer plus 4 additional layers for functions, navigation, RGB control, and utilities
- **RP2040 Support**: Optimized for RP2040-based controllers with UF2 drag-and-drop flashing
- **VIA Compatible**: frogger_rgb_via keymap supports real-time key remapping via VIA software
- **RGB Matrix**: 74 RGB LEDs with customizable animations and effects
- **OLED Support**: Available in keymaps (when enabled)
- **Encoder Support**: Rotary encoder functionality built-in

## Available Keymaps

- **`frogger_rgb_via`**: VIA-compatible 5-layer keymap with RGB matrix support (default)
- **`default`**: Standard QMK keymap for basic functionality

## Quick Start

### Prerequisites
- QMK CLI installed (`brew install qmk/qmk/qmk`)
- RP2040-compatible Lily58 keyboard

### Setup & Build

1. **Clone and setup:**
   ```bash
   git clone https://github.com/ddubyah/qmk_lily58_frogger_firmware.git
   cd qmk_lily58_frogger_firmware
   ./setup.sh
   ```

2. **Build firmware:**
   ```bash
   ./build.sh                     # Builds frogger_rgb_via (default)
   ./build.sh frogger_rgb_via     # VIA-compatible version
   ./build.sh default             # Standard keymap
   ```

3. **Flash firmware:**
   - Put keyboard in bootloader mode (double-tap reset or bridge boot pins)
   - Drag & drop the `.uf2` file from `.build/` to the RPI-RP2 drive that appears
   - Firmware will install automatically

## Project Structure

```
qmk_lily_frogger_firmware/
├── lily58_pro/              # Custom keyboard definition
│   ├── keymaps/
│   │   ├── frogger_rgb_via/ # VIA-compatible keymap
│   │   └── default/         # Standard keymap
│   ├── keyboard.json        # Hardware configuration
│   ├── pro.c               # Board-specific code
│   └── ...
├── scripts/                 # Build scripts (future)
├── .build/                  # Compiled firmware files
├── setup.sh                 # Setup symlinks script
├── build.sh                 # Build firmware script
├── clean.sh                 # Cleanup script
└── README.md               # This file
```

## Hardware Configuration

### Supported Controllers
- RP2040-based boards (Raspberry Pi Pico, compatible controllers)
- Pro Micro form factor with RP2040

### Key Features
- **Matrix**: 5x6 split (58 keys total)
- **RGB Matrix**: 74 individually addressable LEDs (37 per side)
- **Encoder**: Single rotary encoder support
- **OLED**: 128x32 display support (configurable)
- **Communication**: Serial communication between halves

### Pin Configuration
- **Matrix Rows**: C6, D7, E6, B4, B5
- **Matrix Cols**: F6, F7, B1, B3, B2, B6
- **RGB Data**: D3 (WS2812 compatible)
- **Serial**: D2 (split communication)
- **Encoder**: F5 (A), F4 (B)

## Build System

The project uses a clean separation between your custom firmware and the QMK source code:

- **QMK Installation**: Fresh QMK firmware installed at `~/qmk_firmware/`
- **Symlink**: `~/qmk_firmware/keyboards/lily58/frogger` → your project folder
- **Build Output**: Compiled `.uf2` files automatically copied to `.build/`

### Scripts

- **`./setup.sh`**: Creates symlink from QMK to your project directory
- **`./build.sh [keymap]`**: Compiles firmware for specified keymap (defaults to frogger_rgb_via)
- **`./clean.sh`**: Removes symlinks and build artifacts

## Layer Layout (frogger_rgb_via)

### Layer 0 (Base - QWERTY)
Standard QWERTY layout with modifier keys optimized for split keyboard use.

### Layer 1 (Functions)
Function keys (F1-F12) and special characters (!@#$%^&*()).

### Layer 2 (Navigation)
Arrow keys, home/end, page up/down, and number row access.

### Layer 3 (RGB Control)
RGB matrix controls:
- Toggle, mode cycling
- Hue, saturation, value adjustment
- Animation speed control

### Layer 4 (Utilities)
Additional utility functions and reserved keys.

## VIA Support

The `frogger_rgb_via` keymap is fully compatible with [VIA](https://www.caniusevia.com/):

1. Flash the `frogger_rgb_via` firmware
2. Open VIA software
3. Load the keyboard (should auto-detect)
4. Customize keys in real-time without reflashing

**Note**: VIA builds disable OLED support to conserve memory for the dynamic keymap functionality.

## RGB Matrix

74 individually addressable RGB LEDs providing:
- Per-key backlighting
- Underglow effects
- Multiple animation modes
- VIA-compatible real-time control
- Max brightness: 120 (to manage power consumption)

## Development

### Adding New Keymaps
1. Create new folder: `lily58_pro/keymaps/your_keymap/`
2. Add `keymap.c`, `rules.mk`, and optional `config.h`
3. Build with: `./build.sh your_keymap`

### Customizing RGB
Edit the RGB matrix configuration in `keyboard.json` or keymap-specific `config.h`.

### Hardware Modifications
Update pin assignments and features in `keyboard.json`.

## Troubleshooting

### Build Issues
- Ensure QMK CLI is installed: `qmk --version`
- Run setup if symlink missing: `./setup.sh`
- Check QMK installation: `qmk config user.qmk_home`

### Flashing Issues
- Verify RP2040 bootloader mode (RPI-RP2 drive appears)
- Try different USB cable/port
- Check file permissions on .uf2 file

### VIA Issues
- Use `frogger_rgb_via` keymap specifically
- Restart VIA if keyboard not detected
- Check VIA compatibility version

## License

This project follows QMK's GPL-2.0 license terms.

## Contributing

1. Fork the repository
2. Create feature branch
3. Test changes thoroughly
4. Submit pull request

For issues or questions, please open a GitHub issue.

---

**Built for RP2040 • Optimized for VIA • RGB Matrix Ready**
