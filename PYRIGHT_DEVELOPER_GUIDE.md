# Pyright Type Checking Developer Guide

## Overview

This project is implementing comprehensive static type checking using Pyright to achieve 100% type safety compliance. This guide provides developers with the knowledge and tools needed to work effectively with the type checking system.

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry for dependency management
- Pyright is automatically installed via development dependencies

### Installation

```bash
# Install all dependencies including pyright
poetry install

# Verify pyright installation
poetry run pyright --version
```

## Configuration

### Pyright Configuration

The project uses `pyrightconfig.json` with strict type checking enabled:

```json
{
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.12"
}
```

### VS Code Integration

For optimal development experience, install the Pylance extension:

1. Install "Python" and "Pylance" extensions
2. Pyright will automatically use the project's configuration
3. Type errors will be highlighted in real-time

## Type Checking Commands

### Basic Commands

```bash
# Check entire codebase
poetry run pyright cue/

# Check specific file
poetry run pyright cue/graph/graph.py

# Check with statistics
poetry run pyright cue/ --stats

# Generate JSON output for CI
poetry run pyright cue/ --outputjson
```

### Development Workflow

```bash
# Quick check during development
poetry run pyright <file_you_modified>

# Full validation before commit
poetry run pyright cue/
```

## Type Annotation Guidelines

### Function Signatures

```python
# Good: Complete type annotations
def process_node(node: Node, options: Dict[str, Any]) -> Optional[ProcessResult]:
    pass

# Bad: Missing type annotations
def process_node(node, options):
    pass
```

### Class Attributes

```python
# Good: Explicit attribute typing
class Graph:
    nodes_by_path: DefaultDict[str, Set[Node]]
    file_nodes_by_path: Dict[str, FileNode]
    
    def __init__(self) -> None:
        self.nodes_by_path = defaultdict(set)
        self.file_nodes_by_path = {}
```

### Generic Types

```python
# Good: Specific generic types
def get_nodes_by_label(self, label: NodeLabels) -> Set[Node]:
    return self.nodes_by_label[label]

# Bad: Unspecified generic types
def get_nodes_by_label(self, label) -> set:
    return self.nodes_by_label[label]
```

### Optional Types

```python
# Good: Proper Optional typing
def create_node(parent: Optional[Node] = None) -> Node:
    pass

# Bad: None without Optional
def create_node(parent: Node = None) -> Node:  # Type error!
    pass
```

## Common Patterns

### TYPE_CHECKING Pattern

For circular imports, use the TYPE_CHECKING pattern:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cue.graph.relationship import Relationship

class Node:
    def get_relationships(self) -> List["Relationship"]:
        return []
```

### Forward References

Use string literals for forward references:

```python
class Node:
    parent: "Node"  # Forward reference to same class
    
    def add_child(self, child: "Node") -> None:
        pass
```

### Dict Return Types

For methods returning dictionaries:

```python
def as_object(self) -> Dict[str, Any]:
    return {
        "id": self.id,
        "type": self.label.name,
        "attributes": {...}
    }
```

## Current Implementation Status

### ✅ Fully Typed Modules

- `cue/graph/graph.py` - **Zero pyright errors**
- `cue/graph/node/types/node.py` - Basic typing complete
- `cue/graph/relationship/relationship.py` - Basic typing complete

### 🔄 In Progress

- `cue/graph/node/` - Node hierarchy (175 errors)
- Import cycle resolution across modules
- Optional type parameter fixes

### ⏳ Pending

- Database managers (`cue/db_managers/`)
- LSP integration (`cue/code_references/`)
- Language processing (`cue/code_hierarchy/`)
- LLM integration (`cue/llm_descriptions/`)
- File system operations (`cue/project_file_explorer/`)
- Test files (`tests/`)

## Error Categories and Solutions

### 1. Import Cycles

**Problem**: Circular import dependencies
**Solution**: Use TYPE_CHECKING pattern

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from other_module import SomeClass
```

### 2. Missing Type Annotations

**Problem**: Functions without type hints
**Solution**: Add comprehensive annotations

```python
# Before
def process_data(data):
    return processed_data

# After  
def process_data(data: List[Dict[str, Any]]) -> ProcessedData:
    return processed_data
```

### 3. Optional Parameters

**Problem**: None values without Optional typing
**Solution**: Use Optional[T] or Union[T, None]

```python
# Before
def create_node(parent: Node = None):
    pass

# After
def create_node(parent: Optional[Node] = None):
    pass
```

### 4. Generic Collections

**Problem**: Untyped lists, dicts, sets
**Solution**: Specify element types

```python
# Before
nodes: list = []

# After
nodes: List[Node] = []
```

## Troubleshooting

### Common Issues

1. **"Type is partially unknown"**
   - Add explicit type annotations
   - Check that all dependencies are properly typed

2. **"Cannot assign None to parameter"**
   - Use Optional[T] for parameters that can be None
   - Check default parameter values

3. **"Cycle detected in import chain"**
   - Use TYPE_CHECKING pattern
   - Restructure imports to avoid cycles

4. **"reportUnusedImport"**
   - Remove unused imports
   - Move type-only imports to TYPE_CHECKING block

### Performance Tips

- **Incremental checking**: Pyright only re-checks modified files
- **IDE integration**: Use Pylance for real-time feedback
- **Focused checking**: Check specific files during development

## CI/CD Integration

### Current Pipeline

The project uses gradual adoption:

```yaml
- name: Run type checking with pyright
  run: |
    poetry run pyright cue/graph/graph.py || echo "Type checking in progress"
```

### Future Pipeline (Target)

```yaml
- name: Run type checking
  run: |
    poetry run pyright cue/
```

## Contributing

### Before Submitting PRs

1. **Run type checking**: `poetry run pyright <files_modified>`
2. **Fix type errors**: Address all pyright issues
3. **Add type annotations**: Ensure new code is fully typed
4. **Update tests**: Include type annotations in test files

### Code Review Checklist

- [ ] All functions have return type annotations
- [ ] All parameters have type annotations
- [ ] Optional parameters use Optional[T]
- [ ] Generic collections specify element types
- [ ] No pyright errors in modified files
- [ ] TYPE_CHECKING pattern used for circular imports

## Resources

- [Pyright Documentation](https://github.com/microsoft/pyright)
- [Python Typing Module](https://docs.python.org/3/library/typing.html)
- [MyPy Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Type Hints PEP 484](https://www.python.org/dev/peps/pep-0484/)

## Support

For questions about type checking in this project:

1. Check this guide for common patterns
2. Run `poetry run pyright --help` for command options
3. Review existing typed modules for examples
4. Create an issue for complex typing challenges

---

*This guide will be updated as more modules achieve type safety compliance.*