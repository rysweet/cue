# MCP Blarify Server

An MCP (Model Context Protocol) server that provides AI coding agents with sophisticated tools to query and analyze Blarify graph databases stored in Neo4j.

## Overview

This MCP server sits in front of a Neo4j database containing a Blarify graph representation of a codebase. It provides three main tools that AI agents can use to understand code structure, relationships, and plan changes.

## Features

### Tools

1. **`getContextForFiles`**
   - Retrieves comprehensive context for specified files
   - Includes classes, functions, dependencies, imports, and documentation
   - Traverses the graph to configurable depth
   - Returns organized Markdown with LLM assistance

2. **`getContextForSymbol`**
   - Gets detailed context for a specific symbol (class, function, variable)
   - Finds definitions, usages, inheritance, and relationships
   - Supports fuzzy matching for symbol names
   - Shows callers, callees, and references

3. **`buildPlanForChange`**
   - Analyzes codebase to create implementation plans
   - Extracts entities from change requests using LLM
   - Identifies affected files, dependencies, and tests
   - Generates step-by-step implementation guide

### Capabilities

- **Intelligent Query Building**: Constructs efficient Cypher queries for complex traversals
- **LLM Integration**: Uses Azure OpenAI to organize results and extract information
- **Context Organization**: Structures graph data into readable Markdown
- **Impact Analysis**: Traces dependencies and affected components
- **Pattern Recognition**: Identifies design patterns and architectural concepts

## Installation

1. Clone the repository:
```bash
cd mcp-blarify-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Neo4j configuration
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your-password"
export NEO4J_DATABASE="neo4j"

# Azure OpenAI configuration (optional but recommended)
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# Optional settings
export MAX_TRAVERSAL_DEPTH="3"
export MAX_CONTEXT_LENGTH="8000"
export ENABLE_QUERY_CACHE="true"
```

## Usage

### Running the Server

```bash
python -m src.server
```

The server runs on stdio transport, making it compatible with any MCP client.

### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "blarify": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-blarify-server",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your-password",
        "AZURE_OPENAI_API_KEY": "your-api-key",
        "AZURE_OPENAI_ENDPOINT": "https://your-instance.openai.azure.com/"
      }
    }
  }
}
```

### Example Queries

#### Get Context for Files
```
Use the getContextForFiles tool to show me the context for:
- src/services/auth.py
- src/models/user.py
```

#### Find Symbol Information
```
Use the getContextForSymbol tool to find information about the UserService class
```

#### Build Implementation Plan
```
Use the buildPlanForChange tool to create a plan for:
"Add email verification to the user registration process"
```

## Architecture

```
mcp-blarify-server/
├── src/
│   ├── server.py              # Main MCP server
│   ├── config.py              # Configuration management
│   ├── tools/
│   │   ├── context_tools.py   # File and symbol context retrieval
│   │   ├── planning_tools.py  # Change planning functionality
│   │   └── query_builder.py   # Cypher query construction
│   └── processors/
│       ├── graph_traversal.py # Neo4j graph traversal logic
│       ├── context_builder.py # Context organization
│       └── llm_processor.py   # LLM integration for formatting
└── tests/                     # Test suite
```

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `NEO4J_DATABASE` | Neo4j database name | `neo4j` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | None |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | None |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | `gpt-4` |
| `MAX_TRAVERSAL_DEPTH` | Maximum graph traversal depth | `3` |
| `MAX_CONTEXT_LENGTH` | Maximum context length in chars | `8000` |
| `ENABLE_QUERY_CACHE` | Enable query result caching | `true` |
| `CACHE_TTL_SECONDS` | Cache time-to-live | `3600` |

## Development

### Running Tests

#### Unit Tests

Run unit tests without Neo4j:
```bash
pytest tests/test_query_builder.py tests/test_context_builder.py tests/test_llm_processor.py tests/test_server.py -v
```

#### Integration Tests

Run integration tests with real Neo4j:

1. Start Neo4j:
```bash
docker-compose up -d
```

2. Set up test data:
```bash
python tests/setup_test_graph.py
```

3. Run integration tests:
```bash
pytest tests/test_integration.py -v
```

Or use the convenience script:
```bash
./run_integration_tests.sh
```

#### Manual Testing

Test the server interactively:
```bash
python manual_test.py
```

This will:
- Connect to Neo4j
- List available tools
- Test each tool with sample data
- Show example responses

### Adding New Tools

1. Create tool arguments model in `server.py`
2. Add tool definition in `handle_list_tools()`
3. Implement tool logic in appropriate module
4. Add handler in `handle_call_tool()`

### Extending Query Patterns

Add new query builders in `src/tools/query_builder.py` for custom graph traversals.

## Troubleshooting

### Connection Issues

If you see connection errors:
1. Verify Neo4j is running: `neo4j status`
2. Check credentials and URI
3. Ensure the database exists
4. Test connection with `cypher-shell`

### LLM Processing

If LLM features aren't working:
1. Verify Azure OpenAI credentials
2. Check API endpoint format
3. Ensure deployment name is correct
4. Monitor API quotas

### Performance

For large graphs:
1. Adjust `MAX_TRAVERSAL_DEPTH`
2. Use `MAX_NODES_PER_TYPE` limits
3. Enable query caching
4. Consider adding indexes in Neo4j

## License

This project follows the same license as the parent Blarify project.