#!/bin/bash

# GhostForge Galactic v11 Global Installer
# Connect to the Neural Link

echo "Initializing Neural Bridge..."

# Path setup
TARGET_DIR="/usr/local/bin"
SOURCE_FILE="$(pwd)/ghostforge.py"
LINK_NAME="ghostforge"

if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is required."
    exit 1
fi

chmod +x "$SOURCE_FILE"

if [ -w "$TARGET_DIR" ]; then
    ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
else
    echo "Requesting sudo for global link..."
    sudo ln -sf "$SOURCE_FILE" "$TARGET_DIR/$LINK_NAME"
fi

# ZSH Completion (Standard on Mac)
ZSH_COMP_DIR="${HOME}/.zsh/completion"
mkdir -p "$ZSH_COMP_DIR"
cat <<EOF > "${ZSH_COMP_DIR}/_ghostforge"
#compdef ghostforge
_arguments '1: :((status mission link clear exit))'
EOF

if [[ "$SHELL" == *"zsh"* ]]; then
    if ! grep -q "fpath=(~/.zsh/completion \$fpath)" ~/.zshrc; then
        echo "fpath=(~/.zsh/completion \$fpath)" >> ~/.zshrc
        echo "autoload -U compinit && compinit" >> ~/.zshrc
        echo "Added Zsh completion to ~/.zshrc"
    fi
fi

echo "--- INSTALL COMPLETE ---"
echo "GhostForge Galactic Nexus active."
echo "Type 'ghostforge' to begin."
ghostforge s
