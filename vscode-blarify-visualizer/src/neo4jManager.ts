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
            
            // Try to use existing container with saved password first
            let savedPassword = this.configManager.getNeo4jPassword(containerName);
            
            if (savedPassword) {
                this.outputChannel.appendLine(`[Neo4j] Found saved password for container: ${containerName}`);
                this.outputChannel.appendLine(`[Neo4j] Trying to connect with saved password...`);
                try {
                    this.instance = await this.manager.start({
                        environment: environment,
                        containerPrefix: containerPrefix,
                        password: savedPassword,
                        username: 'neo4j'
                    });
                    
                    this.outputChannel.appendLine(`[Neo4j] Connected to existing container successfully`);
                    this.outputChannel.appendLine(`URI: ${this.instance.uri}`);
                    this.outputChannel.appendLine(`Container ID: ${this.instance.containerId}`);
                    return; // Success! Exit early
                } catch (error: any) {
                    this.outputChannel.appendLine(`[Neo4j] Failed to connect with saved password: ${error.message}`);
                    // Clear invalid password
                    await this.configManager.clearNeo4jPassword(containerName);
                    this.outputChannel.appendLine(`[Neo4j] Cleared invalid saved password`);
                }
            } else {
                this.outputChannel.appendLine(`[Neo4j] No saved password found for container: ${containerName}`);
            }
            
            // If we get here, either no saved password or connection failed
            // Remove existing container and start fresh
            this.outputChannel.appendLine(`[Neo4j] Removing any existing containers...`);
            try {
                // Check if container exists first
                const { stdout: psOutput } = await execAsync(`docker ps -a --filter name=${containerName} --format "{{.ID}}"`);
                if (psOutput.trim()) {
                    this.outputChannel.appendLine(`[Neo4j] Found existing container: ${psOutput.trim()}`);
                    
                    // Get volume name before removing container
                    const { stdout: volumeOutput } = await execAsync(`docker inspect ${containerName} --format '{{range .Mounts}}{{.Name}}{{end}}' 2>/dev/null || true`);
                    const volumeName = volumeOutput.trim();
                    
                    // Force remove the container
                    const { stdout: rmOutput, stderr: rmError } = await execAsync(`docker rm -f ${containerName} 2>&1`);
                    if (rmOutput) this.outputChannel.appendLine(`[Neo4j] Container removed: ${rmOutput.trim()}`);
                    if (rmError && !rmError.includes('No such container')) {
                        this.outputChannel.appendLine(`[Neo4j] Remove error: ${rmError.trim()}`);
                    }
                    
                    // Also remove the volume to prevent authentication issues
                    if (volumeName) {
                        this.outputChannel.appendLine(`[Neo4j] Removing volume: ${volumeName}`);
                        const { stdout: volRmOutput, stderr: volRmError } = await execAsync(`docker volume rm ${volumeName} 2>&1 || true`);
                        if (volRmOutput) this.outputChannel.appendLine(`[Neo4j] Volume removed: ${volRmOutput.trim()}`);
                        if (volRmError && !volRmError.includes('No such volume')) {
                            this.outputChannel.appendLine(`[Neo4j] Volume remove error: ${volRmError.trim()}`);
                        }
                    }
                    
                    // Also remove volumes with the container manager naming pattern
                    this.outputChannel.appendLine(`[Neo4j] Checking for additional volumes...`);
                    const { stdout: volListOutput } = await execAsync(`docker volume ls --format "{{.Name}}" | grep -E "^blarify-neo4j-${environment}" || true`);
                    const volumes = volListOutput.trim().split('\n').filter(v => v);
                    for (const vol of volumes) {
                        if (vol) {
                            this.outputChannel.appendLine(`[Neo4j] Removing volume: ${vol}`);
                            await execAsync(`docker volume rm ${vol} 2>&1 || true`);
                        }
                    }
                    
                    // Wait for Docker to clean up
                    this.outputChannel.appendLine(`[Neo4j] Waiting for cleanup...`);
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // Verify container is gone
                    const { stdout: checkOutput } = await execAsync(`docker ps -a --filter name=${containerName} --format "{{.ID}}"`);
                    if (checkOutput.trim()) {
                        throw new Error(`Failed to remove container ${containerName}`);
                    }
                    this.outputChannel.appendLine(`[Neo4j] Container and volume successfully removed`);
                } else {
                    this.outputChannel.appendLine(`[Neo4j] No existing container found`);
                }
            } catch (e: any) {
                this.outputChannel.appendLine(`[Neo4j] Critical error during cleanup: ${e.message}`);
                throw new Error(`Failed to clean up existing container: ${e.message}`);
            }
            
            const password = this.generatePassword();
            this.outputChannel.appendLine(`[Neo4j] Generated new password for Neo4j`);
            this.outputChannel.appendLine(`[Neo4j] Starting container with config:`);
            this.outputChannel.appendLine(`  - Environment: ${environment}`);
            this.outputChannel.appendLine(`  - Container prefix: ${containerPrefix}`);
            this.outputChannel.appendLine(`  - Username: neo4j`);
            
            try {
                this.outputChannel.appendLine(`[Neo4j] Calling container manager start method...`);
                this.instance = await this.manager.start({
                    environment: environment,
                    containerPrefix: containerPrefix,
                    password: password,
                    username: 'neo4j'
                });
                
                this.outputChannel.appendLine(`[Neo4j] Container manager returned successfully`);
                this.outputChannel.appendLine(`[Neo4j] Neo4j started successfully`);
                this.outputChannel.appendLine(`[Neo4j] URI: ${this.instance.uri}`);
                this.outputChannel.appendLine(`[Neo4j] Container ID: ${this.instance.containerId}`);
                
                // Save password
                try {
                    await this.configManager.saveNeo4jPassword(containerName, password);
                    this.outputChannel.appendLine(`[Neo4j] Password saved successfully for container: ${containerName}`);
                } catch (e) {
                    this.outputChannel.appendLine(`[Neo4j] Could not save password: ${e}`);
                }
            } catch (error: any) {
                this.outputChannel.appendLine(`[Neo4j] Container manager start failed: ${error.message}`);
                this.outputChannel.appendLine(`[Neo4j] Error stack: ${error.stack}`);
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