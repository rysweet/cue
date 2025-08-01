# Fix VS Code Extension BlarifyIntegration Command Mismatch

## Overview

This prompt addresses a critical integration issue in the VS Code Blarify Visualizer extension where the BlarifyIntegration class attempts to execute a non-existent 'ingest' command. Instead of using command-line arguments, the bundled Blarify version expects to be invoked with environment variables. This mismatch causes workspace analysis to fail, preventing users from visualizing their codebase graphs.

## Problem Statement

### Current Issue
The VS Code extension's `BlarifyIntegration.ts` class is configured to call Blarify using:
```bash
python main.py ingest <workspace_path> --json [additional_args]
```

However, the bundled Blarify version doesn't recognize the 'ingest' command and instead expects to be invoked with environment variables like `ROOT_PATH`.

### Impact
- Workspace analysis fails completely
- Users cannot generate codebase visualizations
- Error messages are confusing and don't clearly indicate the root cause
- The extension appears broken to end users

### Evidence from Codebase
- `blarifyIntegration.ts:45` shows: `const args = ['ingest', workspacePath, '--json'];`
- Test files `test-blarify-extension-style.js` and `test-blarify-no-llm.js` demonstrate the correct environment variable approach
- Working pattern: `ROOT_PATH=<path>` with no command-line arguments

## Feature Requirements

### Functional Requirements
1. **Environment Variable Integration**: Replace command-line arguments with environment variables
2. **Configuration Mapping**: Map VS Code extension settings to Blarify environment variables
3. **Backward Compatibility**: Ensure the change doesn't break existing functionality
4. **Error Handling**: Provide clear error messages for integration failures
5. **Progress Reporting**: Maintain existing progress reporting mechanisms

### Technical Requirements
1. **Environment Variable Support**: 
   - `ROOT_PATH`: Workspace path to analyze
   - `NEO4J_URI`: Database connection string
   - `NEO4J_USER`: Database username  
   - `NEO4J_PASSWORD`: Database password
   - `AZURE_API_KEY`, `AZURE_ENDPOINT`, `AZURE_DEPLOYMENT`: LLM configuration
   - `ENABLE_LLM_DESCRIPTIONS`: Boolean flag for LLM features
   - `ENABLE_DOCUMENTATION_NODES`: Boolean flag for documentation analysis
   - `NAMES_TO_SKIP`: Comma-separated list of patterns to exclude

2. **Process Execution**: 
   - Remove command-line arguments except for main.py path
   - Pass all configuration through environment variables
   - Maintain working directory and Python path setup

3. **Configuration Integration**:
   - Map `ConfigurationManager` settings to environment variables
   - Handle Azure OpenAI configuration
   - Support exclude patterns from VS Code settings

### Integration Requirements
- Maintain existing `BlarifyIntegration` public API
- Preserve error handling and cancellation support
- Keep progress reporting functionality intact
- Ensure Python environment setup remains unchanged

## Technical Analysis

### Current Implementation Analysis
The current `BlarifyIntegration.analyzeWorkspace()` method:
1. Sets up Python environment correctly ✅
2. Builds command-line arguments incorrectly ❌
3. Spawns process with proper environment setup ✅
4. Handles output parsing correctly ✅

### Root Cause
Line 45 in `blarifyIntegration.ts`:
```typescript
const args = ['ingest', workspacePath, '--json'];
```

This should be replaced with environment variable configuration.

### Working Pattern Analysis
From `test-blarify-extension-style.js`:
```javascript
const child = spawn(pythonPath, [mainPath], {
    cwd: testDir,
    env: {
        ...process.env,
        PYTHONPATH: blarifyPath,
        ROOT_PATH: testDir,
        NEO4J_URI: 'bolt://localhost:7957',
        NEO4J_USER: 'neo4j',
        NEO4J_PASSWORD: 'test-password'
    }
});
```

### Dependencies and Integration Points
1. **ConfigurationManager**: Provides Azure OpenAI settings and exclude patterns
2. **PythonEnvironment**: Handles Python path resolution (unchanged)
3. **Process Spawning**: Child process creation and management (updated)
4. **Neo4j Integration**: Database connection details (unchanged)

## Implementation Plan

### Phase 1: Environment Variable Mapping (2-3 hours)
**Objective**: Replace command-line arguments with environment variables

**Deliverables**:
1. Update `BlarifyIntegration.analyzeWorkspace()` method
2. Create environment variable mapping function
3. Remove command-line argument construction

**Tasks**:
- Remove `args` array construction logic
- Create `buildEnvironmentVariables()` private method
- Map configuration settings to environment variables
- Update process spawn call to use only `[mainPath]` arguments

### Phase 2: Configuration Integration (1-2 hours)
**Objective**: Ensure all VS Code settings are properly passed through environment variables

**Deliverables**:
1. Azure OpenAI configuration mapping
2. Exclude patterns handling
3. Documentation nodes toggle support

**Tasks**:
- Map Azure OpenAI config to `AZURE_*` environment variables
- Convert exclude patterns array to `NAMES_TO_SKIP` comma-separated string
- Add `ENABLE_DOCUMENTATION_NODES` environment variable
- Handle LLM descriptions toggle with `ENABLE_LLM_DESCRIPTIONS`

### Phase 3: Testing and Validation (1-2 hours)
**Objective**: Verify the integration works correctly

**Deliverables**:
1. Updated unit tests
2. Integration test validation
3. Error handling verification

**Tasks**:
- Update existing tests to expect environment variables
- Add test cases for configuration mapping
- Verify error messages are clear and helpful
- Test cancellation and progress reporting

## Testing Requirements

### Unit Testing Strategy
1. **Environment Variable Construction**:
   - Test `buildEnvironmentVariables()` method
   - Verify Azure OpenAI configuration mapping
   - Test exclude patterns conversion
   - Validate boolean flag handling

2. **Process Execution**:
   - Mock spawn calls to verify environment variables
   - Test error handling for missing configuration
   - Verify progress reporting continues to work

3. **Configuration Integration**:
   - Test with various ConfigurationManager settings
   - Verify default values are handled correctly
   - Test edge cases (empty exclude patterns, missing Azure config)

### Integration Testing
1. **End-to-End Workspace Analysis**:
   - Test with real workspace using bundled Blarify
   - Verify JSON output parsing continues to work
   - Test cancellation functionality

2. **Configuration Scenarios**:
   - Test with Azure OpenAI enabled/disabled
   - Test with various exclude patterns
   - Test with documentation nodes enabled/disabled

### Test Cases
1. **Basic Functionality**:
   - Workspace analysis with minimal configuration
   - Verify environment variables are set correctly
   - Confirm process spawns without 'ingest' command

2. **Configuration Mapping**:
   - Azure OpenAI settings -> environment variables
   - Exclude patterns -> NAMES_TO_SKIP comma-separated string
   - Boolean toggles -> environment flags

3. **Error Scenarios**:
   - Missing workspace path
   - Invalid Python environment
   - Blarify execution failures

## Success Criteria

### Functional Success Metrics
1. **Core Functionality**: Workspace analysis completes successfully without 'ingest' command
2. **Configuration Support**: All VS Code settings are properly passed to Blarify
3. **Error Handling**: Clear error messages for common failure scenarios
4. **Performance**: No regression in analysis time or resource usage

### Quality Metrics
1. **Test Coverage**: 95%+ coverage for modified code paths
2. **Code Quality**: No ESLint violations or TypeScript errors
3. **Documentation**: Updated inline comments and method documentation
4. **Maintainability**: Clean separation between configuration and execution logic

### User Experience Metrics
1. **Reliability**: Workspace analysis succeeds consistently
2. **Clarity**: Error messages guide users to resolution
3. **Performance**: Progress reporting works smoothly
4. **Configuration**: All extension settings function as expected

## Implementation Steps

### Step 1: Create GitHub Issue
Create a detailed issue with:
```markdown
Title: Fix BlarifyIntegration command mismatch - replace 'ingest' command with environment variables

Description:
The VS Code extension's BlarifyIntegration class incorrectly tries to call `blarify ingest <path>` 
but the bundled Blarify version expects environment variables instead. This causes all workspace 
analysis to fail.

Root Cause:
- Line 45 in blarifyIntegration.ts uses command: ['ingest', workspacePath, '--json']
- Bundled Blarify expects ROOT_PATH environment variable instead

Solution:
Replace command-line arguments with environment variable configuration as demonstrated 
in test-blarify-extension-style.js

Acceptance Criteria:
- [ ] Remove 'ingest' command from args array
- [ ] Map all configuration to environment variables
- [ ] Maintain existing progress reporting and error handling
- [ ] Update tests to reflect new integration pattern
- [ ] Verify workspace analysis works end-to-end
```

Labels: `bug`, `integration`, `high-priority`
Assignee: AI Agent
Milestone: Next Release

### Step 2: Create Feature Branch
```bash
git checkout -b fix/blarify-integration-environment-variables
```

Branch naming follows pattern: `fix/blarify-integration-environment-variables`

### Step 3: Research and Analysis
- [x] Analyze current BlarifyIntegration implementation
- [x] Review working test patterns for environment variable usage
- [x] Identify all configuration points that need mapping
- [x] Document the required environment variables

### Step 4: Implementation Phase 1 - Core Environment Variable Support
**Files to modify**: 
- `src/blarifyIntegration.ts`

**Changes**:
1. **Remove command-line arguments**:
   ```typescript
   // OLD: const args = ['ingest', workspacePath, '--json'];
   // NEW: const args = []; // Only main.py path in spawn call
   ```

2. **Add environment variable builder**:
   ```typescript
   private buildEnvironmentVariables(
       workspacePath: string,
       azureConfig: any,
       excludePatterns: string[]
   ): NodeJS.ProcessEnv {
       return {
           ...process.env,
           PYTHONPATH: path.join(this.extensionPath, 'bundled'),
           ROOT_PATH: workspacePath,
           NEO4J_URI: 'bolt://localhost:7957', // From Neo4j manager
           NEO4J_USER: 'neo4j',
           NEO4J_PASSWORD: 'password', // From configuration
           ENABLE_DOCUMENTATION_NODES: 'true',
           ...(azureConfig.apiKey && {
               ENABLE_LLM_DESCRIPTIONS: 'true',
               AZURE_API_KEY: azureConfig.apiKey,
               AZURE_ENDPOINT: azureConfig.endpoint,
               AZURE_DEPLOYMENT: azureConfig.deploymentName
           }),
           ...(excludePatterns.length > 0 && {
               NAMES_TO_SKIP: excludePatterns.join(',')
           })
       };
   }
   ```

3. **Update process spawn**:
   ```typescript
   // OLD: const blarify = spawn(pythonPath, [blarifyMainPath, ...args], {
   // NEW: const blarify = spawn(pythonPath, [blarifyMainPath], {
       cwd: workspacePath,
       env: this.buildEnvironmentVariables(workspacePath, azureConfig, excludePatterns)
   // });
   ```

### Step 5: Implementation Phase 2 - Neo4j Integration
**Files to modify**:
- `src/blarifyIntegration.ts`
- Coordinate with Neo4j manager for connection details

**Changes**:
1. **Get Neo4j connection details**:
   ```typescript
   // Add method to get Neo4j configuration from manager
   private async getNeo4jConfig(): Promise<{uri: string, user: string, password: string}> {
       // Coordinate with Neo4jManager to get connection details
       // This may require updating constructor to accept Neo4jManager instance
   }
   ```

2. **Update environment variable builder**:
   ```typescript
   const neo4jConfig = await this.getNeo4jConfig();
   return {
       ...baseEnv,
       NEO4J_URI: neo4jConfig.uri,
       NEO4J_USER: neo4jConfig.user,
       NEO4J_PASSWORD: neo4jConfig.password
   };
   ```

### Step 6: Implementation Phase 3 - Testing Updates
**Files to modify**:
- `src/test/suite/extension.test.ts`
- `src/test/suite/blarifyPathResolution.test.ts`
- Any other test files that mock BlarifyIntegration

**Changes**:
1. **Update spawn mocks**:
   ```typescript
   // Update mocks to expect environment variables instead of command args
   sinon.stub(childProcess, 'spawn').callsFake((command, args, options) => {
       // Verify args only contains main.py path
       assert.strictEqual(args.length, 1);
       assert.ok(args[0].endsWith('main.py'));
       
       // Verify environment variables are set
       assert.strictEqual(options.env.ROOT_PATH, expectedWorkspacePath);
       assert.strictEqual(options.env.ENABLE_DOCUMENTATION_NODES, 'true');
       
       // Return mock process
       return mockProcess;
   });
   ```

2. **Add environment variable tests**:
   ```typescript
   test('buildEnvironmentVariables should include all required variables', () => {
       const envVars = blarifyIntegration.buildEnvironmentVariables(
           '/test/path',
           { apiKey: 'test-key', endpoint: 'test-endpoint', deploymentName: 'test-deployment' },
           ['node_modules', '.git']
       );
       
       assert.strictEqual(envVars.ROOT_PATH, '/test/path');
       assert.strictEqual(envVars.ENABLE_LLM_DESCRIPTIONS, 'true');
       assert.strictEqual(envVars.AZURE_API_KEY, 'test-key');
       assert.strictEqual(envVars.NAMES_TO_SKIP, 'node_modules,.git');
   });
   ```

### Step 7: Documentation Updates
**Files to modify**:
- `src/blarifyIntegration.ts` (inline comments)
- `EXTENSION-TROUBLESHOOTING.md` (if needed)

**Changes**:
1. **Update method documentation**:
   ```typescript
   /**
    * Analyzes the workspace using Blarify with environment variable configuration.
    * 
    * Blarify is invoked using environment variables instead of command-line arguments:
    * - ROOT_PATH: The workspace path to analyze
    * - NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD: Database connection
    * - AZURE_*: LLM configuration if enabled
    * - NAMES_TO_SKIP: Comma-separated exclude patterns
    * - ENABLE_*: Feature toggles
    */
   ```

2. **Add troubleshooting notes**:
   ```markdown
   ## Environment Variable Configuration
   
   The extension now uses environment variables instead of command-line arguments:
   - Verify ROOT_PATH is set to workspace directory
   - Check Neo4j connection variables are correct
   - Ensure Azure configuration is passed through environment
   ```

### Step 8: End-to-End Testing
**Test scenarios**:
1. **Clean installation test**: Fresh extension install and workspace analysis
2. **Configuration variations**: Test with/without Azure OpenAI, different exclude patterns
3. **Error handling**: Test with invalid workspace paths, missing dependencies
4. **Cancellation**: Verify process cancellation still works correctly

**Validation**:
```bash
# Package and install updated extension
npm run compile
npm run package
code-insiders --install-extension blarify-visualizer-0.1.0.vsix --force

# Test in clean workspace
mkdir -p /tmp/test-workspace
cd /tmp/test-workspace
echo "console.log('test');" > test.js
code-insiders --new-window .

# Run blarifyVisualizer.ingestWorkspace command
# Verify it completes without 'ingest' command errors
```

### Step 9: Create Pull Request
**PR Title**: Fix BlarifyIntegration command mismatch - replace 'ingest' with environment variables

**PR Description**:
```markdown
## Problem
The VS Code extension's BlarifyIntegration was calling `blarify ingest <path>` but the bundled 
Blarify version doesn't support the 'ingest' command. Instead, it expects configuration through
environment variables.

## Solution
- Removed command-line arguments from BlarifyIntegration
- Added environment variable mapping for all configuration
- Updated process spawning to use environment variables only
- Maintained all existing functionality (progress reporting, error handling, cancellation)

## Changes
- `src/blarifyIntegration.ts`: Core integration fix with environment variables
- Tests updated to reflect new integration pattern
- Documentation updated with new configuration approach

## Testing
- [x] Unit tests pass with environment variable mocking
- [x] Integration tests verify end-to-end workspace analysis
- [x] Manual testing confirms workspace analysis works
- [x] Error handling and cancellation verified

## Breaking Changes
None - public API remains unchanged

## AI Agent Attribution
This PR was created by Claude Code AI agent following the fix-vscode-blarify-integration-command-mismatch.md prompt.

Fixes #[issue-number]
```

### Step 10: Code Review
Invoke code-reviewer sub-agent:
```markdown
/agent:code-reviewer

Please review the BlarifyIntegration environment variable fix PR. Focus on:
1. Correct environment variable mapping
2. Maintained error handling and progress reporting
3. Test coverage for new configuration approach
4. Integration with existing Neo4j and configuration systems
```

## Verification Steps

### Pre-Implementation Verification
- [ ] Current implementation fails with 'ingest' command not found
- [ ] Test files demonstrate working environment variable pattern
- [ ] All configuration points identified and documented

### Post-Implementation Verification
- [ ] Workspace analysis completes successfully
- [ ] All VS Code settings are passed through environment variables
- [ ] Progress reporting continues to work
- [ ] Error handling provides clear messages
- [ ] Cancellation functionality preserved
- [ ] Tests pass with new environment variable approach
- [ ] No regression in analysis performance or output quality

### Integration Verification
- [ ] Neo4j connection details properly passed
- [ ] Azure OpenAI configuration mapped correctly
- [ ] Exclude patterns converted to comma-separated format
- [ ] Documentation nodes toggle works via environment variable
- [ ] Python environment setup unchanged and working

This prompt provides comprehensive guidance for fixing the critical BlarifyIntegration command mismatch issue by replacing the non-existent 'ingest' command with proper environment variable configuration, ensuring the VS Code extension can successfully analyze workspaces using the bundled Blarify version.