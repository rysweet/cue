import * as vscode from 'vscode';

export interface AzureOpenAIConfig {
    apiKey: string;
    endpoint: string;
    deploymentName: string;
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
    
    // Neo4j password management
    getNeo4jPassword(containerName: string): string | undefined {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const passwords = config.get<Record<string, string>>('neo4jPasswords', {});
        return passwords[containerName];
    }
    
    async saveNeo4jPassword(containerName: string, password: string): Promise<void> {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const passwords = config.get<Record<string, string>>('neo4jPasswords', {});
        passwords[containerName] = password;
        await config.update('neo4jPasswords', passwords, 
            vscode.ConfigurationTarget.Global);
    }
    
    async clearNeo4jPassword(containerName: string): Promise<void> {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const passwords = config.get<Record<string, string>>('neo4jPasswords', {});
        delete passwords[containerName];
        await config.update('neo4jPasswords', passwords, 
            vscode.ConfigurationTarget.Global);
    }
}