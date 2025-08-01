# Neo4j Container Manager

Transparent Neo4j container lifecycle management for Blarify. This package handles all aspects of running Neo4j in Docker containers, including automatic startup/shutdown, dynamic port allocation, data persistence, and environment isolation.

## Features

- 🚀 **Automatic container lifecycle** - Starts when needed, stops when not
- 🔌 **Dynamic port allocation** - Avoids conflicts with other services  
- 💾 **Data persistence** - Uses Docker volumes across sessions
- 🧪 **Test isolation** - Separate containers and data for testing
- 📦 **Import/Export** - Backup and restore graph data
- 🛡️ **Graceful shutdown** - Handles process signals properly
- 📊 **Container monitoring** - CPU, memory, and network stats

## Installation

```bash
npm install @blarify/neo4j-container-manager
```

## Quick Start

```typescript
import { Neo4jContainerManager } from '@blarify/neo4j-container-manager';

// Create manager
const manager = new Neo4jContainerManager();

// Start Neo4j
const instance = await manager.start({
  environment: 'development',
  password: 'your-password'
});

console.log(`Neo4j running at ${instance.uri}`);

// Use the driver
const session = instance.driver.session();
try {
  await session.run('CREATE (n:Test {name: $name})', { name: 'Hello' });
} finally {
  await session.close();
}

// Stop when done
await instance.stop();
```

## Configuration

### Container Configuration

```typescript
interface Neo4jContainerConfig {
  environment: 'development' | 'test' | 'production';
  password: string;               // Required
  username?: string;              // Default: 'neo4j'
  dataPath?: string;              // Custom data directory
  plugins?: string[];             // e.g., ['apoc', 'graph-data-science']
  memory?: string;                // e.g., '2G'
  containerPrefix?: string;       // Custom container name prefix
  debug?: boolean;                // Enable debug logging
}
```

### Manager Options

```typescript
const manager = new Neo4jContainerManager({
  dataDir: '/path/to/metadata',    // Default: ~/.blarify
  dockerSocket: '/custom/docker.sock',
  debug: true,
  logger: customLogger
});
```

## Usage Examples

### VS Code Extension

```typescript
// In extension activation
export async function activate(context: vscode.ExtensionContext) {
  const manager = new Neo4jContainerManager();
  
  const instance = await manager.start({
    environment: 'development',
    password: config.get('neo4j.password'),
    plugins: ['apoc']
  });
  
  context.subscriptions.push({
    dispose: async () => {
      await instance.stop();
    }
  });
}
```

### MCP Server

```typescript
// In server startup
const instance = await manager.start({
  environment: process.env.NODE_ENV as any || 'development',
  password: process.env.NEO4J_PASSWORD!,
  memory: '4G'
});

// Register cleanup
process.on('SIGINT', async () => {
  await instance.stop();
  process.exit(0);
});
```

### Testing

```typescript
describe('Graph Operations', () => {
  let instance: Neo4jContainerInstance;
  
  beforeEach(async () => {
    instance = await manager.start({
      environment: 'test',
      password: 'test-password'
    });
  });
  
  afterEach(async () => {
    await instance.stop();
  });
  
  test('should create nodes', async () => {
    const session = instance.driver.session();
    // ... test code
  });
});
```

### Data Import/Export

```typescript
// Export data
await instance.exportData('/backups/graph-backup.tar.gz');

// Import data with validation
await instance.importData('/backups/graph-backup.tar.gz', {
  validate: true,
  backup: true,  // Create backup before import
  force: false   // Don't import if versions mismatch
});
```

### Container Management

```typescript
// List all running containers
const containers = await manager.list();

// Stop all containers
await manager.stopAll();

// Clean up old test containers (older than 7 days)
await manager.cleanup(7);

// Get container stats
const stats = await instance.getStats();
console.log(`Memory: ${stats.memoryUsage / 1024 / 1024}MB`);
console.log(`CPU: ${stats.cpuUsage}%`);
```

## Environment Isolation

The manager automatically isolates environments:

- **Development**: Persistent container and volume (`blarify-neo4j-dev`)
- **Test**: Unique containers with auto-cleanup (`blarify-neo4j-test-{uuid}`)
- **Production**: Persistent with extra safeguards (`blarify-neo4j-prod`)

## Port Management

Ports are dynamically allocated to avoid conflicts:

- Base ports: 7474 (HTTP), 7687 (Bolt)
- Increments by 10 for each instance
- Tracks allocations in `~/.blarify/ports.json`
- Automatically released on container stop

## Data Persistence

Data is stored in Docker volumes:

- Development: `blarify-neo4j-dev-data`
- Test: `blarify-neo4j-test-{uuid}-data` (auto-removed)
- Production: `blarify-neo4j-prod-data`

## Error Handling

The manager handles common scenarios gracefully:

```typescript
try {
  const instance = await manager.start({ 
    environment: 'development',
    password: 'password'
  });
} catch (error) {
  if (error.message.includes('Docker')) {
    console.error('Docker is not running');
  } else if (error.message.includes('port')) {
    console.error('No available ports');
  }
}
```

## Debugging

Enable debug logging for troubleshooting:

```typescript
const manager = new Neo4jContainerManager({ debug: true });

// Or use custom logger
const manager = new Neo4jContainerManager({
  logger: {
    debug: (msg, meta) => console.debug(`[DEBUG] ${msg}`, meta),
    info: (msg, meta) => console.info(`[INFO] ${msg}`, meta),
    warn: (msg, meta) => console.warn(`[WARN] ${msg}`, meta),
    error: (msg, meta) => console.error(`[ERROR] ${msg}`, meta),
  }
});
```

## Migration from Manual Setup

If you have existing Neo4j containers:

1. Export your data: `neo4j-admin dump`
2. Stop existing containers
3. Use this manager with import:

```typescript
const instance = await manager.start({
  environment: 'development',
  password: 'your-password'
});

await instance.importData('/path/to/dump.tar.gz');
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT