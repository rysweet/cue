import * as vscode from 'vscode';

export interface AzureOpenAIConfig {
    apiKey: string;
    endpoint: string;
    deploymentName: string;
}

export interface Neo4jConfig {
    uri: string;
    username: string;
    password: string;
}

export interface VisualizationConfig {
    nodeLimit: number;
    defaultLayout: 'force-directed' | 'hierarchical' | 'circular';
}

export class ConfigurationManager {
    private readonly configSection = 'blarifyVisualizer';
    
    getAzureOpenAIConfig(): AzureOpenAIConfig {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return {
            apiKey: config.get('azureOpenAI.apiKey', ''),
            endpoint: config.get('azureOpenAI.endpoint', ''),
            deploymentName: config.get('azureOpenAI.deploymentName', 'gpt-4')
        };
    }
    
    getNeo4jConfig(): Neo4jConfig {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return {
            uri: config.get('neo4j.uri', 'bolt://localhost:7687'),
            username: config.get('neo4j.username', 'neo4j'),
            password: config.get('neo4j.password', '')
        };
    }
    
    getVisualizationConfig(): VisualizationConfig {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return {
            nodeLimit: config.get('visualization.nodeLimit', 500),
            defaultLayout: config.get('visualization.defaultLayout', 'force-directed')
        };
    }
    
    getAutoUpdate(): boolean {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get('ingestion.autoUpdate', true);
    }
    
    getExcludePatterns(): string[] {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get('ingestion.excludePatterns', []);
    }
    
    isConfigured(): boolean {
        const azureConfig = this.getAzureOpenAIConfig();
        return !!(azureConfig.apiKey && azureConfig.endpoint);
    }
    
    async promptForConfiguration(): Promise<boolean> {
        const configure = await vscode.window.showInformationMessage(
            'Blarify Visualizer requires Azure OpenAI configuration for full functionality.',
            'Configure', 'Later'
        );
        
        if (configure === 'Configure') {
            await vscode.commands.executeCommand('workbench.action.openSettings', 
                '@ext:blarify.blarify-visualizer');
            return true;
        }
        
        return false;
    }
}