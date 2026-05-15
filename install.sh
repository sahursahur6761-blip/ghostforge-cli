#!/bin/bash

# GhostForge Nexus v9 Global Installer
# Connect your terminal to the Singularity

echo "Initializing Nexus Bridge..."

# Path setup
TARGET_DIR="/usr/local/bin"
SOURCE_FILE="$(pwd)/ghostforge.py"
LINK_NAME="ghostforge"

if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is required for the Nexus."
    exit 1
fi

chmod +x "$SOURCE_FILE"

if [ -w "$TARGET_DIR" ]; then
    ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
else
    echo "Elevated privileges required for global installation..."
    sudo ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
fi

echo "--- INSTALLATION COMPLETE ---"
echo "GhostForge Nexus v9 is now globally available."
echo "Type 'ghostforge' to enter the Forge."
echo "------------------------------"
ghostforge s
