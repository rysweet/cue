We have forked a program called Blarify that uses tree-sitter and language server protocol servers to create a graph of a codebase AST and its bindings to symbols. This is a powerful tool for understanding code structure and relationships. Analyze this code base and remember its structure so that you can make plans about the new features we will add.

## Problem Statement

Modern software projects contain extensive documentation in various formats (README.md, API docs, architecture docs, user guides, etc.) that describe important concepts, design decisions, workflows, and relationships. Currently, Blarify only analyzes code structure but misses this rich semantic information contained in documentation. This creates a gap between the code's implementation and its intended design and usage patterns.

## Feature Overview

We are going to add a new feature to Blarify that parses documentation files and creates a knowledge graph of important concepts, relationships, and entities found within them. This documentation graph will be integrated with the existing code graph, creating connections between documented concepts and their implementations in code.

The feature will:
1. Identify and parse documentation files (Markdown, reStructuredText, plain text, etc.)
2. Use Azure OpenAI's GPT-4 to extract concepts, entities, and relationships from documentation
3. Create DOCUMENTATION nodes and relationship edges in the graph
4. Intelligently link documentation nodes to relevant code nodes (files, classes, functions)
5. Execute after AST+symbols, filesystem, and LLM summaries processing

## Feature Requirements

### Documentation File Detection
- Automatically detect documentation files by extension: `.md`, `.markdown`, `.rst`, `.txt`, `.adoc`, `README*`, `CHANGELOG*`, `LICENSE*`
- Support documentation in common directories: `docs/`, `documentation/`, project root
- Allow configuration of additional documentation patterns

### LLM-Powered Knowledge Extraction
Using Azure OpenAI, extract:
1. **Concepts**: Key ideas, patterns, architectures (e.g., "Event-Driven Architecture", "Repository Pattern")
2. **Entities**: Components, services, modules mentioned (e.g., "UserService", "AuthenticationModule")
3. **Relationships**: How concepts relate (e.g., "UserService implements Repository Pattern")
4. **Code References**: Files, classes, or functions mentioned in documentation

### Graph Structure
Create new node types:
- `DOCUMENTATION_FILE`: Represents a documentation file
- `CONCEPT`: Represents an abstract concept or pattern
- `DOCUMENTED_ENTITY`: Represents a documented component/service/module
- `DOCUMENTATION_SECTION`: Represents major sections within docs

Create new relationship types:
- `CONTAINS_CONCEPT`: Documentation file contains a concept
- `DESCRIBES_ENTITY`: Documentation describes an entity
- `RELATES_TO`: Concept relates to another concept
- `DOCUMENTS`: Documentation node documents a code node
- `IMPLEMENTS_CONCEPT`: Code node implements a documented concept

### Intelligent Cross-Linking
The LLM should analyze documentation content and:
1. Identify code references (file paths, class names, function names)
2. Match documented entities to actual code nodes
3. Create edges between documentation and code nodes
4. Infer relationships even when not explicitly stated

### Configuration
- Use existing Azure OpenAI configuration from environment/settings
- Allow enabling/disabling documentation parsing
- Configure which file patterns to include/exclude
- Set limits on LLM calls per documentation file

## Technical Analysis

### Current Architecture Understanding
- Blarify processes files through `ProjectGraphCreator`
- Features are modular (LLM descriptions, filesystem nodes)
- Graph nodes extend base `Node` class
- Relationships are created through `RelationshipCreator`
- Azure OpenAI integration exists in `llm_descriptions` module

### Key Integration Points
1. **ProjectGraphCreator**: Add `_generate_documentation_nodes()` method
2. **Node Types**: Extend `NodeLabels` with documentation types
3. **Relationships**: Extend `RelationshipType` with documentation relationships
4. **LLM Service**: Reuse existing `LLMService` with new prompts
5. **File Detection**: Integrate with `ProjectFilesIterator`

### Processing Flow
1. After code graph is built (AST + symbols + filesystem + LLM summaries)
2. Identify documentation files in the project
3. For each documentation file:
   - Read content
   - Send to LLM with structured prompt for extraction
   - Parse LLM response into concepts and entities
   - Create documentation nodes
4. Cross-link documentation nodes with code nodes
5. Add all nodes and relationships to graph

## Implementation Plan

### Architecture Design
1. Create `cue/documentation/` module with:
   - `documentation_parser.py`: Main parser class
   - `concept_extractor.py`: LLM-based concept extraction
   - `documentation_linker.py`: Links docs to code nodes
   - `documentation_types.py`: Node and relationship types

2. Extend existing types:
   - Add documentation node types to `NodeLabels`
   - Add documentation relationships to `RelationshipType`

3. Integration approach:
   - Follow pattern of `filesystem` and `llm_descriptions` modules
   - Make feature optional via configuration
   - Reuse existing LLM infrastructure

### LLM Prompt Design
Create structured prompts that:
1. Extract concepts with descriptions
2. Identify entities and their relationships
3. Find code references (explicit and implicit)
4. Maintain consistent JSON output format

Example prompt structure:
```
Analyze this documentation and extract:
1. Key concepts and patterns discussed
2. Named entities (components, services, classes)
3. Relationships between concepts
4. References to code files, classes, or functions

Documentation content:
{content}

Return as JSON with structure:
{
  "concepts": [...],
  "entities": [...],
  "relationships": [...],
  "code_references": [...]
}
```

## Testing Requirements

### Test Strategy
1. **Unit Tests**:
   - Documentation file detection
   - Concept extraction with mocked LLM
   - Node creation logic
   - Cross-linking algorithms

2. **Integration Tests**:
   - Full pipeline with sample documentation
   - Graph structure validation
   - Edge creation verification

3. **Test Documentation Types**:
   - README with architecture overview
   - API documentation
   - Code examples in docs
   - Tutorial/guide documents

### Test Infrastructure
- Use pytest fixtures for test documentation
- Mock Azure OpenAI responses for consistent testing
- Create test graphs to verify relationships
- Ensure tests don't require actual LLM calls

## Implementation Steps

Once you have analyzed the codebase and created a detailed plan, please create an issue in the issues database of the remote repo (https://github.com/rysweet/cue) to describe the feature and record your plan, step by step.

Once the issue is created, then create a new branch in the remote for the issue and switch to it, then proceed to:

1. **Write failing tests** that demonstrate the desired functionality
2. **Create documentation module structure** with necessary classes
3. **Extend node and relationship types** for documentation
4. **Implement documentation file detection** in the file iterator
5. **Create concept extraction logic** using LLM with structured prompts
6. **Implement documentation parser** that orchestrates the extraction
7. **Build cross-linking system** to connect docs to code
8. **Integrate with ProjectGraphCreator** to run after other processing
9. **Add configuration options** to GraphBuilder
10. **Update documentation** with usage examples
11. **Ensure all tests pass** and refactor as needed

Commit changes incrementally as you implement each component.

## Success Criteria

The feature is successful when:
1. Documentation files are automatically detected and parsed
2. Concepts, entities, and relationships are accurately extracted
3. Documentation nodes are properly linked to relevant code nodes
4. The feature can be enabled/disabled via configuration
5. LLM prompts produce consistent, structured output
6. Cross-references between docs and code are accurate
7. All tests pass and documentation is complete
8. Performance impact is acceptable (configurable LLM call limits)

## Example Usage

```python
# Enable documentation parsing
graph_builder = GraphBuilder(
    root_path="/path/to/project",
    enable_documentation_nodes=True,
    documentation_patterns=["*.md", "docs/**/*.rst"],  # Optional custom patterns
    max_llm_calls_per_doc=5  # Optional rate limiting
)

graph = graph_builder.build()

# Query documentation nodes
documentation_nodes = graph.get_nodes_by_label(NodeLabels.DOCUMENTATION_FILE)
concept_nodes = graph.get_nodes_by_label(NodeLabels.CONCEPT)

# Find which code implements a concept
auth_concept = graph.find_node_by_name("Authentication Flow")
implementing_code = graph.get_relationships_by_type(
    RelationshipType.IMPLEMENTS_CONCEPT,
    end_node=auth_concept
)
```

Once the work is complete, please create a pull request on https://github.com/rysweet/cue to merge the branch into main, and then review it carefully before merging.