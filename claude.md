# AI Assistant Instructions

This file combines generic Claude Code best practices with project-specific instructions for the AI-SIP workshop repository.

⚠️ **FIRST ACTION**: Check and update @.github/Memory.md ! ⚠️

⚠️ **SECOND ACTION**: When working on Claude agents or instructions, read https://docs.anthropic.com/en/docs/claude-code/memory ! ⚠️

---

## CRITICAL: Workflow Execution Pattern

**For ANY development task that requires multiple phases (issue, branch, code, PR):**

1. **DO NOT manually execute workflow phases**
2. **Use the proper agent hierarchy**:
   
   **For multiple tasks or when parallelization is possible**:
   ```
   /agent:orchestrator-agent
   
   Execute these specific prompts in parallel:
   - prompt-file-1.md
   - prompt-file-2.md
   ```
   
   **For single sequential tasks**:
   ```
   /agent:workflow-master
   
   Task: Execute workflow for /prompts/[prompt-file].md
   ```

3. **Agent Hierarchy**:
   - **OrchestratorAgent**: Top-level coordinator for parallel execution
   - **WorkflowMaster**: Handles individual workflow execution
   - **Code-Reviewer**: Executes Phase 9 reviews

4. **Automated Workflow Handling**:
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
- Multiple related tasks? → Use OrchestratorAgent
- Single complex task? → Use WorkflowMaster
- Need an issue/branch/PR? → Use agents, not manual execution

---

## Generic Claude Code Instructions

See gadugi repository for generic Claude Code best practices and instructions.

## Project-Specific Instructions

@claude-project-specific.md

## Agent Management

Most agents are now managed via the gadugi repository. The agent-manager itself must remain local to manage synchronization.

To update agents from gadugi:
1. Run `/agent:agent-manager check-and-update-agents`
2. Or manually sync: `/agent:agent-manager sync gadugi`

Available agents from gadugi:
- workflow-master
- orchestrator-agent
- code-reviewer
- code-review-response
- prompt-writer
- task-analyzer
- worktree-manager
- execution-monitor

Local agents:
- agent-manager (required for synchronization)
