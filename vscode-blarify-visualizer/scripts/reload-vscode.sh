#!/bin/bash
# Script to simulate VS Code reload by closing and reopening

# Kill VS Code Insiders
echo "Closing VS Code Insiders..."
osascript -e 'quit app "Visual Studio Code - Insiders"'

# Wait a moment
sleep 2

# Reopen VS Code Insiders
echo "Reopening VS Code Insiders..."
code-insiders .

echo "VS Code Insiders reloaded!"