#!/bin/bash
# Clean script for lily58 frogger firmware
# Removes symlinks and build artifacts

set -e

QMK_HOME=$(qmk config user.qmk_home | cut -d'=' -f2)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🧹 Cleaning up..."

# Remove symlink from QMK
if [ -L "$QMK_HOME/keyboards/lily58/frogger" ]; then
    rm "$QMK_HOME/keyboards/lily58/frogger"
    echo "✓ Removed symlink: $QMK_HOME/keyboards/lily58/frogger"
else
    echo "ℹ️  No symlink found to remove"
fi

# Clean local build artifacts
if [ -d "$PROJECT_DIR/.build" ]; then
    rm -rf "$PROJECT_DIR/.build"
    echo "✓ Removed local build artifacts"
fi

# Clean QMK build artifacts
if [ -d "$QMK_HOME/.build" ]; then
    rm -rf "$QMK_HOME/.build"
    echo "✓ Removed QMK build artifacts"
fi

echo "✓ Cleanup complete!"