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

export async function activate(context: vscode.ExtensionContext) {
    console.log('Blarify Visualizer is now active!');

    // Initialize configuration manager
    configManager = new ConfigurationManager();
    
    // Initialize status bar
    statusBarManager = new StatusBarManager();
    context.subscriptions.push(statusBarManager);
    
    // Initialize Neo4j manager
    neo4jManager = new Neo4jManager(configManager);
    context.subscriptions.push(neo4jManager);
    
    // Initialize Blarify integration
    blarifyIntegration = new BlarifyIntegration(configManager);
    
    // Initialize graph data provider
    graphDataProvider = new GraphDataProvider(neo4jManager, configManager);
    
    // Skip Docker startup in test environment
    const isTestMode = context.extensionMode === vscode.ExtensionMode.Test;
    if (!isTestMode) {
        // Start Neo4j container
        statusBarManager.setStatus('Starting Neo4j...', 'sync~spin');
        try {
            await neo4jManager.ensureRunning();
            statusBarManager.setStatus('Neo4j ready', 'database');
            
            // Prompt user to ingest workspace on startup
            const shouldIngest = await vscode.window.showInformationMessage(
                'Would you like to analyze your workspace with Blarify?',
                'Yes', 'Not now'
            );
            
            if (shouldIngest === 'Yes') {
                await ingestWorkspace();
            }
        } catch (error) {
            statusBarManager.setStatus('Neo4j failed', 'error');
            vscode.window.showErrorMessage(`Failed to start Neo4j: ${error}`);
        }
    }
    
    // Register commands
    const showVisualizationCommand = vscode.commands.registerCommand(
        'blarifyVisualizer.showVisualization',
        () => showVisualization(context)
    );
    
    const ingestWorkspaceCommand = vscode.commands.registerCommand(
        'blarifyVisualizer.ingestWorkspace',
        ingestWorkspace
    );
    
    const updateGraphCommand = vscode.commands.registerCommand(
        'blarifyVisualizer.updateGraph',
        updateGraph
    );
    
    const searchGraphCommand = vscode.commands.registerCommand(
        'blarifyVisualizer.searchGraph',
        searchGraph
    );
    
    context.subscriptions.push(
        showVisualizationCommand,
        ingestWorkspaceCommand,
        updateGraphCommand,
        searchGraphCommand
    );
    
    // Register status view provider
    const statusProvider = new StatusViewProvider(neo4jManager, blarifyIntegration);
    vscode.window.registerTreeDataProvider('blarifyStatus', statusProvider);
    
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
            
            const result = await blarifyIntegration.analyzeWorkspace(
                workspaceFolder.uri.fsPath,
                progress,
                token
            );
            
            progress.report({ increment: 50, message: 'Saving to Neo4j...' });
            await neo4jManager.saveGraph(result.nodes, result.edges);
            
            progress.report({ increment: 100, message: 'Complete!' });
            statusBarManager.setStatus('Analysis complete', 'check');
            
            vscode.window.showInformationMessage(
                `Analysis complete: ${result.nodes.length} nodes, ${result.edges.length} relationships`
            );
            
            // Refresh any open visualizations
            VisualizationPanel.refreshAll();
        } catch (error) {
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