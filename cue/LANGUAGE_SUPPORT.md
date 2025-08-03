# Blarify Language Support

Blarify supports multiple programming languages through tree-sitter parsers. The system is designed to be robust and will continue to work even if some language parsers are not installed.

## Default Language Support

By default, Blarify includes support for the most popular programming languages:

### Core Languages (Always Included)
- **Python** - tree-sitter-python
- **JavaScript** - tree-sitter-javascript  
- **TypeScript** - tree-sitter-typescript
- **Java** - tree-sitter-java
- **Go** - tree-sitter-go

### Additional Languages (Included by Default)
- **Ruby** - tree-sitter-ruby
- **C#** - tree-sitter-c-sharp
- **PHP** - tree-sitter-php

## Installing Language Support

All language parsers are installed by default when you install Blarify:

```bash
pip install blarify
```

Or with poetry:

```bash
poetry install
```

## Handling Missing Language Support

If a language parser is not installed or fails to import:
- Blarify will display a warning message
- The tool will continue to work for other supported languages
- Files in unsupported languages will be skipped gracefully

Example warning:
```
Warning: Could not import ruby language support: No module named 'tree_sitter_ruby'. ruby files will be skipped.
```

## Checking Available Languages

You can check which languages are available in your installation:

```python
from blarify.code_hierarchy.languages import get_available_languages

available = get_available_languages()
print(f"Available languages: {', '.join(available)}")
```

## Troubleshooting

If you encounter issues with a specific language:

1. **Check if the parser is installed**:
   ```bash
   pip list | grep tree-sitter
   ```

2. **Reinstall the specific parser**:
   ```bash
   pip install tree-sitter-ruby  # or the language you need
   ```

3. **Verify Python version compatibility**: Tree-sitter parsers require Python 3.8+

## Adding New Language Support

To add support for a new language:

1. Install the tree-sitter parser for that language
2. Create a new language definition class in `blarify/code_hierarchy/languages/`
3. Add the language to the mapping in `__init__.py`

The system will automatically detect and use the new language support.