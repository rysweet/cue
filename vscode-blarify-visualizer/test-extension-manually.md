# Manual Testing Guide for Extension Behavior

To manually verify the extension behavior:

1. Open VS Code Insiders
2. Open the Output panel (View > Output)
3. Select "Blarify Visualizer" from the dropdown
4. Reload the window (Cmd+R) to trigger extension activation

## Expected Output Sequence:

You should see logs in this order:
1. "=== Blarify Visualizer extension activation started ==="
2. "Running setup tasks..."
3. "Starting Neo4j..." (happening in parallel with setup)
4. Either:
   - "Setup tasks completed"
   - "Neo4j started successfully"
5. Then the other one completes
6. Only after BOTH are done: "Prompting for initial analysis..."
7. The prompt dialog appears

## What to Look For:

✅ The prompt should NOT appear until you see both:
- "Setup tasks completed"
- "Neo4j started successfully"

❌ If you see "Prompting for initial analysis..." before both tasks complete, the fix isn't working

## Current Implementation:

The extension now:
1. Runs setup tasks and Neo4j startup in parallel
2. Tracks completion of both via `setupState`
3. Only shows the analysis prompt when `canPromptForAnalysis()` returns true (both complete)