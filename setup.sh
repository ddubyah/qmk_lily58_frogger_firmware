#!/bin/bash
# Setup script for lily58 frogger firmware
# Creates symlink from QMK installation to our custom keyboard

set -e

# Detect QMK home from config
QMK_HOME=$(qmk config user.qmk_home | cut -d'=' -f2)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Validate QMK home exists
if [ ! -d "$QMK_HOME" ]; then
    echo "❌ QMK home directory not found: $QMK_HOME"
    echo "Please run: qmk setup --home ~/qmk_firmware"
    exit 1
fi

# Create lily58 directory structure if needed
mkdir -p "$QMK_HOME/keyboards/lily58"

# Remove existing symlink or directory
if [ -L "$QMK_HOME/keyboards/lily58/frogger" ]; then
    rm "$QMK_HOME/keyboards/lily58/frogger"
    echo "🔗 Removed existing symlink"
elif [ -d "$QMK_HOME/keyboards/lily58/frogger" ]; then
    rm -rf "$QMK_HOME/keyboards/lily58/frogger"
    echo "🗑️  Removed existing frogger directory"
fi

# Create symlink to our custom keyboard
ln -sfn "$PROJECT_DIR/lily58_pro" "$QMK_HOME/keyboards/lily58/frogger"

echo "✓ Setup complete!"
echo "  QMK Home: $QMK_HOME"
echo "  Symlink: $QMK_HOME/keyboards/lily58/frogger → $PROJECT_DIR/lily58_pro"
echo ""
echo "Now you can build with: ./build.sh [keymap]"