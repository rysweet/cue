import * as vscode from 'vscode';
import * as path from 'path';
import { Driver } from 'neo4j-driver';
import { ConfigurationManager } from './configurationManager';

export interface Neo4jStatus {
    running: boolean;
    containerId?: string;
    details?: string;
}

interface GraphStats {
    nodeCount: number;
    relationshipCount: number;
    nodeTypes: { [key: string]: number };
    relationshipTypes: { [key: string]: number };
}

// Constants
const CONTAINER_PREFIX = 'blarify-visualizer';
const ENVIRONMENT = 'development';

export class Neo4jManager {
    private instance: any = null;
    private driver: Driver | null = null;
    private manager: any = null;
    private outputChannel: vscode.OutputChannel;

    constructor(
        private configManager: ConfigurationManager,
        private extensionPath: string
    ) {
        this.outputChannel = vscode.window.createOutputChannel('Neo4j Manager');
        this.initializeContainerManager();
    }

    /**
     * Initialize the container manager module
     */
    private initializeContainerManager(): void {
        if (this.manager) return;

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

    /**
     * Ensure Neo4j is running - simplified version that relies on fixed container manager
     */
    async ensureRunning(): Promise<void> {
        if (this.instance && this.driver) {
            try {
                await this.driver.verifyConnectivity();
                this.outputChannel.appendLine('[Neo4j] Existing instance is healthy');
                return;
            } catch (error: any) {
                this.outputChannel.appendLine(`[Neo4j] Existing instance is not responding: ${error.message}, will restart`);
                this.instance = null;
                this.driver = null;
            }
        }

        if (!this.instance) {
            const containerName = `${CONTAINER_PREFIX}-${ENVIRONMENT}`;
            let password: string;
            
            try {
                // Attempt to retrieve saved password with error handling
                const savedPassword = this.configManager.getNeo4jPassword(containerName);
                if (savedPassword) {
                    this.outputChannel.appendLine(`[Neo4j] Found saved password for container: ${containerName}`);
                    password = savedPassword;
                } else {
                    this.outputChannel.appendLine(`[Neo4j] No saved password found, generating new one`);
                    password = this.generatePassword();
                }
            } catch (error: any) {
                this.outputChannel.appendLine(`[Neo4j] Error retrieving password: ${error.message}, generating new one`);
                password = this.generatePassword();
            }
            
            this.outputChannel.appendLine(`[Neo4j] Starting container with config:`);
            this.outputChannel.appendLine(`  - Environment: ${ENVIRONMENT}`);
            this.outputChannel.appendLine(`  - Container prefix: ${CONTAINER_PREFIX}`);
            this.outputChannel.appendLine(`  - Container name: ${containerName}`);
            this.outputChannel.appendLine(`  - Username: neo4j`);
            this.outputChannel.appendLine(`  - Using ${password === this.configManager.getNeo4jPassword(containerName) ? 'saved' : 'new'} password`);
            
            try {
                this.outputChannel.appendLine(`[Neo4j] Calling container manager start method...`);
                const startTime = Date.now();
                
                this.instance = await this.manager.start({
                    environment: ENVIRONMENT,
                    containerPrefix: CONTAINER_PREFIX,
                    password: password,
                    username: 'neo4j'
                });
                
                const startDuration = Date.now() - startTime;
                this.outputChannel.appendLine(`[Neo4j] Container manager returned successfully in ${startDuration}ms`);
                this.outputChannel.appendLine(`[Neo4j] Neo4j started successfully`);
                this.outputChannel.appendLine(`[Neo4j] URI: ${this.instance.uri}`);
                this.outputChannel.appendLine(`[Neo4j] Container ID: ${this.instance.containerId}`);
                
                // Check container age if available
                if (typeof this.instance.createdAt === 'string' || typeof this.instance.createdAt === 'number') {
                    const containerAge = this.getContainerAge(this.instance.createdAt);
                    this.outputChannel.appendLine(`[Neo4j] Container age: ${containerAge}`);
                    
                    // Warn if container is older than 7 days
                    if (containerAge.includes('day') && parseInt(containerAge) > 7) {
                        this.outputChannel.appendLine(`[Neo4j WARN] Container is older than 7 days, consider recreation for optimal performance`);
                    }
                }
                
                // Save password for future use with error handling
                try {
                    await this.configManager.saveNeo4jPassword(containerName, password);
                    this.outputChannel.appendLine(`[Neo4j] Password saved successfully to global configuration`);
                } catch (saveError: any) {
                    this.outputChannel.appendLine(`[Neo4j WARN] Failed to save password: ${saveError.message}`);
                    // Don't fail the entire operation if password saving fails
                }
            } catch (error: any) {
                this.outputChannel.appendLine(`[Neo4j] Container manager start failed: ${error.message}`);
                this.outputChannel.appendLine(`[Neo4j] Error details: ${error.stack || 'No stack trace available'}`);
                
                // If password retrieval failed, clear potentially corrupted password
                if (error.message.includes('password') || error.message.includes('authentication')) {
                    try {
                        await this.configManager.clearNeo4jPassword(containerName);
                        this.outputChannel.appendLine(`[Neo4j] Cleared potentially corrupted saved password`);
                    } catch (clearError: any) {
                        this.outputChannel.appendLine(`[Neo4j WARN] Failed to clear password: ${clearError.message}`);
                    }
                }
                
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
                await session.run(
                    'CREATE (n:Node {id: $id, name: $name, type: $type, filePath: $filePath})',
                    node
                );
            }
            
            for (const edge of edges) {
                await session.run(
                    'MATCH (a:Node {id: $source}), (b:Node {id: $target}) CREATE (a)-[:DEPENDS_ON {type: $type}]->(b)',
                    edge
                );
            }
        } finally {
            await session.close();
        }
    }

    async getGraphStats(): Promise<GraphStats> {
        const driver = await this.getDriver();
        const session = driver.session();
        
        try {
            const nodeCountResult = await session.run('MATCH (n) RETURN count(n) as count');
            const nodeCount = nodeCountResult.records[0].get('count').toNumber();
            
            const relCountResult = await session.run('MATCH ()-[r]->() RETURN count(r) as count');
            const relationshipCount = relCountResult.records[0].get('count').toNumber();
            
            const nodeTypesResult = await session.run('MATCH (n) RETURN n.type as type, count(n) as count');
            const nodeTypes: { [key: string]: number } = {};
            nodeTypesResult.records.forEach(record => {
                nodeTypes[record.get('type')] = record.get('count').toNumber();
            });
            
            const relTypesResult = await session.run('MATCH ()-[r]->() RETURN type(r) as type, count(r) as count');
            const relationshipTypes: { [key: string]: number } = {};
            relTypesResult.records.forEach(record => {
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

    async dispose(): Promise<void> {
        if (this.driver) {
            await this.driver.close();
            this.driver = null;
        }
        if (this.instance && this.instance.stop) {
            await this.instance.stop();
            this.instance = null;
        }
        this.outputChannel.dispose();
    }

    /**
     * Generate a cryptographically secure password using Node.js crypto module
     */
    private generatePassword(): string {
        try {
            const crypto = require('crypto');
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
            const passwordLength = 16;
            const randomBytes = crypto.randomBytes(passwordLength);
            let password = '';
            
            for (let i = 0; i < passwordLength; i++) {
                password += chars[randomBytes[i] % chars.length];
            }
            
            this.outputChannel.appendLine(`[Neo4j] Generated secure password of length ${passwordLength}`);
            return password;
        } catch (error: any) {
            this.outputChannel.appendLine(`[Neo4j ERROR] Failed to generate secure password: ${error.message}`);
            // Fallback to a simple but less secure method if crypto fails
            const fallbackPassword = 'fallback-' + Date.now().toString(36);
            this.outputChannel.appendLine(`[Neo4j WARN] Using fallback password generation method`);
            return fallbackPassword;
        }
    }

    /**
     * Calculate container age from creation timestamp
     */
    private getContainerAge(createdAt: string | number): string {
        try {
            const creationTime = typeof createdAt === 'string' ? new Date(createdAt).getTime() : createdAt;
            const now = Date.now();
            const ageMs = now - creationTime;
            
            const minutes = Math.floor(ageMs / (1000 * 60));
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);
            
            if (days > 0) {
                return `${days} day${days > 1 ? 's' : ''}, ${hours % 24} hour${(hours % 24) > 1 ? 's' : ''}`;
            } else if (hours > 0) {
                return `${hours} hour${hours > 1 ? 's' : ''}, ${minutes % 60} minute${(minutes % 60) > 1 ? 's' : ''}`;
            } else {
                return `${minutes} minute${minutes > 1 ? 's' : ''}`;
            }
        } catch (error: any) {
            this.outputChannel.appendLine(`[Neo4j WARN] Failed to calculate container age: ${error.message}`);
            return 'unknown';
        }
    }
}