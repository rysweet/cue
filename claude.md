# AI Assistant Instructions

This file combines generic Claude Code best practices with project-specific instructions for the AI-SIP workshop repository.

⚠️ **FIRST ACTION**: Check and update `.github/Memory.md` ! ⚠️

---

## CRITICAL: Workflow Execution Pattern

**For ANY development task that requires multiple phases (issue, branch, code, PR):**

1. **DO NOT manually execute workflow phases**
2. **ALWAYS invoke WorkflowMaster**: 
   ```
   /agent:workflow-master
   
   Task: Execute workflow for /prompts/[prompt-file].md
   ```
3. **Let WorkflowMaster handle**:
   - Issue creation
   - Branch management  
   - Implementation tracking
   - PR creation
   - Code review invocation (Phase 9)
   - State management

**Only execute manual steps for**:
- Quick fixes that don't need full workflow
- Investigations or analysis
- Direct user requests for specific actions

**Before ANY development task, ask yourself**:
- Does this need an issue? → Use WorkflowMaster
- Does this need a branch? → Use WorkflowMaster  
- Does this need a PR? → Use WorkflowMaster
- Is this a feature/fix? → Use WorkflowMaster

---

## Generic Claude Code Instructions

The following section contains universal best practices applicable to any Claude Code project.

<!-- START: claude-generic-instructions.md -->

# Claude Code Generic Instructions

## Required Context

**CRITICAL - MUST DO AT START OF EVERY SESSION**: 
1. **READ** `.github/Memory.md` for current context
2. **UPDATE** `.github/Memory.md` after completing any significant task
3. **COMMIT** Memory.md changes regularly to preserve context

**Memory.md is your persistent brain across sessions - USE IT!**

## Using GitHub CLI for Issue and PR Management

**IMPORTANT**: When creating issues, PRs, or comments using `gh` CLI, always include a note that the action was performed by an AI agent on behalf of the repository owner. Add "*Note: This [issue/PR/comment] was created by an AI agent on behalf of the repository owner.*" to the body.

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
- Maintain documentation files with up-to-date instructions and context
- Document all major decisions and architectural choices
- Include examples and edge cases in documentation

### 2. Structured Task Management
- Break down complex features into smaller, manageable tasks
- Use GitHub issues to track all work items
- Create detailed implementation plans before coding

### 3. Iterative Improvement
- Start with a working prototype and iterate
- Use test-driven development when possible
- Course-correct early based on test results

### 4. Context Management
- Use `/clear` command to reset context when switching tasks
- Keep focused on one feature at a time
- Reference specific files when discussing code changes

### 5. Subagents
- Subagents are documented at https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Utilize specialized agents for repetitive tasks
- Create new agents for common patterns or issues
- Document agent capabilities and usage patterns
- Subagents can be used to pass scoped or limited context to specialized agents for focused tasks

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
- Propose improvements to documentation
- Update relevant sections to prevent recurrence
- Add new best practices based on learnings

### Continuous Improvement
- Update documentation with new patterns discovered
- Add commonly used commands
- Document project-specific conventions
- Include solutions to recurring problems

## Git Workflow Best Practices

### General Git Workflow
1. **Always fetch latest before creating branches**: `git fetch origin && git reset --hard origin/main`
2. Create feature branches from main: `feature-<issue-number>-description`
3. Make atomic commits with clear messages
4. Always create PRs for code review
5. Ensure CI/CD passes before merging

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
   git remote -v  # Ensure working with correct repository
   ```

4. **Before creating new branches**:
   - Run `git status` to check for uncommitted changes
   - Commit or stash any important files
   - Verify the base branch contains all expected files

5. **If files go missing**:
   ```bash
   # Find when files existed
   git log --all --full-history -- <missing-file-path>
   # Restore from specific commit
   git checkout <commit-hash> -- <file-path>
   ```

## Using and Creating Reusable Agents

### Using Agents
To invoke a reusable agent, use the following pattern:
```
/agent:[agent-name]

Context: [Provide specific context about the problem]
Requirements: [What needs to be achieved]
```

### Creating New Agents
New specialized agents can be added to `.github/agents/` or `.claude/agents/` following the existing template structure. Each agent should have:
- Clear specialization and purpose
- Documented approaches and methods
- Success metrics and validation criteria
- Required tools listed in frontmatter

## Git Guidelines

### Git Workflow Rules
- **Never commit directly to main**
- **Use meaningful commit messages**
- **Include co-authorship for AI-generated commits**:
  ```
  🤖 Generated with [Claude Code](https://claude.ai/code)
  
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

<!-- END: claude-generic-instructions.md -->

---

## Project-Specific Instructions

The following section contains instructions specific to the AI-SIP workshop repository.

<!-- START: claude-project-specific.md -->

# AI-SIP Workshop Project-Specific Instructions

## Overview

This repository contains a sample JavaScript application used in the AI-SIP (AI-enhanced Software development In Practice) workshop. The application visualizes file system structures as an interactive graph using D3.js, providing a hands-on environment for demonstrating AI-assisted development workflows, debugging practices, and automated issue management.

The workshop focuses on:
- Leveraging AI tools like Claude Code and GitHub Copilot for efficient development
- Implementing test-driven development with AI assistance
- Creating automated error handling and issue creation workflows
- Building visual debugging and annotation features

## Project-Specific Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use ES6+ JavaScript features
- Maintain consistent indentation (2 spaces)
- Add meaningful variable and function names

### Workshop-Specific Git Practices
- Keep feature branches (don't delete) for workshop instruction purposes
- Use descriptive branch names that help workshop attendees understand the progression

### Project-Specific Files to Verify
- Always verify existence of: `CLAUDE.md`, `prompts/`, `.github/agents/`
- These files may contain critical project configuration
- The repository should be: `rysweet/cue`

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

## Available Project Agents
- **test-solver**: Specialized in fixing failing tests, particularly Playwright E2E tests. Excels at debugging cross-browser issues, timing problems, and test stability.

## Visual-First Development
- Use screenshots and mockups to guide implementation
- Test UI changes visually using the Playwright MCP service
- Capture and annotate screenshots for bug reports

## Technology Stack Resources
- [Neo4j Documentation](https://neo4j.com/docs/)
- [D3.js Documentation](https://d3js.org/)
- [Playwright Documentation](https://playwright.dev/docs/intro)

## Project Structure
This is a JavaScript/TypeScript project with:
- D3.js for graph visualization
- Neo4j for graph database
- Playwright for E2E testing
- GitHub Actions for CI/CD

## Workshop Context
This repository serves as a teaching tool for AI-enhanced development practices. When making changes:
- Consider the educational value of the implementation
- Document the AI assistance process
- Create clear examples for workshop participants
- Maintain progression of complexity across branches

<!-- END: claude-project-specific.md -->

---

## Additional Notes

This file uses a manual include approach for maintainability. When updating:
1. Edit the source files (`claude-generic-instructions.md` or `claude-project-specific.md`)
2. Copy the updated content between the START/END markers in this file
3. Consider automating this process with a simple script if frequent updates are needed

For other projects adopting these practices:
1. Copy `claude-generic-instructions.md` to your project
2. Create your own project-specific instructions
3. Combine them using this template or a build process