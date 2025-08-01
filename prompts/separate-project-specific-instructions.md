# Prompt: Separate Project-Specific Instructions from Generic Claude Code Guidelines

## Context
The current CLAUDE.md file contains a mix of generic Claude Code best practices and project-specific instructions for the AI-SIP workshop repository. This creates unnecessary coupling and makes it harder to reuse the generic guidance across different projects.

## Task
Review the CLAUDE.md file and create a modular structure that separates:
1. Generic Claude Code best practices (applicable to any codebase)
2. Project-specific instructions (specific to this JavaScript/D3.js visualization project)

## Analysis Required

### Identify Generic Claude Code Instructions
Review CLAUDE.md and extract sections that are universally applicable:
- Memory management patterns (.github/Memory.md usage)
- Git workflow best practices
- GitHub CLI usage patterns
- Subagent usage guidelines
- Task management principles
- Code review practices
- General AI-enhanced development practices

### Identify Project-Specific Instructions
Extract content specific to this codebase:
- AI-SIP workshop details
- JavaScript/TypeScript/D3.js specific guidelines
- Project-specific code style (ES6+, 2 spaces)
- Specific test frameworks (Playwright)
- Project-specific agents (test-solver)
- Repository-specific files and paths
- Workshop-specific git practices (keeping feature branches)

## Deliverables

### 1. Create `claude-generic-instructions.md`
A reusable template containing:
- Universal memory management patterns
- Generic git workflows
- GitHub CLI usage
- Subagent best practices
- General task management
- Code review principles
- AI development methodologies

### 2. Create `claude-project-specific.md`
Project-specific content including:
- Project overview (AI-SIP workshop)
- Technology stack specifics (JavaScript, D3.js, Neo4j)
- Project-specific agents
- Custom workflows
- Repository-specific conventions

### 3. Update `CLAUDE.md`
Refactor to include both files:
```markdown
# AI Assistant Instructions

<!-- Include generic Claude Code instructions -->
{{include: claude-generic-instructions.md}}

<!-- Include project-specific instructions -->
{{include: claude-project-specific.md}}
```

## Implementation Guidelines

### Structure Considerations
- Use clear section headers
- Maintain the same level of detail
- Ensure no duplication between files
- Keep related content together
- Use consistent formatting

### Include Mechanism
Consider using:
1. Markdown reference links
2. A simple preprocessor script
3. Git submodules for truly generic content
4. Symbolic links where appropriate

### Validation Criteria
- All current functionality preserved
- Clear separation of concerns
- Easy to update either file independently
- Other projects can use generic file
- Project maintainers can focus on project-specific file

## Benefits
1. **Reusability**: Generic instructions can be shared across projects
2. **Maintainability**: Updates to Claude Code best practices in one place
3. **Clarity**: Project teams see what's specific to their codebase
4. **Onboarding**: New team members understand project conventions faster
5. **Standardization**: Organization-wide Claude Code practices

## Example Section Migration

### Before (in CLAUDE.md):
```markdown
### Git Workflow
1. **Always fetch latest before creating branches**: `git fetch origin && git reset --hard origin/main`
2. Create feature branches from main: `feature-<issue-number>-description`
3. Make atomic commits with clear messages
4. Always create PRs for code review
5. Ensure CI/CD passes before merging
6. Keep feature branches (don't delete) for workshop instruction purposes
```

### After:
**In claude-generic-instructions.md:**
```markdown
### Git Workflow
1. **Always fetch latest before creating branches**: `git fetch origin && git reset --hard origin/main`
2. Create feature branches from main: `feature-<issue-number>-description`
3. Make atomic commits with clear messages
4. Always create PRs for code review
5. Ensure CI/CD passes before merging
```

**In claude-project-specific.md:**
```markdown
### Workshop-Specific Git Practices
- Keep feature branches (don't delete) for workshop instruction purposes
- Use descriptive branch names that help workshop attendees understand the progression
```

## Next Steps
1. Execute this separation following the guidelines above
2. Test that the combined instructions work correctly
3. Document the include mechanism chosen
4. Create a migration guide for other projects
5. Consider creating a Claude Code template repository