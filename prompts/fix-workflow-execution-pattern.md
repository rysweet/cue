# Fix Workflow Execution Pattern

## Problem Statement

The AI assistant is manually executing workflow phases (creating issues, branches, PRs) instead of invoking the WorkflowMaster sub-agent. This leads to:
- Phase 9 (code review) being skipped
- No state tracking
- Inconsistent workflow execution
- Manual steps prone to omission

## Root Cause

The AI assistant is treating WorkflowMaster documentation as a manual checklist rather than invoking the actual WorkflowMaster agent to orchestrate the workflow.

## Solution

### 1. Update CLAUDE.md with Explicit Workflow Instructions

Add a new section that makes it crystal clear when and how to use WorkflowMaster:

```markdown
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
```

### 2. Create Workflow Enforcement Checklist

Before starting any multi-phase task, the AI should ask itself:
- Does this task need an issue? → Use WorkflowMaster
- Does this task need a branch? → Use WorkflowMaster
- Does this task need a PR? → Use WorkflowMaster
- Is this a complete feature/fix? → Use WorkflowMaster

### 3. Add Pre-Task Validation

Create a mental model that triggers before any development work:

```
IF task involves (issue OR branch OR PR OR multiple files) THEN
    MUST use WorkflowMaster
ELSE
    Can proceed manually
END IF
```

## Implementation Steps

1. Update CLAUDE.md with the new workflow execution section
2. Add clear examples of when to use WorkflowMaster
3. Create a "common mistakes" section highlighting manual execution
4. Test with next task to ensure WorkflowMaster is invoked

## Success Criteria

- [ ] Next development task uses WorkflowMaster
- [ ] Phase 9 (code review) executes automatically
- [ ] State tracking works properly
- [ ] No manual workflow execution unless explicitly justified

## Example Correct Usage

```
User: "Please implement feature X"

AI: "I'll use WorkflowMaster to execute this feature development."

/agent:workflow-master

Task: Execute workflow for feature X
Prompt: /prompts/feature-x.md (or create prompt first if needed)
```

## Common Mistakes to Avoid

❌ Creating issue manually with `gh issue create`
❌ Creating branch manually with `git checkout -b`
❌ Creating PR manually with `gh pr create`
❌ Forgetting Phase 9 code review

✅ Using `/agent:workflow-master` for all multi-phase tasks
✅ Letting WorkflowMaster handle the entire workflow
✅ Only intervening if WorkflowMaster encounters errors