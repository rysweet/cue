# AI-SIP Workshop Repository

⚠️ **FIRST ACTION**: Check and update `.github/Memory.md` ! ⚠️

## Overview

This repository contains a sample JavaScript application used in the AI-SIP (AI-enhanced Software development In Practice) workshop. The application visualizes file system structures as an interactive graph using D3.js, providing a hands-on environment for demonstrating AI-assisted development workflows, debugging practices, and automated issue management.

The workshop focuses on:
- Leveraging AI tools like Claude Code and GitHub Copilot for efficient development
- Implementing test-driven development with AI assistance
- Creating automated error handling and issue creation workflows
- Building visual debugging and annotation features

## Required Context

**CRITICAL - MUST DO AT START OF EVERY SESSION**: 
1. **READ** `.github/Memory.md` for current context
2. **UPDATE** `.github/Memory.md` after completing any significant task
3. **COMMIT** Memory.md changes regularly to preserve context

**Memory.md is your persistent brain across sessions - USE IT!**


## Using GitHub CLI for Issue and PR Management

### Issues
```bash
# Create a new issue
gh issue create --title "Issue title" --body "Issue description"

# List open issues
gh issue list

# View issue details
gh issue view <issue-number>

# Update issue
gh issue edit <issue-number>

# Close issue
gh issue close <issue-number>
```

### Pull Requests
```bash
# Create a PR
gh pr create --base main --head feature-branch --title "PR title" --body "PR description"

# List PRs
gh pr list

# View PR details
gh pr view <pr-number>

# Check PR status
gh pr checks <pr-number>

# Merge PR
gh pr merge <pr-number>
```

### Workflows
```bash
# List workflow runs
gh workflow run list

# View workflow run details
gh run view <run-id>

# Watch workflow run in real-time
gh run watch <run-id>
```

## Best Practices for AI-Enhanced Development

### 1. Clear Documentation
- Maintain this CLAUDE.md file with up-to-date instructions and context
- Document all major decisions and architectural choices
- Include examples and edge cases in documentation

### 2. Structured Task Management
- Break down complex features into smaller, manageable tasks
- Use GitHub issues to track all work items
- Create detailed implementation plans before coding

### 3. Visual-First Development
- Use screenshots and mockups to guide implementation
- Test UI changes visually using the Playwright MCP service
- Capture and annotate screenshots for bug reports

### 4. Iterative Improvement
- Start with a working prototype and iterate
- Use test-driven development when possible
- Course-correct early based on test results

### 5. Context Management
- Use `/clear` command to reset context when switching tasks
- Keep focused on one feature at a time
- Reference specific files when discussing code changes

### 6. Subagents
- subagents are documented at https://docs.anthropic.com/en/docs/claude-code/sub-agents - you may read that document to understand them
- Utilize specialized agents for repetitive tasks
- Create new agents for common patterns or issues
- Document agent capabilities and usage patterns
- Subagents can be used to pass scoped or limited context to specialized agents for focused tasks - eg testing, debugging, database management. 

## Memory Storage Instructions

### Regular Memory Updates
You should regularly update the memory file at `.github/Memory.md` with:
- Current date and time
- Consolidated summary of completed tasks
- Current todo list with priorities
- Important context and decisions made
- Any blockers or issues encountered

### Memory File Format
```markdown
# AI Assistant Memory
Last Updated: [ISO 8601 timestamp]

## Current Goals
[List of active goals]

## Todo List
[Current tasks with status]

## Recent Accomplishments
[What was completed recently]

## Important Context
[Key decisions, patterns, or information to remember]

## Reflections
[Insights and improvements]
```

### When to Update Memory
**MANDATORY UPDATE TRIGGERS:**
- ✅ After completing ANY task from todo list
- ✅ When creating or merging a PR
- ✅ When discovering important technical details
- ✅ After fixing any bugs
- ✅ Every 30 minutes during long sessions
- ✅ BEFORE ending any conversation

**Set a mental reminder: "Did I update Memory.md in the last 30 minutes?"**

### Memory Pruning
Keep the memory file concise by:
- Removing completed tasks older than 7 days
- Consolidating similar context items
- Archiving detailed reflections after incorporating improvements
- Keeping only the most recent 5-10 accomplishments

## Task Completion Reflection

After completing each task, reflect on:

### What Worked Well
- Successful approaches and techniques
- Effective tool usage
- Good architectural decisions

### Areas for Improvement
- What could have been done more efficiently
- Any confusion or missteps
- Missing documentation or context

### User Feedback Integration
If the user expressed frustration or provided feedback:
- Document the specific issue
- Propose improvements to this CLAUDE.md file
- Update relevant sections to prevent recurrence
- Add new best practices based on learnings

### Continuous Improvement
- Update this file with new patterns discovered
- Add commonly used commands
- Document project-specific conventions
- Include solutions to recurring problems

## Project-Specific Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use ES6+ JavaScript features
- Maintain consistent indentation (2 spaces)
- Add meaningful variable and function names

### Git Workflow
1. **Always fetch latest before creating branches**: `git fetch origin && git reset --hard origin/main`
2. Create feature branches from main: `feature-<issue-number>-description`
3. Make atomic commits with clear messages
4. Always create PRs for code review
5. Ensure CI/CD passes before merging
6. Keep feature branches (don't delete) for workshop instruction purposes

### Git Safety Instructions (CRITICAL)
**ALWAYS follow these steps to prevent accidental file deletion:**

1. **Check git status before ANY branch operations**:
   ```bash
   git status  # ALWAYS run this first
   ```

2. **Preserve uncommitted files when switching branches**:
   ```bash
   # If uncommitted files exist:
   git stash push -m "Preserving work before branch switch"
   git checkout -b new-branch
   git stash pop
   ```

3. **Verify repository context**:
   ```bash
   git remote -v  # Ensure working with correct fork (rysweet/cue)
   ```

4. **Check for project-specific files**:
   - Always verify existence of: `claude.md`, `prompts/`, `.github/agents/`
   - These files may contain critical project configuration

5. **Before creating new branches**:
   - Run `git status` to check for uncommitted changes
   - Commit or stash any important files
   - Verify the base branch contains all expected files

6. **If files go missing**:
   ```bash
   # Find when files existed
   git log --all --full-history -- <missing-file-path>
   # Restore from specific commit
   git checkout <commit-hash> -- <file-path>
   ```

### Testing Strategy
- Write tests for all new features
- Maintain test coverage above 80%
- Use Playwright for E2E testing
- Test error scenarios and edge cases

### Error Handling
- Catch and log all exceptions appropriately
- Create GitHub issues for production errors
- Include stack traces and reproduction steps
- Assign issues to appropriate team members

## Reusable Agents

The repository includes specialized agents in `.github/agents/` that can be invoked for specific tasks:

### Available Agents
- **test-solver**: Specialized in fixing failing tests, particularly Playwright E2E tests. Excels at debugging cross-browser issues, timing problems, and test stability.

### Using Agents
To invoke a reusable agent, use the following pattern:
```
/agent:test-solver

Context: [Provide specific context about the problem]
Requirements: [What needs to be achieved]
```

### Creating New Agents
New specialized agents can be added to `.github/agents/` following the existing template structure. Each agent should have clear specialization, documented approaches, and success metrics.

## Additional Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [D3.js Documentation](https://d3js.org/)
- [Playwright Documentation](https://playwright.dev/docs/intro)