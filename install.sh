#!/bin/bash

# GhostForge CLI v8 Global Installer
# Forges a link to the Overseer in your PATH

echo "Forging GhostForge Global Link..."

# Path setup
TARGET_DIR="/usr/local/bin"
SOURCE_FILE="$(pwd)/ghostforge.py"
LINK_NAME="ghostforge"

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is required for the Galactic Forge."
    exit 1
fi

# Make executable
chmod +x "$SOURCE_FILE"

# Create symlink (may require sudo)
if [ -w "$TARGET_DIR" ]; then
    ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
    echo "Galactic Link established at $TARGET_DIR/$LINK_NAME"
else
    echo "Requesting sudo to establish Galactic Link at $TARGET_DIR/$LINK_NAME..."
    sudo ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
fi

echo "Done! You can now run GhostForge from anywhere by typing 'ghostforge'"
ghostforge status
