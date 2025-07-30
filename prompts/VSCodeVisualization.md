We have forked a program called Blarify that uses tree-sitter and language server protocol servers to create a graph of a codebase AST and its bindings to symbols. This is a powerful tool for understanding code structure and relationships. Analyze this code base and remember its structure so that you can make plans about the new features we will add.

## Problem Statement

Developers need intuitive ways to understand complex codebases. While Blarify creates rich graph representations in Neo4j, there's no integrated visualization tool within their development environment. Developers must switch contexts between their IDE and external tools to explore code relationships, making it difficult to:

1. Visualize the overall architecture of a codebase
2. Understand dependencies and relationships between components
3. Navigate complex inheritance hierarchies and call graphs
4. Access LLM-generated summaries and documentation in context
5. Explore how changes might ripple through the codebase

## Feature Overview

We will create a VS Code extension that provides an interactive 3D graph visualization of codebases analyzed by Blarify. The extension will:

1. Automatically manage Neo4j in a Docker container
2. Ingest the current VS Code workspace using Blarify
3. Render an interactive 3D graph visualization
4. Display relationships between files, classes, functions, and other code elements
5. Show LLM summaries and documentation from the knowledge graph
6. Provide search and navigation capabilities
7. Display detailed information for selected nodes and edges

## Technical Requirements

### Core Features

1. **Neo4j Management**
   - Start/stop Neo4j container automatically
   - Check if container exists and reuse it
   - Handle container lifecycle with VS Code extension lifecycle
   - Show status in VS Code status bar

2. **Workspace Ingestion**
   - Detect when VS Code has a workspace open
   - Prompt user to start or update ingestion
   - Show progress during ingestion
   - Support incremental updates for changed files
   - Handle multiple language types supported by Blarify

3. **3D Graph Visualization**
   - Interactive 3D graph using Three.js or similar library
   - WebView panel in VS Code
   - Different node shapes/colors for different types:
     - Files (spheres)
     - Classes (cubes)
     - Functions (pyramids)
     - Folders (larger spheres)
     - Documentation (cylinders)
   - Different edge styles for relationships:
     - Imports (solid lines)
     - Inherits (dashed lines)
     - Calls (dotted lines)
     - Contains (thick lines)
   - Force-directed layout with physics simulation
   - Zoom, pan, rotate controls
   - Node clustering for large graphs

4. **Visual Legend**
   - Floating legend showing all node types and their visual representations
   - Edge type descriptions
   - Toggleable visibility
   - Color coding explanations

5. **Interactive Features**
   - Click node to select and center
   - Hover to show preview tooltip
   - Double-click to open file in editor
   - Right-click context menu for actions
   - Multi-select with Ctrl/Cmd+click
   - Highlight connected nodes on selection
   - Filter by node/edge types
   - Search functionality with autocomplete

6. **Detail Panel**
   - Sidebar or panel showing full details of selected element
   - For nodes:
     - Name, type, path
     - LLM-generated summary
     - Metrics (lines of code, complexity, etc.)
     - Related documentation
     - List of relationships
   - For edges:
     - Relationship type
     - Source and target details
     - Context (line numbers, import statements, etc.)

7. **Search Capabilities**
   - Search bar with fuzzy matching
   - Filter by type (file, class, function, etc.)
   - Search in LLM summaries
   - Quick navigation to search results
   - Search history

### Extension Architecture

```
vscode-blarify-visualizer/
├── src/
│   ├── extension.ts           # Main extension entry point
│   ├── neo4jManager.ts        # Docker container management
│   ├── blarifyIngestion.ts   # Workspace ingestion logic
│   ├── graphProvider.ts      # Graph data provider
│   ├── webview/
│   │   ├── index.html        # WebView HTML
│   │   ├── visualization.js  # 3D graph rendering
│   │   ├── controls.js       # User interaction handling
│   │   └── styles.css        # Styling
│   ├── commands/
│   │   ├── ingestWorkspace.ts
│   │   ├── updateGraph.ts
│   │   └── searchGraph.ts
│   └── config/
│       └── settings.ts       # Configuration management
├── resources/
│   ├── icons/
│   └── templates/
├── package.json
└── README.md
```

### Configuration Settings

The extension should provide VS Code settings for:

```json
{
  "blarifyVisualizer.azureOpenAI.apiKey": "",
  "blarifyVisualizer.azureOpenAI.endpoint": "",
  "blarifyVisualizer.azureOpenAI.deploymentName": "",
  "blarifyVisualizer.neo4j.uri": "bolt://localhost:7687",
  "blarifyVisualizer.neo4j.username": "neo4j",
  "blarifyVisualizer.neo4j.password": "",
  "blarifyVisualizer.visualization.nodeLimit": 500,
  "blarifyVisualizer.visualization.defaultLayout": "force-directed",
  "blarifyVisualizer.ingestion.autoUpdate": true,
  "blarifyVisualizer.ingestion.excludePatterns": []
}
```

### Implementation Plan

1. **Phase 1: Extension Scaffold**
   - Set up VS Code extension project structure
   - Implement basic activation/deactivation
   - Add status bar item
   - Create WebView panel
   - Add configuration settings

2. **Phase 2: Neo4j Integration**
   - Implement Docker container management
   - Check Docker availability
   - Start/stop Neo4j container
   - Monitor container health
   - Handle connection errors

3. **Phase 3: Blarify Integration**
   - Import Blarify as a dependency
   - Implement workspace ingestion command
   - Show progress notifications
   - Handle ingestion errors
   - Support incremental updates

4. **Phase 4: Graph Data Provider**
   - Query Neo4j for graph data
   - Transform to visualization format
   - Implement pagination for large graphs
   - Cache frequently accessed data
   - Handle real-time updates

5. **Phase 5: 3D Visualization**
   - Set up Three.js in WebView
   - Implement force-directed layout
   - Add node and edge rendering
   - Implement camera controls
   - Add selection handling

6. **Phase 6: Interactive Features**
   - Add search functionality
   - Implement detail panel
   - Add context menus
   - Implement filtering
   - Add keyboard shortcuts

7. **Phase 7: Polish and Testing**
   - Add visual legend
   - Improve performance for large graphs
   - Add error handling
   - Write tests
   - Create documentation

### Testing Strategy

1. **Unit Tests**
   - Neo4j manager functions
   - Graph data transformations
   - Search algorithms

2. **Integration Tests**
   - Blarify ingestion process
   - Neo4j queries
   - WebView communication

3. **End-to-End Tests**
   - Full workflow from ingestion to visualization
   - User interaction scenarios
   - Performance with large codebases

### Performance Considerations

1. **Large Graphs**
   - Implement level-of-detail rendering
   - Use clustering for distant nodes
   - Lazy load node details
   - Virtualize search results

2. **Memory Management**
   - Limit number of rendered nodes
   - Dispose Three.js objects properly
   - Clear caches periodically
   - Stream large query results

3. **Responsiveness**
   - Debounce search input
   - Use web workers for heavy computations
   - Progressive rendering
   - Async Neo4j queries

## Development Approach

1. **Study the Codebase Carefully**
   - Review how Blarify creates and stores graphs
   - Understand the Neo4j schema
   - Study existing visualization examples
   - Review VS Code extension best practices

2. **Start with MVP**
   - Basic Neo4j connection
   - Simple 2D visualization first
   - Manual ingestion command
   - Minimal interactivity

3. **Iterate and Enhance**
   - Add 3D visualization
   - Implement search
   - Add detail views
   - Improve performance

4. **User Testing**
   - Test with small codebases first
   - Gather feedback on UX
   - Test with various languages
   - Profile performance

Think carefully about the implementation, create an issue in the repository to describe the feature and your implementation plan. Once the issue is created, create a new branch and proceed with the implementation following test-driven development practices. The extension should be packaged as a .vsix file that can be installed in VS Code.

Key considerations:
- The extension must work on macOS (and ideally cross-platform)
- It should gracefully handle cases where Docker is not installed
- The visualization should be performant even with large codebases
- The UI should follow VS Code design guidelines
- Settings should be stored securely (especially API keys)
- The extension should provide helpful error messages and recovery options