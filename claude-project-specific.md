# Blarify/Cue Project-Specific Instructions

## Overview

This repository contains Blarify (formerly Cue), a sophisticated code analysis tool that creates comprehensive multilayer graph representations of codebases. The project enables AI agents and developers to understand, navigate, and modify code with unprecedented precision through intelligent graph structures.

The project includes:
- **Blarify Core**: Python-based code analysis engine with multilayer graph generation
- **VS Code Extension**: Interactive 3D visualization with ThreeJS-based rendering  
- **MCP Server**: Model Context Protocol server for AI agent integration
- **Neo4j Integration**: Graph database storage and querying capabilities

## Project-Specific Guidelines

### Code Style
- Follow existing Python patterns and PEP 8 conventions
- Use type hints for better code clarity and IDE support
- Maintain consistent indentation (4 spaces for Python, 2 for JSON/YAML)
- Use descriptive variable and function names that reflect domain concepts
- Prefer composition over inheritance in graph node design

### Development Practices
- Keep feature branches for review and CI/CD pipeline execution
- Use descriptive branch names that reflect the feature or fix being implemented
- Maintain comprehensive test coverage (target >80%)

### Project-Specific Files to Verify
- Always verify existence of: `CLAUDE.md`, `prompts/`, `.github/agents/`
- These files may contain critical project configuration
- The repository should be: `rysweet/cue`

### Testing Strategy
- Write comprehensive tests for all new features and bug fixes
- Maintain test coverage above 80% (current: 63.76%)
- Use pytest for unit and integration testing
- Mock external dependencies (Neo4j, Azure OpenAI) appropriately
- Test error scenarios, edge cases, and language parser edge cases
- Validate graph structure integrity and relationship consistency

### Error Handling
- Use structured logging with appropriate log levels
- Implement graceful degradation for missing language parsers
- Handle Neo4j connection failures with clear error messages
- Validate graph data integrity before database operations
- Provide helpful error messages for configuration issues

## Available Project Agents
- **workflow-master**: Orchestrates complete development workflows from prompt files
- **code-reviewer**: Conducts comprehensive code reviews with quality checks
- **orchestrator-agent**: Manages parallel execution of multiple workflow tasks
- **test-solver**: Specialized in fixing failing tests and improving test coverage

## Graph-First Development
- Design features around graph data structures and relationships
- Consider impact on all graph layers (filesystem, code hierarchy, documentation, semantic)
- Validate graph traversal efficiency for new relationship types
- Test visualization performance with large graphs
- Ensure incremental update operations maintain graph consistency

## Technology Stack Resources
- [Neo4j Documentation](https://neo4j.com/docs/) - Graph database queries and operations
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/) - Language parsing and AST analysis
- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) - Code analysis and symbol resolution
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI agent integration patterns
- [ThreeJS Documentation](https://threejs.org/docs/) - 3D visualization in VS Code extension
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/) - LLM integration

## Project Structure
This is a Python-based project with multiple components:
- **Core**: Python package with graph analysis engine
- **VS Code Extension**: TypeScript/JavaScript extension with 3D visualization
- **MCP Server**: Python MCP server for AI agent integration  
- **Neo4j Container Manager**: Node.js package for Docker container management
- **Tests**: Comprehensive pytest test suite with >63% coverage

## Development Context
This repository demonstrates advanced AI-powered code analysis. When making changes:
- Consider impact on graph structure and relationships
- Validate changes don't break existing language parsers
- Test with real codebases to ensure scalability
- Document new graph relationship types and their semantics
- Maintain backwards compatibility for existing graph databases