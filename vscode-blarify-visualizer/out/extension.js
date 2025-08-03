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
// Neo4j initialization promise to prevent concurrent calls
let neo4jInitPromise = null;
// Setup state tracking
const setupState = {
    isSetupComplete: false,
    canPromptForAnalysis() {
        return this.isSetupComplete;
    }
};
async function activate(context) {
    console.log('Blarify Visualizer is now active!');
    // Create output channel for debugging
    outputChannel = vscode.window.createOutputChannel('Blarify Visualizer');
    context.subscriptions.push(outputChannel);
    outputChannel.appendLine('=== Blarify Visualizer extension activation started ===');
    outputChannel.appendLine(`Extension path: ${context.extensionPath}`);
    outputChannel.appendLine(`Extension mode: ${context.extensionMode}`);
    outputChannel.show();
    // Initialize components with error handling
    try {
        configManager = new configurationManager_1.ConfigurationManager();
        outputChannel.appendLine('Configuration manager initialized');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR initializing configuration manager: ${error}`);
        // Create a minimal config manager
        configManager = new configurationManager_1.ConfigurationManager();
    }
    try {
        statusBarManager = new statusBarManager_1.StatusBarManager();
        context.subscriptions.push(statusBarManager);
        outputChannel.appendLine('Status bar manager initialized');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR initializing status bar: ${error}`);
    }
    try {
        neo4jManager = new neo4jManager_1.Neo4jManager(configManager, context.extensionPath);
        context.subscriptions.push(neo4jManager);
        outputChannel.appendLine('Neo4j manager initialized');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR initializing Neo4j manager: ${error}`);
        // This might happen if bundled module fails to load, but we still want commands to work
    }
    try {
        blarifyIntegration = new blarifyIntegration_1.BlarifyIntegration(configManager, context.extensionPath, neo4jManager);
        outputChannel.appendLine('Blarify integration initialized');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR initializing Blarify integration: ${error}`);
    }
    try {
        graphDataProvider = new graphDataProvider_1.GraphDataProvider(neo4jManager, configManager);
        outputChannel.appendLine('Graph data provider initialized');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR initializing graph data provider: ${error}`);
    }
    // Skip Docker startup in test environment
    const isTestMode = context.extensionMode === vscode.ExtensionMode.Test;
    outputChannel.appendLine(`Extension mode: ${context.extensionMode} (Test mode: ${isTestMode})`);
    if (!isTestMode) {
        // Start background tasks asynchronously to not block activation
        setTimeout(async () => {
            try {
                // Run all setup tasks (including Python and Neo4j)
                await runSetupTasks();
                // Only show prompt when setup is complete
                if (setupState.canPromptForAnalysis()) {
                    await promptForInitialAnalysis();
                }
            }
            catch (error) {
                outputChannel.appendLine(`Background setup failed: ${error}`);
                // Don't show error to user here as it's handled within runSetupTasks
                // Setup can be retried when user tries to use ingestion command
            }
        }, 1000); // Delay to ensure extension is fully activated
    }
    async function runSetupTasks() {
        try {
            outputChannel.appendLine('Running setup tasks...');
            // Check Azure OpenAI configuration
            if (configManager && !configManager.isConfigured()) {
                const configured = await configManager.promptForConfiguration();
                if (!configured) {
                    vscode.window.showInformationMessage('Some features may be limited without Azure OpenAI configuration. You can configure it later in settings.');
                }
            }
            // Set up Python environment (including Blarify dependencies)
            outputChannel.appendLine('Setting up Python environment...');
            if (blarifyIntegration && statusBarManager) {
                statusBarManager.setStatus('Setting up Python...', 'sync~spin');
                try {
                    // This will trigger the Python environment setup including pip install
                    const pythonEnv = blarifyIntegration.pythonEnv;
                    await pythonEnv.ensureSetup();
                    outputChannel.appendLine('Python environment setup completed');
                }
                catch (error) {
                    statusBarManager.setStatus('Python setup failed', 'error');
                    outputChannel.appendLine(`Failed to set up Python environment: ${error}`);
                    vscode.window.showErrorMessage(`Blarify setup failed: ${error}. Please check the output channel for details.`);
                    throw new Error(`Python environment setup failed: ${error}`);
                }
            }
            // Start Neo4j as part of setup
            outputChannel.appendLine('Starting Neo4j...');
            if (neo4jManager && statusBarManager) {
                statusBarManager.setStatus('Starting Neo4j...', 'sync~spin');
                try {
                    await ensureNeo4jRunning();
                    statusBarManager.setStatus('Neo4j ready', 'database');
                    outputChannel.appendLine('Neo4j started successfully');
                }
                catch (error) {
                    statusBarManager.setStatus('Neo4j offline', 'warning');
                    outputChannel.appendLine(`Failed to start Neo4j: ${error}`);
                    // Don't throw error for Neo4j - it can be started later
                    vscode.window.showWarningMessage('Neo4j failed to start automatically. You can restart it manually using the "Restart Neo4j" command.');
                }
            }
            setupState.isSetupComplete = true;
            outputChannel.appendLine('Setup tasks completed successfully');
            if (statusBarManager) {
                statusBarManager.setStatus('Ready', 'check');
            }
        }
        catch (error) {
            outputChannel.appendLine(`Error during setup: ${error}`);
            setupState.isSetupComplete = false;
            if (statusBarManager) {
                statusBarManager.setStatus('Setup failed', 'error');
            }
            throw error; // Re-throw to be handled by caller
        }
    }
    async function promptForInitialAnalysis() {
        outputChannel.appendLine('Prompting for initial analysis...');
        const shouldIngest = await vscode.window.showInformationMessage('Would you like to analyze your workspace with Blarify?', 'Yes', 'Not now');
        if (shouldIngest === 'Yes') {
            await ingestWorkspace();
        }
    }
    // Register commands
    outputChannel.appendLine('Registering commands...');
    try {
        const showVisualizationCommand = vscode.commands.registerCommand('blarifyVisualizer.showVisualization', () => showVisualization(context));
        outputChannel.appendLine('  - showVisualization registered');
        const ingestWorkspaceCommand = vscode.commands.registerCommand('blarifyVisualizer.ingestWorkspace', async () => {
            outputChannel.appendLine('Command: ingestWorkspace invoked');
            outputChannel.appendLine(`  neo4jManager: ${neo4jManager ? 'initialized' : 'NOT INITIALIZED'}`);
            outputChannel.appendLine(`  blarifyIntegration: ${blarifyIntegration ? 'initialized' : 'NOT INITIALIZED'}`);
            outputChannel.appendLine(`  setupState.isSetupComplete: ${setupState.isSetupComplete}`);
            if (!neo4jManager || !blarifyIntegration) {
                const message = 'Extension components not fully initialized. Please reload the window.';
                outputChannel.appendLine(`ERROR: ${message}`);
                vscode.window.showErrorMessage(message);
                return;
            }
            // Ensure setup is complete before allowing ingestion
            if (!setupState.isSetupComplete) {
                outputChannel.appendLine('Setup not complete, waiting for setup to finish...');
                statusBarManager?.setStatus('Waiting for setup...', 'sync~spin');
                // Wait for setup with progress indication
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: "Waiting for Blarify setup to complete",
                    cancellable: false
                }, async (progress) => {
                    progress.report({ message: "Setting up Blarify environment..." });
                    // Poll for setup completion with timeout
                    const maxWaitTime = 300000; // 5 minutes
                    const pollInterval = 1000; // 1 second
                    let elapsed = 0;
                    while (!setupState.isSetupComplete && elapsed < maxWaitTime) {
                        await new Promise(resolve => setTimeout(resolve, pollInterval));
                        elapsed += pollInterval;
                        progress.report({
                            message: `Setting up Blarify environment... (${Math.floor(elapsed / 1000)}s)`
                        });
                    }
                    if (!setupState.isSetupComplete) {
                        throw new Error('Setup timeout: Blarify setup did not complete within 5 minutes');
                    }
                });
            }
            await ingestWorkspace();
        });
        outputChannel.appendLine('  - ingestWorkspace registered');
        const updateGraphCommand = vscode.commands.registerCommand('blarifyVisualizer.updateGraph', updateGraph);
        outputChannel.appendLine('  - updateGraph registered');
        const searchGraphCommand = vscode.commands.registerCommand('blarifyVisualizer.searchGraph', searchGraph);
        outputChannel.appendLine('  - searchGraph registered');
        const restartNeo4jCommand = vscode.commands.registerCommand('blarifyVisualizer.restartNeo4j', restartNeo4j);
        outputChannel.appendLine('  - restartNeo4j registered');
        context.subscriptions.push(showVisualizationCommand, ingestWorkspaceCommand, updateGraphCommand, searchGraphCommand, restartNeo4jCommand);
        outputChannel.appendLine('All commands registered successfully');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR registering commands: ${error}`);
        throw error;
    }
    // Register status view provider
    outputChannel.appendLine('Registering tree view...');
    try {
        const statusProvider = new StatusViewProvider(neo4jManager, blarifyIntegration);
        const treeView = vscode.window.createTreeView('blarifyStatus', {
            treeDataProvider: statusProvider,
            showCollapseAll: false
        });
        context.subscriptions.push(treeView);
        outputChannel.appendLine('Tree view registered successfully');
        // Refresh the view to ensure it's populated
        statusProvider.refresh();
        outputChannel.appendLine('Tree view refreshed');
    }
    catch (error) {
        outputChannel.appendLine(`ERROR registering tree view: ${error}`);
        throw error;
    }
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
    outputChannel.appendLine('=== Extension activation completed successfully ===');
    // List all registered commands for debugging
    vscode.commands.getCommands().then(commands => {
        const blarifyCommands = commands.filter(cmd => cmd.startsWith('blarifyVisualizer.'));
        outputChannel.appendLine(`Registered Blarify commands: ${blarifyCommands.join(', ')}`);
    });
}
exports.activate = activate;
function deactivate() {
    // Cleanup will be handled by dispose methods
    // Reset the initialization promise
    neo4jInitPromise = null;
}
exports.deactivate = deactivate;
// Helper function to ensure Neo4j is running with singleton pattern
async function ensureNeo4jRunning() {
    outputChannel.appendLine('[Neo4j Singleton] ensureNeo4jRunning called');
    // If already initializing, return the existing promise
    if (neo4jInitPromise) {
        outputChannel.appendLine('[Neo4j Singleton] Returning existing initialization promise');
        return neo4jInitPromise;
    }
    // Create new initialization promise
    outputChannel.appendLine('[Neo4j Singleton] Creating new initialization promise');
    neo4jInitPromise = neo4jManager.ensureRunning()
        .then(() => {
        outputChannel.appendLine('[Neo4j Singleton] Neo4j initialization successful');
    })
        .catch((error) => {
        outputChannel.appendLine(`[Neo4j Singleton] Neo4j initialization failed: ${error}`);
        // Reset promise on failure so it can be retried
        neo4jInitPromise = null;
        throw error;
    });
    return neo4jInitPromise;
}
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
    // Check if components are initialized
    if (!blarifyIntegration) {
        vscode.window.showErrorMessage('Blarify integration not initialized. Please reload the window.');
        return;
    }
    if (!neo4jManager) {
        vscode.window.showErrorMessage('Neo4j manager not initialized. Please reload the window.');
        return;
    }
    // Ensure Neo4j is running before attempting analysis
    try {
        await ensureNeo4jRunning();
    }
    catch (error) {
        vscode.window.showErrorMessage(`Neo4j is not running: ${error}. Please restart Neo4j and try again.`);
        return;
    }
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
            if (statusBarManager) {
                statusBarManager.setStatus('Analyzing...', 'sync~spin');
            }
            progress.report({ increment: 0, message: 'Starting analysis...' });
            const result = await blarifyIntegration.analyzeWorkspace(workspaceFolder.uri.fsPath, progress, token);
            progress.report({ increment: 50, message: 'Saving to Neo4j...' });
            await neo4jManager.saveGraph(result.nodes, result.edges);
            progress.report({ increment: 100, message: 'Complete!' });
            if (statusBarManager) {
                statusBarManager.setStatus('Analysis complete', 'check');
            }
            vscode.window.showInformationMessage(`Analysis complete: ${result.nodes.length} nodes, ${result.edges.length} relationships`);
            // Refresh any open visualizations
            visualizationPanel_1.VisualizationPanel.refreshAll();
        }
        catch (error) {
            if (statusBarManager) {
                statusBarManager.setStatus('Analysis failed', 'error');
            }
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
        // Reset the promise since we're restarting
        neo4jInitPromise = null;
        await ensureNeo4jRunning();
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