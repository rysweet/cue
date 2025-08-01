import * as vscode from 'vscode';
import { Neo4jManager } from './neo4jManager';
import { BlarifyIntegration } from './blarifyIntegration';
import { GraphDataProvider } from './graphDataProvider';
import { VisualizationPanel } from './visualizationPanel';
import { StatusBarManager } from './statusBarManager';
import { ConfigurationManager } from './configurationManager';

let neo4jManager: Neo4jManager;
let blarifyIntegration: BlarifyIntegration;
let graphDataProvider: GraphDataProvider;
let statusBarManager: StatusBarManager;
let configManager: ConfigurationManager;
let outputChannel: vscode.OutputChannel;

// Setup state tracking
const setupState = {
    isSetupComplete: false,
    canPromptForAnalysis(): boolean {
        return this.isSetupComplete;
    }
};

export async function activate(context: vscode.ExtensionContext) {
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
        configManager = new ConfigurationManager();
        outputChannel.appendLine('Configuration manager initialized');
    } catch (error) {
        outputChannel.appendLine(`ERROR initializing configuration manager: ${error}`);
        // Create a minimal config manager
        configManager = new ConfigurationManager();
    }
    
    try {
        statusBarManager = new StatusBarManager();
        context.subscriptions.push(statusBarManager);
        outputChannel.appendLine('Status bar manager initialized');
    } catch (error) {
        outputChannel.appendLine(`ERROR initializing status bar: ${error}`);
    }
    
    try {
        neo4jManager = new Neo4jManager(configManager, context.extensionPath);
        context.subscriptions.push(neo4jManager);
        outputChannel.appendLine('Neo4j manager initialized');
    } catch (error) {
        outputChannel.appendLine(`ERROR initializing Neo4j manager: ${error}`);
        // This might happen if bundled module fails to load, but we still want commands to work
    }
    
    try {
        blarifyIntegration = new BlarifyIntegration(configManager, context.extensionPath);
        outputChannel.appendLine('Blarify integration initialized');
    } catch (error) {
        outputChannel.appendLine(`ERROR initializing Blarify integration: ${error}`);
    }
    
    try {
        graphDataProvider = new GraphDataProvider(neo4jManager, configManager);
        outputChannel.appendLine('Graph data provider initialized');
    } catch (error) {
        outputChannel.appendLine(`ERROR initializing graph data provider: ${error}`);
    }
    
    // Skip Docker startup in test environment
    const isTestMode = context.extensionMode === vscode.ExtensionMode.Test;
    outputChannel.appendLine(`Extension mode: ${context.extensionMode} (Test mode: ${isTestMode})`);
    if (!isTestMode) {
        // Start background tasks asynchronously to not block activation
        setTimeout(async () => {
            // Run all setup tasks (including Neo4j)
            await runSetupTasks();
            
            // Only show prompt when setup is complete
            if (setupState.canPromptForAnalysis()) {
                await promptForInitialAnalysis();
            }
        }, 1000); // Delay to ensure extension is fully activated
    }
    
    async function runSetupTasks(): Promise<void> {
        try {
            outputChannel.appendLine('Running setup tasks...');
            
            // Check Azure OpenAI configuration
            if (configManager && !configManager.isConfigured()) {
                const configured = await configManager.promptForConfiguration();
                if (!configured) {
                    vscode.window.showInformationMessage(
                        'Some features may be limited without Azure OpenAI configuration. You can configure it later in settings.'
                    );
                }
            }
            
            // Start Neo4j as part of setup
            outputChannel.appendLine('Starting Neo4j...');
            if (neo4jManager && statusBarManager) {
                statusBarManager.setStatus('Starting Neo4j...', 'sync~spin');
                try {
                    await neo4jManager.ensureRunning();
                    statusBarManager.setStatus('Neo4j ready', 'database');
                    outputChannel.appendLine('Neo4j started successfully');
                } catch (error) {
                    statusBarManager.setStatus('Neo4j offline', 'warning');
                    outputChannel.appendLine(`Failed to start Neo4j: ${error}`);
                    throw new Error(`Neo4j startup failed: ${error}`);
                }
            }
            
            // Add any other setup tasks here
            // e.g., checking Python, installing dependencies, etc.
            
            setupState.isSetupComplete = true;
            outputChannel.appendLine('Setup tasks completed');
        } catch (error) {
            outputChannel.appendLine(`Error during setup: ${error}`);
            setupState.isSetupComplete = false;
        }
    }
    
    async function promptForInitialAnalysis(): Promise<void> {
        outputChannel.appendLine('Prompting for initial analysis...');
        const shouldIngest = await vscode.window.showInformationMessage(
            'Would you like to analyze your workspace with Blarify?',
            'Yes', 'Not now'
        );
        
        if (shouldIngest === 'Yes') {
            await ingestWorkspace();
        }
    }
    
    // Register commands
    outputChannel.appendLine('Registering commands...');
    try {
        const showVisualizationCommand = vscode.commands.registerCommand(
            'blarifyVisualizer.showVisualization',
            () => showVisualization(context)
        );
        outputChannel.appendLine('  - showVisualization registered');
        
        const ingestWorkspaceCommand = vscode.commands.registerCommand(
            'blarifyVisualizer.ingestWorkspace',
            async () => {
                outputChannel.appendLine('Command: ingestWorkspace invoked');
                outputChannel.appendLine(`  neo4jManager: ${neo4jManager ? 'initialized' : 'NOT INITIALIZED'}`);
                outputChannel.appendLine(`  blarifyIntegration: ${blarifyIntegration ? 'initialized' : 'NOT INITIALIZED'}`);
                
                if (!neo4jManager || !blarifyIntegration) {
                    const message = 'Extension components not fully initialized. Please reload the window.';
                    outputChannel.appendLine(`ERROR: ${message}`);
                    vscode.window.showErrorMessage(message);
                    return;
                }
                
                await ingestWorkspace();
            }
        );
        outputChannel.appendLine('  - ingestWorkspace registered');
        
        const updateGraphCommand = vscode.commands.registerCommand(
            'blarifyVisualizer.updateGraph',
            updateGraph
        );
        outputChannel.appendLine('  - updateGraph registered');
        
        const searchGraphCommand = vscode.commands.registerCommand(
            'blarifyVisualizer.searchGraph',
            searchGraph
        );
        outputChannel.appendLine('  - searchGraph registered');
        
        const restartNeo4jCommand = vscode.commands.registerCommand(
            'blarifyVisualizer.restartNeo4j',
            restartNeo4j
        );
        outputChannel.appendLine('  - restartNeo4j registered');
        
        context.subscriptions.push(
            showVisualizationCommand,
            ingestWorkspaceCommand,
            updateGraphCommand,
            searchGraphCommand,
            restartNeo4jCommand
        );
        outputChannel.appendLine('All commands registered successfully');
    } catch (error) {
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
    } catch (error) {
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

export function deactivate() {
    // Cleanup will be handled by dispose methods
}

async function showVisualization(context: vscode.ExtensionContext) {
    try {
        const panel = VisualizationPanel.createOrShow(context.extensionUri);
        panel.setDataProvider(graphDataProvider);
        await panel.loadGraph();
    } catch (error) {
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
        await neo4jManager.ensureRunning();
    } catch (error) {
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
            
            const result = await blarifyIntegration.analyzeWorkspace(
                workspaceFolder.uri.fsPath,
                progress,
                token
            );
            
            progress.report({ increment: 50, message: 'Saving to Neo4j...' });
            await neo4jManager.saveGraph(result.nodes, result.edges);
            
            progress.report({ increment: 100, message: 'Complete!' });
            if (statusBarManager) {
                statusBarManager.setStatus('Analysis complete', 'check');
            }
            
            vscode.window.showInformationMessage(
                `Analysis complete: ${result.nodes.length} nodes, ${result.edges.length} relationships`
            );
            
            // Refresh any open visualizations
            VisualizationPanel.refreshAll();
        } catch (error) {
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
        const panel = VisualizationPanel.currentPanel;
        if (panel) {
            panel.search(query);
        } else {
            // Open visualization first
            vscode.window.showInformationMessage('Please open the visualization first');
            await vscode.commands.executeCommand('blarifyVisualizer.showVisualization');
            // Delay to ensure panel is ready
            setTimeout(() => {
                VisualizationPanel.currentPanel?.search(query);
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
            const container = (neo4jManager as any).docker.getContainer(status.containerId);
            try {
                await container.stop();
                await container.remove();
            } catch (e) {
                // Ignore errors
            }
        }
        
        // Start fresh
        await neo4jManager.ensureRunning();
        statusBarManager.setStatus('Neo4j ready', 'database');
        vscode.window.showInformationMessage('Neo4j restarted successfully');
    } catch (error) {
        statusBarManager.setStatus('Neo4j failed', 'error');
        vscode.window.showErrorMessage(`Failed to restart Neo4j: ${error}`);
    }
}

class StatusViewProvider implements vscode.TreeDataProvider<StatusItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<StatusItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    
    constructor(
        private neo4jManager: Neo4jManager,
        private blarifyIntegration: BlarifyIntegration
    ) {}
    
    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
    
    getTreeItem(element: StatusItem): vscode.TreeItem {
        return element;
    }
    
    async getChildren(element?: StatusItem): Promise<StatusItem[]> {
        if (!element) {
            const items: StatusItem[] = [];
            
            // Neo4j status
            const neo4jStatus = await this.neo4jManager.getStatus();
            items.push(new StatusItem(
                `Neo4j: ${neo4jStatus.running ? 'Running' : 'Stopped'}`,
                neo4jStatus.running ? 'database' : 'database-off',
                neo4jStatus.details
            ));
            
            // Graph statistics
            if (neo4jStatus.running) {
                const stats = await this.neo4jManager.getGraphStats();
                items.push(new StatusItem(
                    `Nodes: ${stats.nodeCount}`,
                    'symbol-class'
                ));
                items.push(new StatusItem(
                    `Relationships: ${stats.relationshipCount}`,
                    'references'
                ));
            }
            
            // Last analysis
            const lastAnalysis = this.blarifyIntegration.getLastAnalysis();
            if (lastAnalysis) {
                items.push(new StatusItem(
                    `Last analysis: ${new Date(lastAnalysis).toLocaleString()}`,
                    'history'
                ));
            }
            
            return items;
        }
        return [];
    }
}

class StatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly icon: string,
        public readonly tooltip?: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.iconPath = new vscode.ThemeIcon(icon);
        if (tooltip) {
            this.tooltip = tooltip;
        }
    }
}