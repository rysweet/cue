import * as vscode from 'vscode';
import * as path from 'path';
import { GraphDataProvider, GraphData } from './graphDataProvider';

export class VisualizationPanel {
    public static currentPanel: VisualizationPanel | undefined;
    private static readonly viewType = 'blarifyVisualization';
    
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _dataProvider?: GraphDataProvider;
    private _currentData?: GraphData;
    
    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        
        // If we already have a panel, show it
        if (VisualizationPanel.currentPanel) {
            VisualizationPanel.currentPanel._panel.reveal(column);
            return VisualizationPanel.currentPanel;
        }
        
        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            VisualizationPanel.viewType,
            'Blarify Code Visualization',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media'),
                    vscode.Uri.joinPath(extensionUri, 'node_modules')
                ]
            }
        );
        
        VisualizationPanel.currentPanel = new VisualizationPanel(panel, extensionUri);
        return VisualizationPanel.currentPanel;
    }
    
    public static refreshAll() {
        if (VisualizationPanel.currentPanel) {
            VisualizationPanel.currentPanel.refresh();
        }
    }
    
    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        
        // Set the webview's initial html content
        this._update();
        
        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                this._handleMessage(message);
            },
            null,
            this._disposables
        );
    }
    
    public setDataProvider(provider: GraphDataProvider) {
        this._dataProvider = provider;
    }
    
    public async loadGraph(nodeId?: string) {
        if (!this._dataProvider) {
            vscode.window.showErrorMessage('No data provider set');
            return;
        }
        
        try {
            const data = nodeId 
                ? await this._dataProvider.getNodeNeighbors(nodeId)
                : await this._dataProvider.getGraphData();
            
            this._currentData = data;
            this._panel.webview.postMessage({
                command: 'loadGraph',
                data
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load graph: ${error}`);
        }
    }
    
    public search(query: string) {
        this._panel.webview.postMessage({
            command: 'search',
            query
        });
    }
    
    public refresh() {
        this.loadGraph();
    }
    
    private async _handleMessage(message: any) {
        switch (message.command) {
            case 'ready':
                // Webview is ready, load initial data
                await this.loadGraph();
                break;
                
            case 'selectNode':
                await this._handleNodeSelection(message.nodeId);
                break;
                
            case 'expandNode':
                await this._handleNodeExpansion(message.nodeId);
                break;
                
            case 'openFile':
                await this._handleOpenFile(message.path);
                break;
                
            case 'showDetails':
                await this._handleShowDetails(message.nodeId);
                break;
                
            case 'filterByType':
                await this._handleFilterByType(message.types);
                break;
                
            case 'changeLayout':
                // Layout change is handled client-side
                break;
                
            case 'error':
                vscode.window.showErrorMessage(message.text);
                break;
        }
    }
    
    private async _handleNodeSelection(nodeId: string) {
        if (!this._dataProvider) return;
        
        const details = await this._dataProvider.getNodeDetails(nodeId);
        if (details) {
            this._panel.webview.postMessage({
                command: 'showNodeDetails',
                node: details
            });
        }
    }
    
    private async _handleNodeExpansion(nodeId: string) {
        if (!this._dataProvider) return;
        
        const neighbors = await this._dataProvider.getNodeNeighbors(nodeId);
        this._panel.webview.postMessage({
            command: 'expandNode',
            nodeId,
            data: neighbors
        });
    }
    
    private async _handleOpenFile(filePath: string) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return;
        
        const uri = vscode.Uri.file(path.join(workspaceFolder.uri.fsPath, filePath));
        try {
            await vscode.window.showTextDocument(uri);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open file: ${filePath}`);
        }
    }
    
    private async _handleShowDetails(nodeId: string) {
        // This could open a separate detail view or sidebar
        const details = await this._dataProvider?.getNodeDetails(nodeId);
        if (details) {
            const detailsJson = JSON.stringify(details.properties, null, 2);
            const doc = await vscode.workspace.openTextDocument({
                content: detailsJson,
                language: 'json'
            });
            await vscode.window.showTextDocument(doc, { preview: true });
        }
    }
    
    private async _handleFilterByType(types: string[]) {
        if (!this._dataProvider) return;
        
        const data = await this._dataProvider.getGraphData({ nodeTypes: types });
        this._currentData = data;
        this._panel.webview.postMessage({
            command: 'loadGraph',
            data
        });
    }
    
    private _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Blarify Code Visualization';
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }
    
    private _getHtmlForWebview(webview: vscode.Webview) {
        // Local path to main script run in the webview
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'visualization.js');
        const scriptUri = webview.asWebviewUri(scriptPathOnDisk);
        
        // Local path to css styles
        const stylePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'visualization.css');
        const styleUri = webview.asWebviewUri(stylePathOnDisk);
        
        // Three.js from node_modules
        const threePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'node_modules', 'three', 'build', 'three.module.js');
        const threeUri = webview.asWebviewUri(threePathOnDisk);
        
        // Use a nonce to only allow specific scripts to be run
        const nonce = getNonce();
        
        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
                <link href="${styleUri}" rel="stylesheet">
                <title>Blarify Code Visualization</title>
            </head>
            <body>
                <div id="container">
                    <div id="toolbar">
                        <div class="toolbar-group">
                            <input type="text" id="searchInput" placeholder="Search nodes..." />
                            <button id="searchBtn">Search</button>
                            <button id="clearSearchBtn">Clear</button>
                        </div>
                        <div class="toolbar-group">
                            <label>Layout:</label>
                            <select id="layoutSelect">
                                <option value="force-directed">Force Directed</option>
                                <option value="hierarchical">Hierarchical</option>
                                <option value="circular">Circular</option>
                            </select>
                        </div>
                        <div class="toolbar-group">
                            <button id="resetViewBtn">Reset View</button>
                            <button id="fitToScreenBtn">Fit to Screen</button>
                        </div>
                    </div>
                    <div id="main-content">
                        <div id="visualization"></div>
                        <div id="sidebar">
                            <div id="legend">
                                <h3>Legend</h3>
                                <div id="legend-content"></div>
                            </div>
                            <div id="details">
                                <h3>Details</h3>
                                <div id="details-content">
                                    <p>Select a node to view details</p>
                                </div>
                            </div>
                            <div id="filters">
                                <h3>Filters</h3>
                                <div id="filter-content"></div>
                            </div>
                        </div>
                    </div>
                    <div id="status-bar">
                        <span id="node-count">0 nodes</span>
                        <span id="edge-count">0 edges</span>
                        <span id="selected-info"></span>
                    </div>
                </div>
                <script nonce="${nonce}">
                    window.threeModuleUrl = '${threeUri}';
                </script>
                <script nonce="${nonce}" src="${scriptUri}"></script>
            </body>
            </html>`;
    }
    
    public dispose() {
        VisualizationPanel.currentPanel = undefined;
        
        // Clean up our resources
        this._panel.dispose();
        
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}