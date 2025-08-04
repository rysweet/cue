# Neo4j Container Management for Blarify

## Problem Statement

Currently, users of Blarify's MCP server and VS Code extension must manually manage Neo4j containers, including:
- Starting/stopping containers
- Managing port conflicts
- Ensuring data persistence
- Handling different environments (dev/test/prod)

This creates friction for end users and complicates testing. Neo4j should be an implementation detail that "just works" transparently.

## Feature Overview

Create a robust Neo4j container management system that:
1. **Automatically manages container lifecycle** - starts when needed, stops when not
2. **Uses dynamic port allocation** - avoids conflicts with other services
3. **Persists data across sessions** - using Docker volumes
4. **Isolates test environments** - separate containers/data for testing
5. **Supports data import/export** - for backup and migration
6. **Works transparently** - users never need to know about the container

## Technical Requirements

### Core Dependencies
- Docker/Dockerode for container management
- Port-finder or similar for dynamic port allocation
- Neo4j 5.x Community Edition image
- File system operations for data export/import
- Process lifecycle hooks for cleanup

### Architecture Requirements
- Single responsibility: Neo4j lifecycle management only
- Reusable by both MCP server and VS Code extension
- Environment-aware (development, test, production)
- Graceful shutdown handling
- Automatic recovery from crashes

## Implementation Plan

### Phase 1: Core Container Manager
Create `neo4j-container-manager/` package with:

```
neo4j-container-manager/
├── src/
│   ├── index.ts              # Main exports
│   ├── container-manager.ts   # Core container lifecycle
│   ├── port-manager.ts       # Dynamic port allocation
│   ├── volume-manager.ts     # Data persistence management
│   ├── data-manager.ts       # Import/export functionality
│   └── types.ts              # TypeScript interfaces
├── tests/
│   ├── container-manager.test.ts
│   ├── port-manager.test.ts
│   └── integration.test.ts
├── package.json
├── tsconfig.json
└── README.md
```

### Phase 2: Container Lifecycle Management

```typescript
interface Neo4jContainerConfig {
  environment: 'development' | 'test' | 'production';
  dataPath?: string;  // Custom data directory
  password: string;
  username?: string;  // Default: neo4j
  plugins?: string[]; // e.g., ['apoc', 'graph-data-science']
  memory?: string;    // e.g., '2G'
}

interface Neo4jContainerInstance {
  uri: string;        // bolt://localhost:XXXXX
  httpUri: string;    // http://localhost:XXXXX
  containerId: string;
  volume: string;     // Volume name for data persistence
  stop(): Promise<void>;
  isRunning(): Promise<boolean>;
  exportData(path: string): Promise<void>;
  importData(path: string): Promise<void>;
}

class Neo4jContainerManager {
  async start(config: Neo4jContainerConfig): Promise<Neo4jContainerInstance>;
  async stop(containerId: string): Promise<void>;
  async stopAll(): Promise<void>;
  async list(): Promise<Neo4jContainerInstance[]>;
  async cleanup(keepDays: number = 7): Promise<void>; // Clean old test containers
}
```

### Phase 3: Dynamic Port Management
- Use port-finder to get available ports (7474+n, 7687+n)
- Track allocated ports in a lock file
- Release ports on container stop
- Handle port conflicts gracefully

### Phase 4: Data Persistence
- Create named volumes based on environment and timestamp
- Volume naming: `cue-neo4j-{env}-{timestamp}`
- Automatic volume reuse for same environment
- Volume backup before risky operations

### Phase 5: Test Isolation
- Test containers use prefix: `cue-neo4j-test-{uuid}`
- Test volumes auto-cleanup after test run
- Parallel test support with unique containers
- Mock mode for unit tests (no real Docker)

### Phase 6: Import/Export
- Export to compressed tar.gz format
- Include metadata (Neo4j version, export date, schema)
- Import with validation and compatibility check
- Support for incremental exports

### Phase 7: Process Lifecycle Integration
- Register shutdown handlers for clean container stop
- Handle VS Code extension deactivation
- Handle process signals (SIGINT, SIGTERM)
- Implement health checks and auto-recovery

## Testing Strategy

### Unit Tests
- Mock Docker API for container operations
- Test port allocation logic
- Test volume naming and management
- Test configuration validation

### Integration Tests
- Real Docker container creation/destruction
- Data persistence across restarts
- Port conflict resolution
- Import/export with real data

### End-to-End Tests
- VS Code extension integration
- MCP server integration
- Multi-environment scenarios
- Crash recovery testing

## Configuration Examples

### VS Code Extension Usage
```typescript
// In extension activation
const neo4jManager = new Neo4jContainerManager();
const instance = await neo4jManager.start({
  environment: 'development',
  password: config.get('neo4j.password'),
  plugins: ['apoc']
});

// In extension deactivation
await instance.stop();
```

### MCP Server Usage
```typescript
// In server startup
const instance = await neo4jManager.start({
  environment: process.env.NODE_ENV as any || 'development',
  password: process.env.NEO4J_PASSWORD,
  dataPath: process.env.NEO4J_DATA_PATH
});

// Register cleanup
process.on('SIGINT', async () => {
  await instance.stop();
  process.exit(0);
});
```

### Test Usage
```typescript
let testInstance: Neo4jContainerInstance;

beforeEach(async () => {
  testInstance = await neo4jManager.start({
    environment: 'test',
    password: 'test-password'
  });
});

afterEach(async () => {
  await testInstance.stop();
});
```

## Success Criteria

1. **Zero user configuration** - Neo4j "just works" out of the box
2. **No port conflicts** - Dynamic allocation prevents conflicts
3. **Data persistence** - Graph data survives restarts
4. **Clean test isolation** - Tests never affect dev/prod data
5. **Graceful shutdown** - No orphaned containers
6. **Fast startup** - Container reuse when possible
7. **Reliable recovery** - Handles crashes and restarts
8. **Easy data management** - Simple import/export commands

## Implementation Notes

1. **Container Naming Convention**:
   - Development: `cue-neo4j-dev`
   - Test: `cue-neo4j-test-{uuid}`
   - Production: `cue-neo4j-prod`

2. **Volume Naming Convention**:
   - Development: `cue-neo4j-dev-data`
   - Test: `cue-neo4j-test-{uuid}-data`
   - Production: `cue-neo4j-prod-data`

3. **Port Allocation Strategy**:
   - Start from base ports (7474, 7687)
   - Increment by 10 for each instance
   - Track in `~/.cue/ports.json`

4. **Health Check Implementation**:
   - Wait for Neo4j to be fully ready
   - Verify bolt and HTTP endpoints
   - Retry with exponential backoff

5. **Error Handling**:
   - Graceful degradation if Docker not available
   - Clear error messages for common issues
   - Automatic cleanup of failed starts

## Error Scenarios and Recovery

1. **Docker not available**: Provide clear error message and installation instructions
2. **Port allocation failures**: Retry with different port ranges
3. **Volume mount failures**: Fall back to container-internal storage with warning
4. **Container crash**: Automatic restart with backoff
5. **Corrupted data**: Automatic backup before operations, recovery options
6. **Network issues**: Retry with timeout, clear error reporting

## Monitoring and Logging

1. **Structured logging** with levels (debug, info, warn, error)
2. **Performance metrics**: Startup time, query performance
3. **Resource monitoring**: Memory, CPU, disk usage
4. **Health dashboard**: Simple status API for monitoring
5. **Debug mode**: Verbose logging for troubleshooting

## Version Compatibility

1. **Neo4j versions**: Support 5.x, with version detection
2. **Docker API**: Compatible with Docker 20.x+
3. **Node.js**: Require Node 16+ for modern features
4. **Platform support**: Windows, macOS, Linux
5. **Architecture**: amd64 and arm64 (Apple Silicon)

## Migration Strategy

For existing users with manual Neo4j setups:
1. **Detection**: Check for existing Neo4j containers
2. **Migration wizard**: Guided data migration
3. **Backup**: Automatic backup of existing data
4. **Validation**: Verify data integrity post-migration
5. **Rollback**: Keep old setup for 7 days

## Development Approach

1. **Create GitHub issue** describing the feature
2. **Create feature branch**: `feature/neo4j-container-management`
3. **Implement incrementally** with tests for each phase
4. **Document usage** in README with examples
5. **Create pull request** with comprehensive description
6. **Update dependent projects** (MCP server, VS Code extension)

This component will provide a reliable foundation for all Neo4j operations in the Blarify ecosystem, making the graph database truly transparent to end users.