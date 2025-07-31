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
Object.defineProperty(exports, "__esModule", { value: true });
exports.Neo4jManager = void 0;
const vscode = __importStar(require("vscode"));
const neo4j_container_manager_1 = require("@blarify/neo4j-container-manager");
class Neo4jManager {
    constructor(configManager) {
        this.configManager = configManager;
        // Create container manager with VS Code specific settings
        this.containerManager = new neo4j_container_manager_1.Neo4jContainerManager({
            dataDir: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
                ? `${vscode.workspace.workspaceFolders[0].uri.fsPath}/.blarify`
                : undefined,
            debug: vscode.workspace.getConfiguration().get('blarifyVisualizer.debug', false)
        });
    }
    async ensureRunning() {
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
        }
        catch (error) {
            if (error.message.includes('Docker')) {
                throw new Error('Docker is not running. Please start Docker Desktop and try again.');
            }
            throw error;
        }
    }
    async getStatus() {
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
    async getStats() {
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
            const nodeTypes = {};
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
            const relationshipTypes = {};
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
        }
        catch (error) {
            console.error('Failed to get graph stats:', error);
            return null;
        }
        finally {
            await session.close();
        }
    }
    async saveGraph(nodes, edges) {
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
        return this.containerInstance?.driver;
    }
    async dispose() {
        if (this.containerInstance) {
            // Ask user if they want to keep the container running
            const shouldStop = await vscode.window.showQuickPick(['Keep running', 'Stop container'], {
                placeHolder: 'Neo4j container is running. What would you like to do?'
            });
            if (shouldStop === 'Stop container') {
                try {
                    await this.containerInstance.stop();
                }
                catch (error) {
                    console.error('Error stopping Neo4j container:', error);
                }
            }
            else {
                // Just close the driver connection but keep container running
                if (this.containerInstance.driver) {
                    await this.containerInstance.driver.close();
                }
            }
        }
    }
    // Data management methods
    async exportData(path) {
        if (!this.containerInstance) {
            throw new Error('Neo4j is not running');
        }
        await this.containerInstance.exportData(path);
    }
    async importData(path) {
        if (!this.containerInstance) {
            throw new Error('Neo4j is not running');
        }
        await this.containerInstance.importData(path);
    }
}
exports.Neo4jManager = Neo4jManager;
//# sourceMappingURL=neo4jManager.js.map