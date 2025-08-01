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
        try {
            const azureConfig = this.getAzureOpenAIConfig();
            return !!(azureConfig.apiKey && azureConfig.endpoint);
        } catch (error: any) {
            console.error('Failed to check configuration status:', error.message);
            return false;
        }
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
    
    // Neo4j password management with enhanced error handling
    getNeo4jPassword(containerName: string): string | undefined {
        try {
            if (!containerName) {
                throw new Error('Container name is required');
            }
            
            const config = vscode.workspace.getConfiguration(this.configSection);
            const passwords = config.get<Record<string, string>>('neo4jPasswords', {});
            
            // Validate that the password is a string if it exists
            const password = passwords[containerName];
            if (password !== undefined && typeof password !== 'string') {
                throw new Error(`Invalid password format for container ${containerName}`);
            }
            
            return password;
        } catch (error: any) {
            console.error(`Failed to retrieve Neo4j password for ${containerName}:`, error.message);
            // Return undefined to indicate password retrieval failed
            return undefined;
        }
    }
    
    async saveNeo4jPassword(containerName: string, password: string): Promise<void> {
        try {
            if (!containerName) {
                throw new Error('Container name is required');
            }
            if (!password || typeof password !== 'string') {
                throw new Error('Valid password string is required');
            }
            
            const config = vscode.workspace.getConfiguration(this.configSection);
            let passwords: Record<string, string>;
            
            try {
                passwords = config.get<Record<string, string>>('neo4jPasswords', {});
            } catch (getError: any) {
                console.warn('Failed to get existing passwords, starting with empty object:', getError.message);
                passwords = {};
            }
            
            passwords[containerName] = password;
            
            await config.update('neo4jPasswords', passwords, 
                vscode.ConfigurationTarget.Global);
            
        } catch (error: any) {
            const errorMsg = `Failed to save Neo4j password for ${containerName}: ${error.message}`;
            console.error(errorMsg);
            throw new Error(errorMsg);
        }
    }
    
    async clearNeo4jPassword(containerName: string): Promise<void> {
        try {
            if (!containerName) {
                throw new Error('Container name is required');
            }
            
            const config = vscode.workspace.getConfiguration(this.configSection);
            let passwords: Record<string, string>;
            
            try {
                passwords = config.get<Record<string, string>>('neo4jPasswords', {});
            } catch (getError: any) {
                console.warn('Failed to get existing passwords for clearing:', getError.message);
                // If we can't get existing passwords, there's nothing to clear
                return;
            }
            
            if (!(containerName in passwords)) {
                // Password doesn't exist, nothing to clear
                return;
            }
            
            delete passwords[containerName];
            
            await config.update('neo4jPasswords', passwords, 
                vscode.ConfigurationTarget.Global);
            
        } catch (error: any) {
            const errorMsg = `Failed to clear Neo4j password for ${containerName}: ${error.message}`;
            console.error(errorMsg);
            throw new Error(errorMsg);
        }
    }
}