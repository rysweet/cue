# Fix Blarify tree_sitter_ruby ModuleNotFoundError

## Objective
Fix the ModuleNotFoundError for tree_sitter_ruby that prevents Blarify from analyzing any codebase, even non-Ruby projects.

## Context
- Issue #45 tracks this bug
- Blarify is failing on startup due to unconditional import of Ruby language definitions
- The error occurs in the VS Code extension's bundled Blarify installation
- This blocks all code analysis functionality, not just Ruby analysis

## Error Details
```
ModuleNotFoundError: No module named 'tree_sitter_ruby'
```

The error trace shows that `ruby_definitions.py` is imported unconditionally in the languages `__init__.py` file, causing failure even for non-Ruby projects.

## Requirements
1. Make language-specific imports conditional or lazy-loaded
2. Ensure Blarify can analyze codebases without requiring all language parsers installed
3. Maintain backward compatibility
4. Add appropriate error handling for missing language modules
5. Test the fix with both Ruby and non-Ruby projects

## Technical Approach
1. Modify `blarify/code_hierarchy/languages/__init__.py` to use conditional imports
2. Implement lazy loading for language-specific parsers
3. Add try-except blocks around language imports with informative warnings
4. Consider using importlib for dynamic imports based on detected languages
5. Ensure GoDefinitions and other language parsers are similarly handled

## Testing Requirements
1. Verify Blarify starts successfully without tree_sitter_ruby installed
2. Test analysis on Python, JavaScript, and Go projects
3. Ensure Ruby analysis works when tree_sitter_ruby IS installed
4. Verify error messages are helpful when language support is missing

## Success Criteria
- Blarify analyzes non-Ruby codebases without errors
- Missing language parsers generate warnings, not failures
- All existing functionality remains intact
- Code is clean, maintainable, and follows project conventions