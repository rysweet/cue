We have forked a program called Blarify that uses tree-sitter and language server protocol servers to create a graph of a codebase AST and its bindings to symbols. This is a powerful tool for understanding code structure and relationships. Analyze this code base and remember its structure so that you can make plans about the new features we will add.

## Problem Statement

Currently, Blarify uses a `.blarignore` file to specify which files and directories should be excluded from graph analysis. However, this file is:
1. Independent of `.gitignore` - files in `.gitignore` are NOT automatically ignored
2. Must be manually maintained separately from `.gitignore`
3. Not automatically loaded - requires explicit configuration

This leads to duplication and potential inconsistencies where files ignored by git are still processed by Blarify, wasting resources and potentially including unwanted files in the graph.

## Feature Requirements

We need to modify Blarify so that `.blarignore` becomes **additive** to `.gitignore`. This means:

1. **Automatic .gitignore loading**: All patterns in `.gitignore` should be automatically applied
2. **Additive behavior**: `.blarignore` should add additional exclusions on top of `.gitignore`
3. **Proper pattern matching**: Support full gitignore pattern syntax (not just basename matching)
4. **Backward compatibility**: Existing `.blarignore` functionality should continue to work
5. **Performance**: Efficient pattern matching for large repositories

## Technical Analysis

### Current Implementation Issues

1. `ProjectFilesIterator` only accepts a single `blarignore_path` parameter
2. Pattern matching is limited to basename checking: `os.path.basename(path) in self.names_to_skip`
3. No automatic loading of `.blarignore` from project root
4. No integration with `.gitignore` parsing

### Key Files to Modify

- `cue/project_file_explorer/project_files_iterator.py` - Core file filtering logic
- `cue/prebuilt/graph_builder.py` - High-level API that needs `.gitignore` support
- `cue/main.py` - Example usage patterns

## Implementation Plan

Think carefully about the best way to add this `.gitignore` integration feature. The implementation should:

1. **Parse .gitignore properly**: Use a library like `pathspec` or `gitignore-parser` to handle gitignore pattern syntax correctly
2. **Support nested .gitignore files**: Git supports .gitignore files in subdirectories
3. **Maintain performance**: Cache compiled patterns for efficiency
4. **Provide clear configuration**: Allow users to disable .gitignore integration if needed
5. **Test thoroughly**: Cover edge cases like symlinks, nested patterns, negations

Once you have a good plan, please create an issue in the issues database of the remote repo (https://github.com/rysweet/cue) to describe the feature and record your plan, step by step. Your plan should include:

1. Writing failing tests that demonstrate the current limitation
2. Implementing proper gitignore pattern parsing
3. Integrating with existing file filtering logic
4. Updating the GraphBuilder API to support the new behavior
5. Documenting the new behavior and configuration options

## Testing Requirements

You will need to build comprehensive tests for this feature:

1. **Unit tests** for gitignore pattern parsing
2. **Integration tests** showing `.gitignore` + `.blarignore` working together
3. **Performance tests** for large repositories with complex ignore patterns
4. **Edge case tests** for:
   - Nested .gitignore files
   - Negation patterns (!)
   - Directory patterns (/)
   - Glob patterns (*, **, ?)
   - Comments and blank lines

The tests should manage their dependencies and should do so idempotently, not touching any production systems.

## Implementation Steps

Once the issue is created, then you may please create a new branch in the remote for the issue and switch to it, and then proceed to:

1. **Add gitignore parsing library** to dependencies
2. **Create GitignoreManager class** to handle pattern compilation and matching
3. **Modify ProjectFilesIterator** to:
   - Automatically find and load .gitignore files
   - Combine gitignore and blarignore patterns
   - Use proper pattern matching instead of basename-only
4. **Update GraphBuilder** to expose configuration for gitignore integration
5. **Add comprehensive test suite** covering all scenarios
6. **Update documentation** explaining the new behavior
7. **Ensure backward compatibility** for existing users

Once the work is complete, please create a pull request on https://github.com/rysweet/cue to merge the branch into main, and then review it carefully before merging.

## Success Criteria

The feature is successful when:
1. Files ignored by `.gitignore` are automatically excluded from Blarify's graph
2. `.blarignore` can add additional exclusions beyond `.gitignore`
3. All gitignore pattern syntax is properly supported
4. Performance is not significantly impacted
5. The feature can be configured or disabled if needed
6. Comprehensive tests pass and documentation is updated