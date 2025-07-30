"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Neo4jManager = void 0;
const vscode = __importStar(require("vscode"));
const dockerode_1 = __importDefault(require("dockerode"));
const neo4j_driver_1 = __importDefault(require("neo4j-driver"));
class Neo4jManager {
    constructor(configManager) {
        this.configManager = configManager;
        this.containerName = 'blarify-neo4j';
        this.imageName = 'neo4j:5-community';
        this.docker = new dockerode_1.default();
    }
    async ensureRunning() {
        // First try to connect to Neo4j at the configured URI
        try {
            await this.connectDriver();
            await this.driver.verifyConnectivity();
            console.log('Successfully connected to existing Neo4j instance');
            return;
        }
        catch (e) {
            console.log('Could not connect to Neo4j, checking Docker containers...');
            if (this.driver) {
                await this.driver.close();
                this.driver = undefined;
            }
        }
        // Check container status
        const status = await this.getStatus();
        if (!status.running) {
            await this.startContainer();
        }
        await this.connectDriver();
    }
    async getStatus() {
        try {
            const containers = await this.docker.listContainers({ all: true });
            const container = containers.find(c => c.Names.some(name => name.includes(this.containerName)));
            if (container) {
                this.containerId = container.Id;
                return {
                    running: container.State === 'running',
                    containerId: container.Id,
                    details: `${container.State} - ${container.Status}`
                };
            }
            return { running: false };
        }
        catch (error) {
            console.error('Failed to check Neo4j status:', error);
            return { running: false, details: `Error: ${error}` };
        }
    }
    async startContainer() {
        try {
            // Check if container exists
            const status = await this.getStatus();
            if (status.containerId) {
                const container = this.docker.getContainer(status.containerId);
                if (!status.running) {
                    // Container exists but is stopped, start it
                    await container.start();
                    await this.waitForNeo4j();
                    return;
                }
                else {
                    // Container is already running
                    await this.waitForNeo4j();
                    return;
                }
            }
            // Pull image if needed
            await this.pullImageIfNeeded();
            // Check if container already exists
            const containers = await this.docker.listContainers({ all: true });
            const existingContainer = containers.find(c => c.Names.some(name => name === `/${this.containerName}`));
            if (existingContainer) {
                // Container exists, try to start it if stopped
                const container = this.docker.getContainer(existingContainer.Id);
                if (existingContainer.State !== 'running') {
                    try {
                        await container.start();
                        this.containerId = existingContainer.Id;
                        await this.waitForNeo4j();
                        return;
                    }
                    catch (e) {
                        // If we can't start it, remove and recreate
                        try {
                            await container.remove();
                        }
                        catch (removeError) {
                            // Ignore removal errors
                        }
                    }
                }
                else {
                    // Container is already running
                    this.containerId = existingContainer.Id;
                    return;
                }
            }
            // Get configuration
            const config = this.configManager.getNeo4jConfig();
            // Validate password is configured
            if (!config.password) {
                throw new Error('Neo4j password not configured. Please set it in VS Code settings.');
            }
            // Create and start new container
            const container = await this.docker.createContainer({
                Image: this.imageName,
                name: this.containerName,
                Env: [
                    `NEO4J_AUTH=${config.username}/${config.password}`,
                    'NEO4J_PLUGINS=["apoc"]',
                    'NEO4J_apoc_export_file_enabled=true',
                    'NEO4J_apoc_import_file_enabled=true',
                    'NEO4J_apoc_import_file_use__neo4j__config=true'
                ],
                ExposedPorts: {
                    '7474/tcp': {},
                    '7687/tcp': {}
                },
                HostConfig: {
                    PortBindings: {
                        '7474/tcp': [{ HostPort: '7474' }],
                        '7687/tcp': [{ HostPort: this.configManager.getNeo4jConfig().uri.includes('7688') ? '7688' : '7687' }]
                    },
                    AutoRemove: false
                }
            });
            await container.start();
            this.containerId = container.id;
            // Wait for Neo4j to be ready
            await this.waitForNeo4j();
        }
        catch (error) {
            throw new Error(`Failed to start Neo4j container: ${error}`);
        }
    }
    async pullImageIfNeeded() {
        try {
            await this.docker.getImage(this.imageName).inspect();
        }
        catch (error) {
            // Image doesn't exist, pull it
            vscode.window.showInformationMessage(`Pulling Neo4j image ${this.imageName}...`);
            await new Promise((resolve, reject) => {
                this.docker.pull(this.imageName, (err, stream) => {
                    if (err) {
                        reject(err);
                        return;
                    }
                    // Follow pull progress
                    this.docker.modem.followProgress(stream, (err, output) => {
                        if (err) {
                            reject(err);
                        }
                        else {
                            resolve();
                        }
                    });
                });
            });
        }
    }
    async waitForNeo4j(maxRetries = 30) {
        const config = this.configManager.getNeo4jConfig();
        for (let i = 0; i < maxRetries; i++) {
            try {
                const driver = neo4j_driver_1.default.driver(config.uri, neo4j_driver_1.default.auth.basic(config.username, config.password));
                const session = driver.session();
                await session.run('RETURN 1');
                await session.close();
                await driver.close();
                return;
            }
            catch (error) {
                if (i === maxRetries - 1) {
                    throw new Error('Neo4j failed to start within timeout');
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
    async connectDriver() {
        const config = this.configManager.getNeo4jConfig();
        if (!config.password) {
            throw new Error('Neo4j password not configured. Please set it in VS Code settings.');
        }
        this.driver = neo4j_driver_1.default.driver(config.uri, neo4j_driver_1.default.auth.basic(config.username, config.password));
        // Verify connection
        const session = this.driver.session();
        try {
            await session.run('RETURN 1');
        }
        finally {
            await session.close();
        }
    }
    async saveGraph(nodes, edges) {
        if (!this.driver) {
            throw new Error('Neo4j driver not connected');
        }
        const session = this.driver.session();
        try {
            // Clear existing data
            await session.run('MATCH (n) DETACH DELETE n');
            // Create nodes in batches
            const nodeBatchSize = 100;
            for (let i = 0; i < nodes.length; i += nodeBatchSize) {
                const batch = nodes.slice(i, i + nodeBatchSize);
                await session.run(`UNWIND $nodes AS node
                     CALL apoc.create.node(
                         node.extra_labels + [node.type, 'NODE'],
                         node.attributes
                     ) YIELD node as n
                     RETURN count(n)`, { nodes: batch });
            }
            // Create relationships in batches
            const edgeBatchSize = 100;
            for (let i = 0; i < edges.length; i += edgeBatchSize) {
                const batch = edges.slice(i, i + edgeBatchSize);
                await session.run(`UNWIND $edges AS edge
                     MATCH (source:NODE {node_id: edge.sourceId})
                     MATCH (target:NODE {node_id: edge.targetId})
                     CALL apoc.create.relationship(
                         source,
                         edge.type,
                         {scopeText: edge.scopeText},
                         target
                     ) YIELD rel
                     RETURN count(rel)`, { edges: batch });
            }
        }
        finally {
            await session.close();
        }
    }
    async getGraphStats() {
        if (!this.driver) {
            return {
                nodeCount: 0,
                relationshipCount: 0,
                nodeTypes: {},
                relationshipTypes: {}
            };
        }
        const session = this.driver.session();
        try {
            // Get node count and types
            const nodeResult = await session.run(`MATCH (n:NODE)
                 RETURN count(n) as total, labels(n) as labels`);
            const nodeCount = nodeResult.records[0]?.get('total').toNumber() || 0;
            const nodeTypes = {};
            const nodeTypeResult = await session.run(`MATCH (n:NODE)
                 UNWIND labels(n) as label
                 WITH label WHERE label <> 'NODE'
                 RETURN label, count(*) as count
                 ORDER BY count DESC`);
            nodeTypeResult.records.forEach(record => {
                nodeTypes[record.get('label')] = record.get('count').toNumber();
            });
            // Get relationship count and types
            const relResult = await session.run(`MATCH ()-[r]->()
                 RETURN count(r) as total`);
            const relationshipCount = relResult.records[0]?.get('total').toNumber() || 0;
            const relationshipTypes = {};
            const relTypeResult = await session.run(`MATCH ()-[r]->()
                 RETURN type(r) as type, count(*) as count
                 ORDER BY count DESC`);
            relTypeResult.records.forEach(record => {
                relationshipTypes[record.get('type')] = record.get('count').toNumber();
            });
            return {
                nodeCount,
                relationshipCount,
                nodeTypes,
                relationshipTypes
            };
        }
        finally {
            await session.close();
        }
    }
    getDriver() {
        return this.driver;
    }
    async dispose() {
        if (this.driver) {
            await this.driver.close();
        }
        // Optionally stop container
        const shouldStop = await vscode.window.showQuickPick(['Keep running', 'Stop container'], {
            placeHolder: 'Neo4j container is running. What would you like to do?'
        });
        if (shouldStop === 'Stop container' && this.containerId) {
            try {
                const container = this.docker.getContainer(this.containerId);
                await container.stop();
                await container.remove();
            }
            catch (error) {
                console.error('Failed to stop container:', error);
            }
        }
    }
}
exports.Neo4jManager = Neo4jManager;
//# sourceMappingURL=neo4jManager.js.map