# Blarify Visualizer Quick Start

## Prerequisites
1. Ensure Docker Desktop is running
2. Ensure Python 3 is installed and in PATH
3. Open a folder/workspace in VS Code

## Step 1: Configure Settings (Optional)
Azure OpenAI is optional - the extension works without it but won't have LLM summaries.

1. Press `Cmd+,` to open settings
2. Search for "Blarify Visualizer"
3. Add your Azure OpenAI credentials if you have them

## Step 2: Check Extension Status
1. Look for the Blarify icon in the Activity Bar (left sidebar)
2. Click it to open the Blarify Visualizer panel
3. You should see the Status view

## Step 3: Start Neo4j
The extension should automatically start Neo4j when activated. Check the status bar at the bottom - it should say "Blarify: Neo4j ready" or similar.

If Neo4j fails to start:
- Open Command Palette (`Cmd+Shift+P`)
- Run "Blarify: Restart Neo4j"

## Step 4: Analyze Your Workspace
1. Open Command Palette (`Cmd+Shift+P`)
2. Run "Blarify: Analyze Workspace"
3. Wait for the analysis to complete (progress shown)

## Step 5: View the Visualization
1. Open Command Palette (`Cmd+Shift+P`)
2. Run "Blarify: Show 3D Visualization"
3. The visualization will open in a new panel

## Troubleshooting

### "No data provider registered" error
1. Reload the VS Code window: `Cmd+R` or `Ctrl+R`
2. Check the output panel: View > Output > Select "Blarify Visualizer"

### Neo4j won't start
1. Ensure Docker Desktop is running
2. Run "Blarify: Restart Neo4j" command
3. Check if port 7687 is already in use

### Analysis fails
1. Ensure you have a workspace/folder open
2. Check that Python 3 is installed: `python3 --version`
3. The extension uses the local Blarify code from this repository

### No visualization after analysis
1. Ensure the analysis completed successfully
2. Try running "Blarify: Show 3D Visualization" again
3. Check the browser console in the webview for errors (Help > Toggle Developer Tools)