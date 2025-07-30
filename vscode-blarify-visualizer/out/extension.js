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
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const neo4jManager_1 = require("./neo4jManager");
const blarifyIntegration_1 = require("./blarifyIntegration");
const graphDataProvider_1 = require("./graphDataProvider");
const visualizationPanel_1 = require("./visualizationPanel");
const statusBarManager_1 = require("./statusBarManager");
const configurationManager_1 = require("./configurationManager");
let neo4jManager;
let blarifyIntegration;
let graphDataProvider;
let statusBarManager;
let configManager;
let outputChannel;
async function activate(context) {
    console.log('Blarify Visualizer is now active!');
    // Create output channel for debugging
    outputChannel = vscode.window.createOutputChannel('Blarify Visualizer');
    context.subscriptions.push(outputChannel);
    outputChannel.appendLine('Blarify Visualizer extension activated');
    outputChannel.show();
    // Initialize configuration manager
    configManager = new configurationManager_1.ConfigurationManager();
    outputChannel.appendLine('Configuration manager initialized');
    // Initialize status bar
    statusBarManager = new statusBarManager_1.StatusBarManager();
    context.subscriptions.push(statusBarManager);
    outputChannel.appendLine('Status bar manager initialized');
    // Initialize Neo4j manager
    neo4jManager = new neo4jManager_1.Neo4jManager(configManager);
    context.subscriptions.push(neo4jManager);
    outputChannel.appendLine('Neo4j manager initialized');
    // Initialize Blarify integration
    blarifyIntegration = new blarifyIntegration_1.BlarifyIntegration(configManager);
    outputChannel.appendLine('Blarify integration initialized');
    // Initialize graph data provider
    graphDataProvider = new graphDataProvider_1.GraphDataProvider(neo4jManager, configManager);
    outputChannel.appendLine('Graph data provider initialized');
    // Skip Docker startup in test environment
    const isTestMode = context.extensionMode === vscode.ExtensionMode.Test;
    if (!isTestMode) {
        // Start Neo4j container
        statusBarManager.setStatus('Starting Neo4j...', 'sync~spin');
        try {
            await neo4jManager.ensureRunning();
            statusBarManager.setStatus('Neo4j ready', 'database');
            // Prompt user to ingest workspace on startup
            const shouldIngest = await vscode.window.showInformationMessage('Would you like to analyze your workspace with Blarify?', 'Yes', 'Not now');
            if (shouldIngest === 'Yes') {
                await ingestWorkspace();
            }
        }
        catch (error) {
            statusBarManager.setStatus('Neo4j failed', 'error');
            vscode.window.showErrorMessage(`Failed to start Neo4j: ${error}`);
        }
    }
    // Register commands
    const showVisualizationCommand = vscode.commands.registerCommand('blarifyVisualizer.showVisualization', () => showVisualization(context));
    const ingestWorkspaceCommand = vscode.commands.registerCommand('blarifyVisualizer.ingestWorkspace', ingestWorkspace);
    const updateGraphCommand = vscode.commands.registerCommand('blarifyVisualizer.updateGraph', updateGraph);
    const searchGraphCommand = vscode.commands.registerCommand('blarifyVisualizer.searchGraph', searchGraph);
    const restartNeo4jCommand = vscode.commands.registerCommand('blarifyVisualizer.restartNeo4j', restartNeo4j);
    context.subscriptions.push(showVisualizationCommand, ingestWorkspaceCommand, updateGraphCommand, searchGraphCommand, restartNeo4jCommand);
    // Register status view provider
    const statusProvider = new StatusViewProvider(neo4jManager, blarifyIntegration);
    const treeView = vscode.window.createTreeView('blarifyStatus', {
        treeDataProvider: statusProvider,
        showCollapseAll: false
    });
    context.subscriptions.push(treeView);
    // Refresh the view to ensure it's populated
    statusProvider.refresh();
    // Watch for file changes if auto-update is enabled
    if (configManager.getAutoUpdate()) {
        const watcher = vscode.workspace.createFileSystemWatcher('**/*');
        watcher.onDidChange(() => {
            if (configManager.getAutoUpdate()) {
                updateGraph();
            }
        });
        context.subscriptions.push(watcher);
    }
}
exports.activate = activate;
function deactivate() {
    // Cleanup will be handled by dispose methods
}
exports.deactivate = deactivate;
async function showVisualization(context) {
    try {
        const panel = visualizationPanel_1.VisualizationPanel.createOrShow(context.extensionUri);
        panel.setDataProvider(graphDataProvider);
        await panel.loadGraph();
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to show visualization: ${error}`);
    }
}
async function ingestWorkspace() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Analyzing workspace with Blarify',
        cancellable: true
    }, async (progress, token) => {
        try {
            statusBarManager.setStatus('Analyzing...', 'sync~spin');
            progress.report({ increment: 0, message: 'Starting analysis...' });
            const result = await blarifyIntegration.analyzeWorkspace(workspaceFolder.uri.fsPath, progress, token);
            progress.report({ increment: 50, message: 'Saving to Neo4j...' });
            await neo4jManager.saveGraph(result.nodes, result.edges);
            progress.report({ increment: 100, message: 'Complete!' });
            statusBarManager.setStatus('Analysis complete', 'check');
            vscode.window.showInformationMessage(`Analysis complete: ${result.nodes.length} nodes, ${result.edges.length} relationships`);
            // Refresh any open visualizations
            visualizationPanel_1.VisualizationPanel.refreshAll();
        }
        catch (error) {
            statusBarManager.setStatus('Analysis failed', 'error');
            vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
    });
}
async function updateGraph() {
    // Similar to ingestWorkspace but incremental
    await ingestWorkspace();
}
async function searchGraph() {
    const query = await vscode.window.showInputBox({
        prompt: 'Enter search query',
        placeHolder: 'e.g., class:UserService, function:authenticate, file:*.ts'
    });
    if (query) {
        const panel = visualizationPanel_1.VisualizationPanel.currentPanel;
        if (panel) {
            panel.search(query);
        }
        else {
            // Open visualization first
            vscode.window.showInformationMessage('Please open the visualization first');
            await vscode.commands.executeCommand('blarifyVisualizer.showVisualization');
            // Delay to ensure panel is ready
            setTimeout(() => {
                visualizationPanel_1.VisualizationPanel.currentPanel?.search(query);
            }, 500);
        }
    }
}
async function restartNeo4j() {
    statusBarManager.setStatus('Restarting Neo4j...', 'sync~spin');
    try {
        // Stop any existing container
        const status = await neo4jManager.getStatus();
        if (status.containerId) {
            const container = neo4jManager.docker.getContainer(status.containerId);
            try {
                await container.stop();
                await container.remove();
            }
            catch (e) {
                // Ignore errors
            }
        }
        // Start fresh
        await neo4jManager.ensureRunning();
        statusBarManager.setStatus('Neo4j ready', 'database');
        vscode.window.showInformationMessage('Neo4j restarted successfully');
    }
    catch (error) {
        statusBarManager.setStatus('Neo4j failed', 'error');
        vscode.window.showErrorMessage(`Failed to restart Neo4j: ${error}`);
    }
}
class StatusViewProvider {
    constructor(neo4jManager, blarifyIntegration) {
        this.neo4jManager = neo4jManager;
        this.blarifyIntegration = blarifyIntegration;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            const items = [];
            // Neo4j status
            const neo4jStatus = await this.neo4jManager.getStatus();
            items.push(new StatusItem(`Neo4j: ${neo4jStatus.running ? 'Running' : 'Stopped'}`, neo4jStatus.running ? 'database' : 'database-off', neo4jStatus.details));
            // Graph statistics
            if (neo4jStatus.running) {
                const stats = await this.neo4jManager.getGraphStats();
                items.push(new StatusItem(`Nodes: ${stats.nodeCount}`, 'symbol-class'));
                items.push(new StatusItem(`Relationships: ${stats.relationshipCount}`, 'references'));
            }
            // Last analysis
            const lastAnalysis = this.blarifyIntegration.getLastAnalysis();
            if (lastAnalysis) {
                items.push(new StatusItem(`Last analysis: ${new Date(lastAnalysis).toLocaleString()}`, 'history'));
            }
            return items;
        }
        return [];
    }
}
class StatusItem extends vscode.TreeItem {
    constructor(label, icon, tooltip) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.label = label;
        this.icon = icon;
        this.tooltip = tooltip;
        this.iconPath = new vscode.ThemeIcon(icon);
        if (tooltip) {
            this.tooltip = tooltip;
        }
    }
}
//# sourceMappingURL=extension.js.map