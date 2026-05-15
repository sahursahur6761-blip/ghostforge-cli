#!/bin/bash

# GhostForge Singularity v10 Global Installer
# Initializing the Singularity Engine

echo "Connecting to the Singularity..."

# Path setup
TARGET_DIR="/usr/local/bin"
SOURCE_FILE="$(pwd)/ghostforge.py"
LINK_NAME="ghostforge"

if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is required for the Singularity Engine."
    exit 1
fi

chmod +x "$SOURCE_FILE"

if [ -w "$TARGET_DIR" ]; then
    ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
else
    echo "Elevated privileges required for global installation..."
    sudo ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
fi

# Basic Bash Completion
COMP_FILE="/etc/bash_completion.d/ghostforge"
if [ -d "/etc/bash_completion.d" ] && [ -w "/etc/bash_completion.d" ]; then
    echo "Installing bash completion..."
    echo 'complete -W "status mission boss fabricate autoforge clear exit" ghostforge' > "$COMP_FILE"
fi

echo "--- SINGULARITY INITIALIZED ---"
echo "GhostForge v10 is now globally active."
echo "Type 'ghostforge' to begin."
echo "-------------------------------"
ghostforge s
