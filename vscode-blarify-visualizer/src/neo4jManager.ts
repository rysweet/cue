import * as vscode from 'vscode';
import * as path from 'path';
import { Driver } from 'neo4j-driver';
import { ConfigurationManager } from './configurationManager';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

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
    private manager?: any;
    private instance?: any;
    private driver?: Driver;
    private extensionPath: string;
    private outputChannel: vscode.OutputChannel;
    
    constructor(
        private configManager: ConfigurationManager,
        extensionPath: string
    ) {
        this.extensionPath = extensionPath;
        this.outputChannel = vscode.window.createOutputChannel('Neo4j Manager');
    }
    
    private generatePassword(): string {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%';
        let password = '';
        for (let i = 0; i < 16; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return password;
    }
    
    async ensureRunning(): Promise<void> {
        if (!this.manager) {
            try {
                const containerManagerPath = path.join(this.extensionPath, 'bundled', 'neo4j-container-manager');
                this.outputChannel.appendLine(`[Neo4j] Loading container manager from: ${containerManagerPath}`);
                
                const { Neo4jContainerManager } = require(containerManagerPath);
                this.outputChannel.appendLine(`[Neo4j] Container manager module loaded successfully`);
                
                this.manager = new Neo4jContainerManager({
                    logger: {
                        info: (msg: string) => this.outputChannel.appendLine(`[Neo4j] ${msg}`),
                        error: (msg: string) => this.outputChannel.appendLine(`[Neo4j ERROR] ${msg}`),
                        warn: (msg: string) => this.outputChannel.appendLine(`[Neo4j WARN] ${msg}`),
                        debug: (msg: string) => this.outputChannel.appendLine(`[Neo4j Debug] ${msg}`)
                    }
                });
                this.outputChannel.appendLine(`[Neo4j] Container manager instance created`);
            } catch (error) {
                this.outputChannel.appendLine(`Failed to load neo4j-container-manager: ${error}`);
                throw new Error(`Neo4j container manager not found. Error: ${error}`);
            }
        }
        
        if (!this.instance) {
            const containerPrefix = 'blarify-visualizer';
            const environment = 'development';
            const containerName = `${containerPrefix}-${environment}`;
            
            // WORKAROUND: Always remove existing containers
            this.outputChannel.appendLine(`[Neo4j] Removing any existing containers...`);
            try {
                await execAsync(`docker stop ${containerName} 2>/dev/null || true`);
                await execAsync(`docker rm ${containerName} 2>/dev/null || true`);
                this.outputChannel.appendLine(`[Neo4j] Cleanup complete`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            } catch (e) {
                // Ignore errors
            }
            
            const password = this.generatePassword();
            this.outputChannel.appendLine('Generated new password for Neo4j');
            
            try {
                this.instance = await this.manager.start({
                    environment: environment,
                    containerPrefix: containerPrefix,
                    password: password,
                    username: 'neo4j'
                });
                
                this.outputChannel.appendLine(`Neo4j started successfully`);
                this.outputChannel.appendLine(`URI: ${this.instance.uri}`);
                this.outputChannel.appendLine(`Container ID: ${this.instance.containerId}`);
                
                // Save password
                try {
                    await this.configManager.saveNeo4jPassword(containerName, password);
                } catch (e) {
                    this.outputChannel.appendLine(`Could not save password: ${e}`);
                }
            } catch (error: any) {
                this.outputChannel.appendLine(`Failed to start Neo4j: ${error.message}`);
                throw new Error(`Cannot start Neo4j: ${error.message}`);
            }
        }
        
        if (!this.driver) {
            await this.connectDriver();
        }
    }
    
    async getStatus(): Promise<Neo4jStatus> {
        if (!this.instance) {
            return { running: false };
        }
        
        let isRunning = false;
        try {
            if (typeof this.instance.isRunning === 'function') {
                isRunning = await this.instance.isRunning();
            } else {
                isRunning = true;
            }
        } catch (error) {
            this.outputChannel.appendLine(`Error checking instance status: ${error}`);
            isRunning = false;
        }
        
        return {
            running: isRunning,
            containerId: this.instance.containerId,
            details: isRunning ? `Running at ${this.instance.uri}` : 'Stopped'
        };
    }
    
    private async connectDriver(): Promise<void> {
        if (!this.instance) {
            throw new Error('No Neo4j instance available');
        }
        
        if (this.instance.driver) {
            this.driver = this.instance.driver;
        } else {
            throw new Error('Instance does not have driver property');
        }
        
        await this.driver!.verifyConnectivity();
    }
    
    async getDriver(): Promise<Driver> {
        if (!this.driver) {
            await this.ensureRunning();
        }
        return this.driver!;
    }
    
    async saveGraph(nodes: any[], edges: any[]): Promise<void> {
        const driver = await this.getDriver();
        const session = driver.session();
        
        try {
            await session.run('MATCH (n) DETACH DELETE n');
            
            for (const node of nodes) {
                await session.run(`
                    CREATE (n:${node.type || 'Node'})
                    SET n = $props
                `, {
                    props: {
                        id: node.id,
                        name: node.name || node.id,
                        path: node.path,
                        ...node.properties
                    }
                });
            }
            
            for (const edge of edges) {
                await session.run(`
                    MATCH (a {id: $sourceId})
                    MATCH (b {id: $targetId})
                    CREATE (a)-[r:${edge.type || 'RELATED_TO'}]->(b)
                    SET r = $props
                `, {
                    sourceId: edge.source,
                    targetId: edge.target,
                    props: edge.properties || {}
                });
            }
        } finally {
            await session.close();
        }
    }
    
    async getGraphStats(): Promise<GraphStats> {
        const driver = await this.getDriver();
        const session = driver.session();
        
        try {
            const nodeResult = await session.run(`
                MATCH (n)
                RETURN labels(n) as labels, count(n) as count
            `);
            
            const nodeTypes: { [key: string]: number } = {};
            let totalNodes = 0;
            
            nodeResult.records.forEach(record => {
                const labels = record.get('labels');
                const count = record.get('count').toNumber();
                if (labels.length > 0) {
                    nodeTypes[labels[0]] = count;
                    totalNodes += count;
                }
            });
            
            const relResult = await session.run(`
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
            `);
            
            const relationshipTypes: { [key: string]: number } = {};
            let totalRelationships = 0;
            
            relResult.records.forEach(record => {
                const type = record.get('type');
                const count = record.get('count').toNumber();
                relationshipTypes[type] = count;
                totalRelationships += count;
            });
            
            return {
                nodeCount: totalNodes,
                relationshipCount: totalRelationships,
                nodeTypes,
                relationshipTypes
            };
        } finally {
            await session.close();
        }
    }
    
    async exportData(): Promise<string> {
        if (!this.manager || !this.instance) {
            throw new Error('Neo4j not running');
        }
        
        const dataManager = this.manager.getDataManager();
        const exportPath = await dataManager.exportData(this.instance.name);
        return exportPath;
    }
    
    async importData(dataPath: string): Promise<void> {
        if (!this.manager || !this.instance) {
            throw new Error('Neo4j not running');
        }
        
        const dataManager = this.manager.getDataManager();
        await dataManager.importData(this.instance.name, dataPath);
    }
    
    dispose(): void {
        if (this.driver) {
            this.driver.close();
            this.driver = undefined;
        }
    }
}