import * as vscode from 'vscode';
import { Neo4jManager } from './neo4jManager';
import { cueIntegration } from './cueIntegration';
import { GraphDataProvider } from './graphDataProvider';
import { VisualizationPanel } from './visualizationPanel';
import { StatusBarManager } from './statusBarManager';
import { ConfigurationManager } from './configurationManager';
import { PythonEnvironment } from './pythonEnvironment';

let neo4jManager: Neo4jManager;
let cueIntegration: cueIntegration;
let graphDataProvider: GraphDataProvider;
let statusBarManager: StatusBarManager;
let configManager: ConfigurationManager;
let outputChannel: vscode.OutputChannel;

// Neo4j initialization promise to prevent concurrent calls
let neo4jInitPromise: Promise<void> | null = null;

// Setup state tracking
const setupState = {
    isSetupComplete: false,
    canPromptForAnalysis(): boolean {
        return this.isSetupComplete;
    }
};

export async function activate(context: vscode.ExtensionContext) {
    console.log('cue Visualizer is now active!');
    
    // Create output channel for debugging
    outputChannel = vscode.window.createOutputChannel('cue Visualizer');
    context.subscriptions.push(outputChannel);
    outputChannel.appendLine('=== cue Visualizer extension activation started ===');
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
        cueIntegration = new cueIntegration(configManager, context.extensionPath, neo4jManager);
        outputChannel.appendLine('cue integration initialized');
    } catch (error) {
        outputChannel.appendLine(`ERROR initializing cue integration: ${error}`);
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
            try {
                // Run all setup tasks (including Python and Neo4j)
                await runSetupTasks();
                
                // Only show prompt when setup is complete
                if (setupState.canPromptForAnalysis()) {
                    await promptForInitialAnalysis();
                }
            } catch (error) {
                outputChannel.appendLine(`Background setup failed: ${error}`);
                // Don't show error to user here as it's handled within runSetupTasks
                // Setup can be retried when user tries to use ingestion command
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
            
            // Set up Python environment (including cue dependencies)
            outputChannel.appendLine('Setting up Python environment...');
            if (cueIntegration && statusBarManager) {
                statusBarManager.setStatus('Setting up Python...', 'sync~spin');
                try {
                    // This will trigger the Python environment setup including pip install
                    const pythonEnv = (cueIntegration as any).pythonEnv as PythonEnvironment;
                    await pythonEnv.ensureSetup();
                    outputChannel.appendLine('Python environment setup completed');
                } catch (error) {
                    statusBarManager.setStatus('Python setup failed', 'error');
                    outputChannel.appendLine(`Failed to set up Python environment: ${error}`);
                    vscode.window.showErrorMessage(
                        `cue setup failed: ${error}. Please check the output channel for details.`
                    );
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
                } catch (error) {
                    statusBarManager.setStatus('Neo4j offline', 'warning');
                    outputChannel.appendLine(`Failed to start Neo4j: ${error}`);
                    // Don't throw error for Neo4j - it can be started later
                    vscode.window.showWarningMessage(
                        'Neo4j failed to start automatically. You can restart it manually using the "Restart Neo4j" command.'
                    );
                }
            }
            
            setupState.isSetupComplete = true;
            outputChannel.appendLine('Setup tasks completed successfully');
            if (statusBarManager) {
                statusBarManager.setStatus('Ready', 'check');
            }
        } catch (error) {
            outputChannel.appendLine(`Error during setup: ${error}`);
            setupState.isSetupComplete = false;
            if (statusBarManager) {
                statusBarManager.setStatus('Setup failed', 'error');
            }
            throw error; // Re-throw to be handled by caller
        }
    }
    
    async function promptForInitialAnalysis(): Promise<void> {
        outputChannel.appendLine('Prompting for initial analysis...');
        const shouldIngest = await vscode.window.showInformationMessage(
            'Would you like to analyze your workspace with cue?',
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
            'cueVisualizer.showVisualization',
            () => showVisualization(context)
        );
        outputChannel.appendLine('  - showVisualization registered');
        
        const ingestWorkspaceCommand = vscode.commands.registerCommand(
            'cueVisualizer.ingestWorkspace',
            async () => {
                outputChannel.appendLine('Command: ingestWorkspace invoked');
                outputChannel.appendLine(`  neo4jManager: ${neo4jManager ? 'initialized' : 'NOT INITIALIZED'}`);
                outputChannel.appendLine(`  cueIntegration: ${cueIntegration ? 'initialized' : 'NOT INITIALIZED'}`);
                outputChannel.appendLine(`  setupState.isSetupComplete: ${setupState.isSetupComplete}`);
                
                if (!neo4jManager || !cueIntegration) {
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
                        title: "Waiting for cue setup to complete",
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ message: "Setting up cue environment..." });
                        
                        // Poll for setup completion with timeout
                        const maxWaitTime = 300000; // 5 minutes
                        const pollInterval = 1000; // 1 second
                        let elapsed = 0;
                        
                        while (!setupState.isSetupComplete && elapsed < maxWaitTime) {
                            await new Promise(resolve => setTimeout(resolve, pollInterval));
                            elapsed += pollInterval;
                            progress.report({ 
                                message: `Setting up cue environment... (${Math.floor(elapsed/1000)}s)` 
                            });
                        }
                        
                        if (!setupState.isSetupComplete) {
                            throw new Error('Setup timeout: cue setup did not complete within 5 minutes');
                        }
                    });
                }
                
                await ingestWorkspace();
            }
        );
        outputChannel.appendLine('  - ingestWorkspace registered');
        
        const updateGraphCommand = vscode.commands.registerCommand(
            'cueVisualizer.updateGraph',
            updateGraph
        );
        outputChannel.appendLine('  - updateGraph registered');
        
        const searchGraphCommand = vscode.commands.registerCommand(
            'cueVisualizer.searchGraph',
            searchGraph
        );
        outputChannel.appendLine('  - searchGraph registered');
        
        const restartNeo4jCommand = vscode.commands.registerCommand(
            'cueVisualizer.restartNeo4j',
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
        const statusProvider = new StatusViewProvider(neo4jManager, cueIntegration);
        const treeView = vscode.window.createTreeView('cueStatus', {
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
        const cueCommands = commands.filter(cmd => cmd.startsWith('cueVisualizer.'));
        outputChannel.appendLine(`Registered cue commands: ${cueCommands.join(', ')}`);
    });
}

export function deactivate() {
    // Cleanup will be handled by dispose methods
    // Reset the initialization promise
    neo4jInitPromise = null;
}

// Helper function to ensure Neo4j is running with singleton pattern
async function ensureNeo4jRunning(): Promise<void> {
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
    if (!cueIntegration) {
        vscode.window.showErrorMessage('cue integration not initialized. Please reload the window.');
        return;
    }
    
    if (!neo4jManager) {
        vscode.window.showErrorMessage('Neo4j manager not initialized. Please reload the window.');
        return;
    }
    
    // Ensure Neo4j is running before attempting analysis
    try {
        await ensureNeo4jRunning();
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
        title: 'Analyzing workspace with cue',
        cancellable: true
    }, async (progress, token) => {
        try {
            if (statusBarManager) {
                statusBarManager.setStatus('Analyzing...', 'sync~spin');
            }
            progress.report({ increment: 0, message: 'Starting analysis...' });
            
            const result = await cueIntegration.analyzeWorkspace(
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
            await vscode.commands.executeCommand('cueVisualizer.showVisualization');
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
        // Reset the promise since we're restarting
        neo4jInitPromise = null;
        await ensureNeo4jRunning();
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
        private cueIntegration: cueIntegration
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
            const lastAnalysis = this.cueIntegration.getLastAnalysis();
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