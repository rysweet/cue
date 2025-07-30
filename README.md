This repo introduces a method to represent a local code repository as a graph structure. The objective is to allow an LLM to traverse this graph to understand the code logic and flow. Providing the LLM with the power to debug, refactor, and optimize queries.

# Supported Languages

- Python
- JavaScript
- TypeScript
- Ruby
- Go
- C#
- PHP
- Java

# Example

<img src="https://raw.githubusercontent.com/blarApp/blarify/refs/heads/main/docs/visualisation.png"></img>
This graph was generated from the code in this repository.

# Quickstart

Get started with blarify by following our quickstart guide:

[➡️ Quickstart Guide](https://github.com/blarApp/blarify/blob/main/docs/quickstart.md)

# Article

Read our article on Medium to learn more about the motivation behind this project:

[➡️ How we built a tool to turn any codebase into a graph of its relationships](https://medium.com/@v4rgas/how-we-built-a-tool-to-turn-any-code-base-into-a-graph-of-its-relationships-23c7bd130f13)

# Features

- **Code Graph Generation**: Automatically creates a graph representation of your codebase with nodes for files, classes, functions, and their relationships
- **Multi-Language Support**: Supports Python, JavaScript, TypeScript, Ruby, Go, C#, PHP, and Java
- **LLM-Generated Descriptions** (New!): Optionally generate natural language descriptions for code elements using Azure OpenAI
- **Graph Database Integration**: Export to Neo4j or FalkorDB for visualization and querying
- **Incremental Updates**: Efficiently update the graph when code changes

# LLM Description Generation

Blarify can now generate natural language descriptions for your code elements using Azure OpenAI's GPT-4. This feature helps developers quickly understand the purpose and functionality of code components.

## Setup

1. Configure Azure OpenAI credentials in your `.env` file:
```bash
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
ENABLE_LLM_DESCRIPTIONS=true
```

2. Use the feature when building your graph:
```python
graph_builder = GraphBuilder(
    root_path="/path/to/project",
    enable_llm_descriptions=True
)
graph = graph_builder.build()
```

# Future Work

- [x] Gracefully update the graph when new files are added, deleted, or modified
- [x] Add more language servers
- [x] LLM-generated descriptions for code understanding
- [ ] Experiment with parallelizing the language server requests
- [ ] Vector embeddings for semantic code search

# Need help?

If you need help, want to report a bug, or have a feature request, please open an issue on this repository.

You can also reach out to us at [Discord](https://discord.gg/s8pqnPt5AP)
