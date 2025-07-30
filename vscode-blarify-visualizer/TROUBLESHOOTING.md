# Blarify Visualizer Troubleshooting

## Extension Commands Not Found

If you're seeing "command 'blarifyVisualizer.ingestWorkspace' not found", try these steps:

### 1. Check Extension Installation

First, ensure the extension is properly installed:

1. Open VS Code Command Palette (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows/Linux)
2. Run "Developer: Show Running Extensions"
3. Look for "Blarify Code Visualizer" in the list

### 2. Check Output Channel

1. Open VS Code Output panel (View > Output)
2. Select "Blarify Visualizer" from the dropdown
3. Look for any error messages

### 3. Reload VS Code Window

1. Open Command Palette
2. Run "Developer: Reload Window"
3. Wait for VS Code to restart
4. Check if commands are now available

### 4. Manual Installation

If the extension isn't showing:

```bash
# From the extension directory
cd vscode-blarify-visualizer
npm install
npm run compile
code --install-extension blarify-visualizer-0.1.0.vsix
```

### 5. Check Developer Console

1. Open Command Palette
2. Run "Developer: Toggle Developer Tools"
3. Check the Console tab for any errors

### 6. Verify Activation

The extension should activate on startup. If not:

1. Open any file in your workspace
2. Try running the command again

### 7. Common Issues

- **Missing compiled files**: Run `npm run compile` in the extension directory
- **Node modules missing**: Run `npm install` in the extension directory
- **Extension not activated**: Check if there are any errors in the developer console

### 8. Debug Mode

To run the extension in debug mode:

1. Open the extension folder in VS Code
2. Press F5 to launch a new VS Code window with the extension loaded
3. Check the Debug Console for any errors