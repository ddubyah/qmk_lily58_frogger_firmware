#!/bin/bash
# Build script for lily58 frogger firmware
# Compiles firmware and copies UF2 files to local .build folder

set -e

KEYMAP=${1:-frogger_rgb_via}
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
QMK_HOME=$(qmk config user.qmk_home | cut -d'=' -f2)

echo "🔨 Building lily58 frogger firmware..."
echo "  Keymap: $KEYMAP"
echo "  Target: RP2040 (UF2)"

# Ensure setup has been run
if [ ! -L "$QMK_HOME/keyboards/lily58/frogger" ]; then
    echo "⚠️  Symlink not found. Running setup first..."
    ./setup.sh
fi

# Validate keymap exists
if [ ! -d "$PROJECT_DIR/lily58_pro/keymaps/$KEYMAP" ]; then
    echo "❌ Keymap '$KEYMAP' not found in lily58_pro/keymaps/"
    echo "Available keymaps:"
    ls -1 "$PROJECT_DIR/lily58_pro/keymaps/" | sed 's/^/  - /'
    exit 1
fi

# Build firmware for RP2040
echo "🔧 Compiling firmware..."
qmk compile -kb lily58/frogger -km "$KEYMAP" -e CONVERT_TO=rp2040_ce

if [ $? -eq 0 ]; then
    # Copy UF2 files to local build folder
    echo "📦 Copying firmware to .build/"
    mkdir -p "$PROJECT_DIR/.build"

    # Find and copy the UF2 file
    UF2_FILE=$(find "$QMK_HOME" -name "*.uf2" -newer "$PROJECT_DIR/.build" 2>/dev/null | head -1)
    if [ -n "$UF2_FILE" ]; then
        cp "$UF2_FILE" "$PROJECT_DIR/.build/"
        echo "✓ Build complete!"
        echo "  Firmware: $(basename "$UF2_FILE")"
        echo "  Location: $PROJECT_DIR/.build/$(basename "$UF2_FILE")"
        echo ""
        echo "🔌 To flash:"
        echo "  1. Put keyboard in bootloader mode"
        echo "  2. Drag & drop UF2 file to RPI-RP2 drive"
    else
        echo "⚠️  UF2 file not found in QMK build directory"
        echo "Check QMK build output above for errors"
    fi
else
    echo "❌ Build failed. Check QMK output above for errors."
    exit 1
fi