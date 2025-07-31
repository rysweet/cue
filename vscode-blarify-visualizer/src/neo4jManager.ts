import * as vscode from 'vscode';
import { Neo4jContainerManager, Neo4jContainerInstance } from '@blarify/neo4j-container-manager';
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
    private containerManager: Neo4jContainerManager;
    private containerInstance?: Neo4jContainerInstance;
    
    constructor(private configManager: ConfigurationManager) {
        // Create container manager with VS Code specific settings
        this.containerManager = new Neo4jContainerManager({
            dataDir: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath 
                ? `${vscode.workspace.workspaceFolders[0].uri.fsPath}/.blarify`
                : undefined,
            debug: vscode.workspace.getConfiguration().get('blarifyVisualizer.debug', false)
        });
    }
    
    async ensureRunning(): Promise<void> {
        // If already have an instance, check if it's still running
        if (this.containerInstance) {
            if (await this.containerInstance.isRunning()) {
                return;
            }
            this.containerInstance = undefined;
        }
        
        // Get configuration
        const config = this.configManager.getNeo4jConfig();
        
        // Validate password is configured
        if (!config.password) {
            throw new Error('Neo4j password not configured. Please set it in VS Code settings.');
        }
        
        // Start container using the new manager
        try {
            this.containerInstance = await this.containerManager.start({
                environment: 'development',
                password: config.password,
                username: config.username || 'neo4j',
                plugins: ['apoc'],
                memory: '2G'
            });
            
            console.log(`Neo4j started at ${this.containerInstance.uri}`);
        } catch (error: any) {
            if (error.message.includes('Docker')) {
                throw new Error('Docker is not running. Please start Docker Desktop and try again.');
            }
            throw error;
        }
    }
    
    async getStatus(): Promise<Neo4jStatus> {
        if (!this.containerInstance) {
            return { running: false };
        }
        
        const running = await this.containerInstance.isRunning();
        if (!running) {
            this.containerInstance = undefined;
            return { running: false };
        }
        
        return {
            running: true,
            containerId: this.containerInstance.containerId,
            details: `Connected to ${this.containerInstance.uri}`
        };
    }
    
    async getStats(): Promise<GraphStats | null> {
        if (!this.containerInstance?.driver) {
            return null;
        }
        
        const session = this.containerInstance.driver.session();
        try {
            // Get node statistics
            const nodeResult = await session.run(`
                MATCH (n)
                RETURN labels(n) as labels, count(n) as count
            `);
            
            const nodeTypes: { [key: string]: number } = {};
            let totalNodes = 0;
            
            nodeResult.records.forEach(record => {
                const labels = record.get('labels');
                const count = record.get('count').toNumber();
                totalNodes += count;
                
                if (labels.length > 0) {
                    nodeTypes[labels[0]] = count;
                }
            });
            
            // Get relationship statistics
            const relResult = await session.run(`
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
            `);
            
            const relationshipTypes: { [key: string]: number } = {};
            let totalRelationships = 0;
            
            relResult.records.forEach(record => {
                const type = record.get('type');
                const count = record.get('count').toNumber();
                totalRelationships += count;
                relationshipTypes[type] = count;
            });
            
            return {
                nodeCount: totalNodes,
                relationshipCount: totalRelationships,
                nodeTypes,
                relationshipTypes
            };
        } catch (error) {
            console.error('Failed to get graph stats:', error);
            return null;
        } finally {
            await session.close();
        }
    }
    
    async saveGraph(nodes: any[], edges: any[]): Promise<void> {
        if (!this.containerInstance?.driver) {
            throw new Error('Neo4j driver not connected');
        }
        
        const session = this.containerInstance.driver.session();
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
        if (!this.containerInstance?.driver) {
            return {
                nodeCount: 0,
                relationshipCount: 0,
                nodeTypes: {},
                relationshipTypes: {}
            };
        }
        
        const session = this.containerInstance.driver.session();
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
    
    getDriver() {
        return this.containerInstance?.driver;
    }
    
    async dispose() {
        if (this.containerInstance) {
            // Ask user if they want to keep the container running
            const shouldStop = await vscode.window.showQuickPick(
                ['Keep running', 'Stop container'],
                {
                    placeHolder: 'Neo4j container is running. What would you like to do?'
                }
            );
            
            if (shouldStop === 'Stop container') {
                try {
                    await this.containerInstance.stop();
                } catch (error) {
                    console.error('Error stopping Neo4j container:', error);
                }
            } else {
                // Just close the driver connection but keep container running
                if (this.containerInstance.driver) {
                    await this.containerInstance.driver.close();
                }
            }
        }
    }
    
    // Data management methods
    async exportData(path: string): Promise<void> {
        if (!this.containerInstance) {
            throw new Error('Neo4j is not running');
        }
        await this.containerInstance.exportData(path);
    }
    
    async importData(path: string): Promise<void> {
        if (!this.containerInstance) {
            throw new Error('Neo4j is not running');
        }
        await this.containerInstance.importData(path);
    }
}