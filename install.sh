#!/bin/bash

# GhostForge CLI Installer
# Just makes it executable and checks for python

echo "Forging GhostForge..."

if ! command -v python3 &> /dev/null
then
    echo "Error: python3 could not be found. Please install Python 3."
    exit 1
fi

chmod +x ghostforge.py

echo "Done! You can now run GhostForge using './ghostforge.py' or 'python3 ghostforge.py'"
./ghostforge.py vault
