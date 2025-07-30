import * as vscode from 'vscode';
import Docker from 'dockerode';
import neo4j, { Driver, Session } from 'neo4j-driver';
import { ConfigurationManager } from './configurationManager';

export interface Neo4jStatus {
    running: boolean;
    containerId?: string;
    details?: string;
}

export interface GraphStats {
    nodeCount: number;
    relationshipCount: number;
    nodeTypes: { [key: string]: number };
    relationshipTypes: { [key: string]: number };
}

export class Neo4jManager implements vscode.Disposable {
    private docker: Docker;
    private driver?: Driver;
    private containerId?: string;
    private readonly containerName = 'blarify-neo4j';
    private readonly imageName = 'neo4j:5-community';
    
    constructor(private configManager: ConfigurationManager) {
        this.docker = new Docker();
    }
    
    async ensureRunning(): Promise<void> {
        const status = await this.getStatus();
        if (!status.running) {
            await this.startContainer();
        }
        await this.connectDriver();
    }
    
    async getStatus(): Promise<Neo4jStatus> {
        try {
            const containers = await this.docker.listContainers({ all: true });
            const container = containers.find(c => 
                c.Names.some(name => name.includes(this.containerName))
            );
            
            if (container) {
                this.containerId = container.Id;
                return {
                    running: container.State === 'running',
                    containerId: container.Id,
                    details: `${container.State} - ${container.Status}`
                };
            }
            
            return { running: false };
        } catch (error) {
            console.error('Failed to check Neo4j status:', error);
            return { running: false, details: `Error: ${error}` };
        }
    }
    
    private async startContainer(): Promise<void> {
        try {
            // Check if container exists but is stopped
            const status = await this.getStatus();
            if (status.containerId && !status.running) {
                const container = this.docker.getContainer(status.containerId);
                await container.start();
                await this.waitForNeo4j();
                return;
            }
            
            // Pull image if needed
            await this.pullImageIfNeeded();
            
            // Create and start new container
            const container = await this.docker.createContainer({
                Image: this.imageName,
                name: this.containerName,
                Env: [
                    'NEO4J_AUTH=neo4j/blarify123',
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
                        '7687/tcp': [{ HostPort: '7687' }]
                    },
                    AutoRemove: false
                }
            });
            
            await container.start();
            this.containerId = container.id;
            
            // Wait for Neo4j to be ready
            await this.waitForNeo4j();
            
        } catch (error) {
            throw new Error(`Failed to start Neo4j container: ${error}`);
        }
    }
    
    private async pullImageIfNeeded(): Promise<void> {
        try {
            await this.docker.getImage(this.imageName).inspect();
        } catch (error) {
            // Image doesn't exist, pull it
            vscode.window.showInformationMessage(`Pulling Neo4j image ${this.imageName}...`);
            
            await new Promise<void>((resolve, reject) => {
                this.docker.pull(this.imageName, (err: any, stream: any) => {
                    if (err) {
                        reject(err);
                        return;
                    }
                    
                    // Follow pull progress
                    this.docker.modem.followProgress(stream, (err: any, output: any) => {
                        if (err) {
                            reject(err);
                        } else {
                            resolve();
                        }
                    });
                });
            });
        }
    }
    
    private async waitForNeo4j(maxRetries = 30): Promise<void> {
        for (let i = 0; i < maxRetries; i++) {
            try {
                const driver = neo4j.driver(
                    'bolt://localhost:7687',
                    neo4j.auth.basic('neo4j', 'blarify123')
                );
                
                const session = driver.session();
                await session.run('RETURN 1');
                await session.close();
                await driver.close();
                
                return;
            } catch (error) {
                if (i === maxRetries - 1) {
                    throw new Error('Neo4j failed to start within timeout');
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
    
    private async connectDriver(): Promise<void> {
        const config = this.configManager.getNeo4jConfig();
        this.driver = neo4j.driver(
            config.uri,
            neo4j.auth.basic(config.username, config.password || 'blarify123')
        );
        
        // Verify connection
        const session = this.driver.session();
        try {
            await session.run('RETURN 1');
        } finally {
            await session.close();
        }
    }
    
    async saveGraph(nodes: any[], edges: any[]): Promise<void> {
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
                await session.run(
                    `UNWIND $nodes AS node
                     CALL apoc.create.node(
                         node.extra_labels + [node.type, 'NODE'],
                         node.attributes
                     ) YIELD node as n
                     RETURN count(n)`,
                    { nodes: batch }
                );
            }
            
            // Create relationships in batches
            const edgeBatchSize = 100;
            for (let i = 0; i < edges.length; i += edgeBatchSize) {
                const batch = edges.slice(i, i + edgeBatchSize);
                await session.run(
                    `UNWIND $edges AS edge
                     MATCH (source:NODE {node_id: edge.sourceId})
                     MATCH (target:NODE {node_id: edge.targetId})
                     CALL apoc.create.relationship(
                         source,
                         edge.type,
                         {scopeText: edge.scopeText},
                         target
                     ) YIELD rel
                     RETURN count(rel)`,
                    { edges: batch }
                );
            }
        } finally {
            await session.close();
        }
    }
    
    async getGraphStats(): Promise<GraphStats> {
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
            const nodeResult = await session.run(
                `MATCH (n:NODE)
                 RETURN count(n) as total, labels(n) as labels`
            );
            
            const nodeCount = nodeResult.records[0]?.get('total').toNumber() || 0;
            const nodeTypes: { [key: string]: number } = {};
            
            const nodeTypeResult = await session.run(
                `MATCH (n:NODE)
                 UNWIND labels(n) as label
                 WITH label WHERE label <> 'NODE'
                 RETURN label, count(*) as count
                 ORDER BY count DESC`
            );
            
            nodeTypeResult.records.forEach(record => {
                nodeTypes[record.get('label')] = record.get('count').toNumber();
            });
            
            // Get relationship count and types
            const relResult = await session.run(
                `MATCH ()-[r]->()
                 RETURN count(r) as total`
            );
            
            const relationshipCount = relResult.records[0]?.get('total').toNumber() || 0;
            const relationshipTypes: { [key: string]: number } = {};
            
            const relTypeResult = await session.run(
                `MATCH ()-[r]->()
                 RETURN type(r) as type, count(*) as count
                 ORDER BY count DESC`
            );
            
            relTypeResult.records.forEach(record => {
                relationshipTypes[record.get('type')] = record.get('count').toNumber();
            });
            
            return {
                nodeCount,
                relationshipCount,
                nodeTypes,
                relationshipTypes
            };
        } finally {
            await session.close();
        }
    }
    
    getDriver(): Driver | undefined {
        return this.driver;
    }
    
    async dispose(): Promise<void> {
        if (this.driver) {
            await this.driver.close();
        }
        
        // Optionally stop container
        const shouldStop = await vscode.window.showQuickPick(
            ['Keep running', 'Stop container'],
            {
                placeHolder: 'Neo4j container is running. What would you like to do?'
            }
        );
        
        if (shouldStop === 'Stop container' && this.containerId) {
            try {
                const container = this.docker.getContainer(this.containerId);
                await container.stop();
                await container.remove();
            } catch (error) {
                console.error('Failed to stop container:', error);
            }
        }
    }
}