import * as vscode from 'vscode';
import * as path from 'path';
import { Driver } from 'neo4j-driver';
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
        // Generate a secure random password
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%';
        let password = '';
        for (let i = 0; i < 16; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return password;
    }
    
    
    async ensureRunning(): Promise<void> {
        // Initialize the container manager if not already done
        if (!this.manager) {
            try {
                // Try to load the bundled neo4j-container-manager
                const containerManagerPath = path.join(this.extensionPath, 'bundled', 'neo4j-container-manager');
                console.log(`[Neo4j] Loading container manager from: ${containerManagerPath}`);
                console.log(`[Neo4j] Extension path: ${this.extensionPath}`);
                console.log(`[Neo4j] Current working directory: ${process.cwd()}`);
                
                const { Neo4jContainerManager } = require(containerManagerPath);
                console.log(`[Neo4j] Container manager module loaded successfully`);
                
                this.manager = new Neo4jContainerManager({
                    logger: {
                        info: (msg: string) => console.log(`[Neo4j] ${msg}`),
                        error: (msg: string) => console.error(`[Neo4j] ${msg}`),
                        warn: (msg: string) => console.warn(`[Neo4j] ${msg}`),
                        debug: (msg: string) => console.log(`[Neo4j Debug] ${msg}`)
                    }
                });
                console.log(`[Neo4j] Container manager instance created`);
            } catch (error) {
                console.error('Failed to load neo4j-container-manager:', error);
                console.error('Module path attempted:', path.join(this.extensionPath, 'bundled', 'neo4j-container-manager'));
                throw new Error(`Neo4j container manager not found. Please ensure the extension is properly installed. Error: ${error}`);
            }
        }
        
        // Start or get existing instance
        if (!this.instance) {
            // Container name will be: {prefix}-{environment}
            const containerPrefix = 'blarify-visualizer';
            const environment = 'development';
            const containerName = `${containerPrefix}-${environment}`;
            
            // Try to get stored password first
            let password = this.configManager.getNeo4jPassword(containerName);
            
            if (password) {
                this.outputChannel.appendLine('Found stored password, attempting to connect...');
                try {
                    // Try to start/connect with stored password
                    // The container manager will automatically detect existing Docker containers
                    this.instance = await this.manager.start({
                        environment: environment,
                        containerPrefix: containerPrefix,
                        password: password,
                        username: 'neo4j'
                    });
                    this.outputChannel.appendLine('Successfully connected to Neo4j');
                    return; // Success!
                } catch (error: any) {
                    this.outputChannel.appendLine(`Failed to connect with stored password: ${error.message}`);
                    // Password might be wrong for existing container
                    // Clear it and try with a new password
                    await this.configManager.clearNeo4jPassword(containerName);
                    password = undefined;
                }
            }
            
            if (!password) {
                // Generate new password
                password = this.generatePassword();
                this.outputChannel.appendLine('Generated new password for Neo4j');
                
                try {
                    this.instance = await this.manager.start({
                        environment: environment,
                        containerPrefix: containerPrefix,
                        password: password,
                        username: 'neo4j'
                    });
                    
                    // Save password to settings
                    try {
                        await this.configManager.saveNeo4jPassword(containerName, password);
                        this.outputChannel.appendLine('Saved Neo4j password to workspace settings');
                    } catch (error) {
                        // This can fail in test environments or when no workspace is open
                        this.outputChannel.appendLine(`Could not save Neo4j password to workspace settings: ${error}`);
                        // Continue anyway - the container is running
                    }
                    
                    this.outputChannel.appendLine(`Neo4j started successfully`);
                    this.outputChannel.appendLine(`URI: ${this.instance.uri}`);
                    this.outputChannel.appendLine(`HTTP URI: ${this.instance.httpUri}`);
                    this.outputChannel.appendLine(`Container ID: ${this.instance.containerId}`);
                } catch (error: any) {
                    this.outputChannel.appendLine(`Failed to start Neo4j with new password: ${error.message}`);
                    
                    // If we get here, it's likely because a container exists with a different password
                    // We need to stop and remove the existing container
                    if (error.message.includes('Neo4j failed to start within')) {
                        this.outputChannel.appendLine('Existing container may have different password. Attempting to remove it...');
                        
                        // Try to remove the existing container
                        try {
                            const { exec } = require('child_process');
                            const util = require('util');
                            const execAsync = util.promisify(exec);
                            
                            // Stop and remove the container
                            await execAsync(`docker stop ${containerName} 2>/dev/null || true`);
                            await execAsync(`docker rm ${containerName} 2>/dev/null || true`);
                            this.outputChannel.appendLine('Removed existing container. Retrying with new password...');
                            
                            // Try one more time with the new password
                            this.instance = await this.manager.start({
                                environment: environment,
                                containerPrefix: containerPrefix,
                                password: password,
                                username: 'neo4j'
                            });
                            
                            // Save the password since we succeeded
                            try {
                                await this.configManager.saveNeo4jPassword(containerName, password);
                            } catch (saveError) {
                                this.outputChannel.appendLine(`Could not save password: ${saveError}`);
                            }
                            
                            this.outputChannel.appendLine('Neo4j started successfully after removing old container');
                            this.outputChannel.appendLine(`URI: ${this.instance.uri}`);
                            this.outputChannel.appendLine(`Container ID: ${this.instance.containerId}`);
                        } catch (retryError: any) {
                            this.outputChannel.appendLine(`Failed to recover: ${retryError.message}`);
                            throw new Error(`Cannot start Neo4j. Try manually removing container: docker rm -f ${containerName}`);
                        }
                    } else {
                        throw error;
                    }
                }
            }
        }
        
        // Connect driver if not connected
        if (!this.driver) {
            await this.connectDriver();
        }
    }
    
    async getStatus(): Promise<Neo4jStatus> {
        if (!this.instance) {
            return { running: false };
        }
        
        // Check if instance is actually running
        let isRunning = false;
        try {
            if (typeof this.instance.isRunning === 'function') {
                isRunning = await this.instance.isRunning();
            } else {
                // Fallback: assume running if instance exists
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
        
        // The instance has a driver property we can use directly
        if (this.instance.driver) {
            this.driver = this.instance.driver;
        } else {
            // Fallback: create driver from URI if driver not provided
            const uri = this.instance.uri;
            // For container manager instances, credentials might be embedded
            throw new Error('Instance does not have driver property');
        }
        
        // Verify connectivity
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
            // Clear existing graph
            await session.run('MATCH (n) DETACH DELETE n');
            
            // Create nodes
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
            
            // Create relationships
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
            // Get node counts by type
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
            
            // Get relationship counts by type
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
        // Close driver
        if (this.driver) {
            this.driver.close();
            this.driver = undefined;
        }
        
        // Don't stop container on dispose - let it keep running
        // User can manually stop via Docker if needed
    }
}