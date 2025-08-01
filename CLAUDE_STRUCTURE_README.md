# Claude Instructions Structure

This repository now uses a modular structure for Claude Code instructions to separate generic best practices from project-specific guidance.

## Files

### `claude-generic-instructions.md`
Universal Claude Code best practices that can be reused across any project:
- Memory management patterns
- Git workflow best practices
- GitHub CLI usage
- Subagent guidelines
- Task management principles
- Code review practices

### `claude-project-specific.md`
Instructions specific to the AI-SIP workshop repository:
- Project overview and workshop context
- Technology stack (JavaScript, D3.js, Neo4j)
- Project-specific coding standards
- Available specialized agents
- Workshop-specific practices

### `CLAUDE.md`
The main instruction file that combines both generic and project-specific instructions using a manual include approach with START/END markers.

## Maintenance

When updating instructions:

1. **For generic Claude Code practices**: Edit `claude-generic-instructions.md`
2. **For project-specific guidance**: Edit `claude-project-specific.md`
3. **Update CLAUDE.md**: Copy the updated content between the corresponding START/END markers

## Adoption Guide

For other projects wanting to use this structure:

1. Copy `claude-generic-instructions.md` to your project
2. Create your own `[project]-specific.md` file with project details
3. Create a `CLAUDE.md` that combines both using the template structure
4. Optionally create a build script to automate the combination

## Benefits

- **Reusability**: Generic instructions can be shared across projects
- **Maintainability**: Updates to Claude Code best practices in one place
- **Clarity**: Clear separation between universal and project-specific guidance
- **Standardization**: Consistent Claude Code practices across an organization