# Blarify Code Visualizer

Interactive 3D visualization of codebase structure and relationships powered by Blarify and Neo4j.

## Features

- **Automatic Neo4j Management**: Automatically starts and manages a Neo4j Docker container
- **Workspace Analysis**: Analyze your entire workspace with Blarify to generate a comprehensive code graph
- **3D Visualization**: Interactive Three.js-based 3D rendering with multiple layout algorithms
- **Smart Search**: Real-time search across nodes by name, type, or properties
- **Node Filtering**: Filter visualization by node types (classes, functions, files, etc.)
- **Interactive Exploration**: Click nodes to view details and expand neighborhoods
- **Visual Legend**: Color-coded node types with counts
- **Status Integration**: Status bar shows current state and quick access to visualization

## Requirements

- Docker Desktop installed and running
- Python 3.8+ installed and in PATH
- VS Code 1.74.0 or higher

**Note**: This extension uses the local Blarify installation from the same repository. Make sure the extension is located at `vscode-blarify-visualizer/` within the Blarify repository structure.

## Getting Started

1. **Install the Extension**
   - Download the `.vsix` file
   - In VS Code, run "Extensions: Install from VSIX..." command
   - Select the downloaded file

2. **Configure Azure OpenAI (Optional)**
   - Open VS Code settings
   - Search for "Blarify Visualizer"
   - Add your Azure OpenAI credentials for enhanced LLM summaries

3. **Open Your Project**
   - Open a folder containing your codebase
   - The extension will activate automatically

4. **Analyze Your Workspace**
   - You'll be prompted to analyze your workspace on startup
   - Or run "Blarify: Analyze Workspace" command
   - Wait for the analysis to complete

5. **View the Visualization**
   - Run "Blarify: Show 3D Visualization" command
   - Or click the status bar item

## Usage

### Navigation
- **Left Click + Drag**: Rotate the view
- **Right Click + Drag**: Pan the view
- **Scroll**: Zoom in/out
- **Click Node**: Select and view details
- **Double Click Node**: Expand node neighborhood

### Search
- Use the search bar to find nodes by:
  - Name (e.g., "UserService")
  - Type (e.g., "class:" or "function:")
  - File path (e.g., "auth.py")

### Layouts
- **Force Directed**: Physics-based layout showing natural clusters
- **Hierarchical**: Layered layout based on node types
- **Circular**: Nodes arranged in a circle

### Filtering
- Use the filter checkboxes to show/hide node types
- Useful for focusing on specific parts of your codebase

## Commands

- `Blarify: Show 3D Visualization` - Open the visualization panel
- `Blarify: Analyze Workspace` - Run Blarify analysis on your workspace
- `Blarify: Update Graph` - Re-analyze changed files
- `Blarify: Search Graph` - Open search dialog

## Settings

### Azure OpenAI
- `blarifyVisualizer.azureOpenAI.apiKey`: Your API key
- `blarifyVisualizer.azureOpenAI.endpoint`: Your endpoint URL
- `blarifyVisualizer.azureOpenAI.deploymentName`: Model deployment name

### Neo4j
- `blarifyVisualizer.neo4j.uri`: Connection URI (default: bolt://localhost:7687)
- `blarifyVisualizer.neo4j.username`: Username (default: neo4j)
- `blarifyVisualizer.neo4j.password`: Password (REQUIRED - no default)

### Visualization
- `blarifyVisualizer.visualization.nodeLimit`: Maximum nodes to render (default: 500)
- `blarifyVisualizer.visualization.defaultLayout`: Default layout algorithm

### Ingestion
- `blarifyVisualizer.ingestion.autoUpdate`: Auto-update on file changes
- `blarifyVisualizer.ingestion.excludePatterns`: Additional patterns to exclude

## Node Types

- 🔵 **FILE**: Source code files
- 🔴 **CLASS**: Class definitions
- 🟢 **FUNCTION**: Function definitions
- 🟢 **METHOD**: Class methods
- 🟣 **MODULE**: Python modules or packages
- 🟡 **FOLDER**: Directory structure
- 🔷 **DOCUMENTATION_FILE**: Markdown and other docs
- 🟠 **CONCEPT**: Extracted concepts from documentation
- ⚫ **DOCUMENTED_ENTITY**: Code entities referenced in docs

## Troubleshooting

### Neo4j won't start
- Ensure Docker Desktop is running
- Check if port 7687 is already in use
- Try restarting VS Code

### Blarify not found
- Install Blarify: `pip install blarify`
- Ensure Python is in your PATH
- Restart VS Code after installation

### Empty visualization
- Check if the analysis completed successfully
- Look for errors in the Output panel ("Blarify Visualizer")
- Try re-analyzing the workspace

### Performance issues
- Reduce `nodeLimit` in settings
- Close other heavy applications
- Use filtering to show fewer nodes

## Privacy & Security

- All analysis is performed locally
- Neo4j runs in a local Docker container
- No data is sent to external services (except Azure OpenAI if configured)
- The Neo4j container is isolated and uses a random password

## Contributing

This extension is part of the Blarify project. Contributions are welcome!

- Report issues: https://github.com/rysweet/cue/issues
- Source code: https://github.com/rysweet/cue

## License

MIT License - see LICENSE file for details