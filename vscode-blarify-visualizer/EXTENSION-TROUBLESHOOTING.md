# VS Code Extension Troubleshooting Workflow

This document outlines the comprehensive troubleshooting workflow for debugging VS Code extensions, particularly focusing on runtime issues, logging, and testing strategies.

## Table of Contents
- [Development Cycle](#development-cycle)
- [Testing Strategies](#testing-strategies)
- [Logging and Diagnostics](#logging-and-diagnostics)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Tools and Scripts](#tools-and-scripts)

## Development Cycle

### 1. Code Changes
When making changes to fix issues:

```bash
# Edit the source files
vim src/neo4jManager.ts

# Compile TypeScript
npm run compile

# Package the extension
npm run package

# Install the extension
code-insiders --install-extension blarify-visualizer-0.1.0.vsix --force
```

### 2. Clean Testing Environment
Always ensure a clean test environment:

```bash
# Remove existing containers
docker ps -a --filter name=blarify-visualizer --format "{{.ID}}" | xargs -r docker rm -f

# Remove existing volumes (critical for authentication issues)
docker volume ls --filter name=blarify --format "{{.Name}}" | xargs -r docker volume rm
```

## Testing Strategies

### 1. New Window Testing Script
Created `test-vscode-new-window.sh` to test extensions in isolated environments:

```bash
#!/bin/bash
# Creates a temporary workspace and launches VS Code
TEMP_DIR=$(mktemp -d /tmp/blarify-test-workspace-XXXXX)
code-insiders --new-window --verbose "$TEMP_DIR"

# Monitor Docker containers
while true; do
    container=$(docker ps --filter name=blarify-visualizer-development --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")
    if [ ! -z "$container" ]; then
        echo "✅ Neo4j container detected:"
        echo "$container"
        # Test HTTP endpoint
        port=$(docker ps --filter name=blarify-visualizer-development --format "{{.Ports}}" | grep -oE '0\.0\.0\.0:([0-9]+)->7474' | cut -d: -f2 | cut -d- -f1)
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" | grep -q "200"; then
            echo "✅ Neo4j is accessible!"
            exit 0
        fi
    fi
    sleep 1
done
```

### 2. Direct Testing Scripts
For isolated component testing:

```javascript
// debug-neo4j-startup.js
const path = require('path');
const managerPath = path.join(__dirname, 'bundled/neo4j-container-manager');
const Neo4jContainerManager = require(managerPath);

async function testStartup() {
    const manager = new Neo4jContainerManager({
        logger: {
            info: console.log,
            error: console.error,
            warn: console.warn,
            debug: console.log
        }
    });
    
    try {
        const instance = await manager.start({
            environment: 'development',
            containerPrefix: 'blarify-visualizer',
            password: 'test-password',
            username: 'neo4j'
        });
        console.log('Success:', instance);
    } catch (error) {
        console.error('Failed:', error);
    }
}
```

## Logging and Diagnostics

### 1. Extension Output Channels
Add comprehensive logging to track execution flow:

```typescript
export class Neo4jManager {
    private outputChannel: vscode.OutputChannel;
    
    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Neo4j Manager');
    }
    
    async ensureRunning(): Promise<void> {
        this.outputChannel.appendLine(`[Neo4j] Starting container with config:`);
        this.outputChannel.appendLine(`  - Environment: ${environment}`);
        this.outputChannel.appendLine(`  - Container prefix: ${containerPrefix}`);
        this.outputChannel.appendLine(`  - Username: neo4j`);
        
        try {
            // ... operation ...
        } catch (error: any) {
            this.outputChannel.appendLine(`[Neo4j] Error: ${error.message}`);
            this.outputChannel.appendLine(`[Neo4j] Stack: ${error.stack}`);
            throw error;
        }
    }
}
```

### 2. VS Code Log Files
Access extension logs from the filesystem:

```bash
# Find VS Code logs directory
ls -la "/Users/$USER/Library/Application Support/Code - Insiders/logs/"

# Find the most recent window logs
cd "/Users/$USER/Library/Application Support/Code - Insiders/logs/"
ls -lt | head -5

# Navigate to extension output logs
cd [latest-timestamp]/window[N]/exthost/output_logging_[timestamp]/

# View extension-specific logs
cat "*-Blarify Visualizer.log"
cat "*-Neo4j Manager.log"
```

### 3. Docker Container Logs
Essential for debugging container-specific issues:

```bash
# View container logs
docker logs blarify-visualizer-development --tail 50

# Filter for specific issues
docker logs blarify-visualizer-development | grep -E "(ERROR|WARN|authentication|password)"

# Follow logs in real-time
docker logs -f blarify-visualizer-development
```

## Common Issues and Solutions

### 1. Container Already Exists Error
**Error**: "The container name is already in use"

**Solution**: Implement proper cleanup before starting:
```typescript
const { stdout: psOutput } = await execAsync(`docker ps -a --filter name=${containerName} --format "{{.ID}}"`);
if (psOutput.trim()) {
    await execAsync(`docker rm -f ${containerName}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
}
```

### 2. Authentication Failures
**Error**: "The client has provided incorrect authentication details"

**Root Cause**: Reusing volumes with different passwords

**Solution**: Remove volumes when removing containers:
```typescript
// Get volume name
const { stdout: volumeOutput } = await execAsync(
    `docker inspect ${containerName} --format '{{range .Mounts}}{{.Name}}{{end}}'`
);

// Remove volume
if (volumeOutput.trim()) {
    await execAsync(`docker volume rm ${volumeOutput.trim()}`);
}

// Also remove volumes with naming patterns
const { stdout: volumes } = await execAsync(
    `docker volume ls --format "{{.Name}}" | grep -E "^blarify-neo4j-${environment}"`
);
```

### 3. Password Persistence Issues
**Error**: Passwords not persisting across VS Code windows

**Solution**: Use correct configuration scope:
```json
// package.json
"blarifyVisualizer.neo4jPasswords": {
    "type": "object",
    "default": {},
    "description": "Neo4j container passwords",
    "scope": "application"  // Not "resource" or "workspace"
}
```

```typescript
// Save globally
await config.update('neo4jPasswords', passwords, 
    vscode.ConfigurationTarget.Global);
```

### 4. Timeout Errors
**Error**: "Neo4j failed to start within 60000ms"

**Debugging Steps**:
1. Check if container is actually running: `docker ps`
2. Check container logs: `docker logs [container-name]`
3. Verify port accessibility: `curl http://localhost:[port]`
4. Check for volume reuse issues
5. Ensure proper cleanup between attempts

## Tools and Scripts

### 1. Container Cleanup Script
```bash
#!/bin/bash
# cleanup-neo4j.sh
echo "Cleaning up Neo4j containers and volumes..."

# Stop and remove containers
docker ps -a --filter name=blarify-visualizer --format "{{.ID}}" | \
    xargs -r docker rm -f 2>/dev/null || true

# Remove volumes
docker volume ls --filter name=blarify --format "{{.Name}}" | \
    xargs -r docker volume rm 2>/dev/null || true

echo "Cleanup complete"
```

### 2. Extension Testing Checklist
- [ ] Compile TypeScript: `npm run compile`
- [ ] Run unit tests: `npm test`
- [ ] Package extension: `npm run package`
- [ ] Clean up Docker resources
- [ ] Install extension: `code-insiders --install-extension *.vsix --force`
- [ ] Test in new window: `bash test-vscode-new-window.sh`
- [ ] Check logs in Output panel
- [ ] Verify container is running: `docker ps`
- [ ] Test HTTP endpoint: `curl http://localhost:[port]`

### 3. Log Analysis Commands
```bash
# Find recent error logs
find "/Users/$USER/Library/Application Support/Code - Insiders/logs" \
    -name "*.log" -newer [reference-file] -exec grep -l "ERROR" {} \;

# Monitor extension output in real-time
tail -f "/path/to/extension/output.log"

# Search for specific errors across all logs
grep -r "Neo4j failed to start" "/Users/$USER/Library/Application Support/Code - Insiders/logs"
```

## Best Practices

1. **Always add detailed logging** - It's much easier to debug with comprehensive logs
2. **Test in isolation** - Use new VS Code windows to avoid state pollution
3. **Clean up resources** - Always remove containers AND volumes for fresh starts
4. **Check multiple log sources** - Extension output, VS Code logs, and Docker logs
5. **Use proper error handling** - Catch errors and log full stack traces
6. **Version your fixes** - Commit after each successful fix for easy rollback

## Troubleshooting Workflow Summary

1. **Reproduce the issue** in a clean environment
2. **Add logging** to trace execution flow
3. **Check all log sources** (VS Code Output, filesystem logs, Docker logs)
4. **Identify root cause** (often different from the error message)
5. **Implement fix** with proper error handling
6. **Test thoroughly** in new VS Code windows
7. **Verify logs** show expected behavior
8. **Document the solution** for future reference

This workflow has proven effective for debugging complex extension issues, particularly those involving external services like Docker containers.