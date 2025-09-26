# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a clean, standalone QMK firmware project for the Lily58 split keyboard with a custom "frogger" variant. The repository contains ONLY the custom keyboard definition and build infrastructure, with a clean git history separate from the main QMK firmware repository.

## Key Commands

### Setup Commands
- **Initial setup**: `./setup.sh` - Creates symlink from QMK installation to this project
- **Clean setup**: `./clean.sh` - Removes symlinks and build artifacts

### Build Commands
- **Build default keymap**: `./build.sh` (defaults to frogger_rgb_via)
- **Build specific keymap**: `./build.sh [keymap_name]`
- **Build frogger_rgb_via**: `./build.sh frogger_rgb_via` (VIA-compatible)
- **Build default**: `./build.sh default` (basic keymap)

### QMK Commands (if needed)
- **Manual compile**: `qmk compile -kb lily58/frogger -km frogger_rgb_via -e CONVERT_TO=rp2040_ce`
- **List keymaps**: `ls lily58_pro/keymaps/`

## Architecture and Structure

### Project Structure
```
qmk_lily_frogger_firmware/
├── lily58_pro/              # Custom keyboard definition (YOUR CODE)
│   ├── keymaps/
│   │   ├── frogger_rgb_via/ # VIA-compatible 5-layer keymap
│   │   └── default/         # Standard keymap
│   ├── keyboard.json        # Hardware configuration
│   ├── pro.c               # Board initialization
│   ├── config.h            # Board config
│   └── ...
├── .build/                  # Compiled firmware output
├── setup.sh                 # Setup script
├── build.sh                 # Build script
├── clean.sh                 # Cleanup script
├── CLAUDE.md               # This file
└── README.md               # Documentation
```

### Symlink Architecture
- **QMK Home**: Fresh QMK installation at `~/qmk_firmware/`
- **Symlink**: `~/qmk_firmware/keyboards/lily58/frogger` → `./lily58_pro/`
- **Build Output**: Compiled `.uf2` files copied to `.build/`

### Custom Keyboard Details
- **Location**: `lily58_pro/` (the symlink target)
- **QMK Path**: `lily58/frogger` (the symlink source in QMK)
- **Compile Target**: `lily58/frogger`
- **Controller**: RP2040 with UF2 output
- **Features**: RGB Matrix (74 LEDs), VIA support, OLED, Encoder

## Build Process

### How It Works
1. **Setup**: `./setup.sh` creates symlink from QMK to your project
2. **Build**: `./build.sh` runs QMK compile via symlink
3. **Output**: UF2 files copied to `.build/` for easy access
4. **Flash**: Drag & drop UF2 to RP2040 in bootloader mode

### Dependencies
- QMK CLI installed (`brew install qmk/qmk/qmk`)
- Fresh QMK firmware at `~/qmk_firmware/` with submodules initialized
- RP2040-compatible Lily58 hardware

## Important Implementation Notes

### File Locations
- **ONLY edit files in**: `lily58_pro/` directory
- **Build output**: `.build/*.uf2` files
- **Do NOT edit**: QMK base files in `~/qmk_firmware/`

### Keymap Development
- **Primary keymap**: `frogger_rgb_via` (VIA-compatible, RGB matrix, 5 layers)
- **Testing keymap**: `default` (basic functionality)
- **Add new keymaps**: Create folder in `lily58_pro/keymaps/your_keymap/`

### Hardware Configuration
- **RGB Matrix**: 74 LEDs (37 per side) defined in `keyboard.json`
- **VIA Support**: Enabled in `frogger_rgb_via` keymap
- **RP2040 Target**: All builds use `CONVERT_TO=rp2040_ce`

### Memory Considerations
- **VIA builds**: OLED disabled to conserve memory
- **RGB Matrix**: Max brightness 120 for power management
- **Layer Count**: 5 layers for VIA compatibility

## Build Troubleshooting

### Common Issues
1. **Symlink missing**: Run `./setup.sh`
2. **QMK not found**: Check `qmk config user.qmk_home`
3. **Submodules missing**: QMK needs submodules for RP2040 support
4. **Build fails**: Ensure QMK installation is complete with all dependencies

### Build Commands to Remember
- Use the project scripts: `./build.sh`, not direct QMK commands
- All builds target RP2040: automatic UF2 generation
- Output always in `.build/` directory

## Development Workflow

### Making Changes
1. Edit files in `lily58_pro/keymaps/[keymap]/`
2. Run `./build.sh [keymap]` to test
3. Flash `.build/*.uf2` to hardware
4. Commit changes to this repository (not QMK)

### Adding Features
- **RGB**: Modify `keyboard.json` RGB matrix configuration
- **VIA**: Ensure `VIA_ENABLE = yes` in keymap's `rules.mk`
- **Layers**: Update `DYNAMIC_KEYMAP_LAYER_COUNT` for VIA compatibility

## Project Philosophy

This repository maintains ONLY your custom keyboard code with:
- ✅ Clean git history (no QMK base code)
- ✅ Focused scope (just your keyboard variant)
- ✅ Easy setup (automated scripts)
- ✅ Portable builds (works on any machine with QMK CLI)
- ✅ Separation of concerns (your code vs QMK base)

When working with this project, focus on the `lily58_pro/` directory and use the provided build scripts for a clean development experience.