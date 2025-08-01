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
exports.ConfigurationManager = void 0;
const vscode = __importStar(require("vscode"));
class ConfigurationManager {
    constructor() {
        this.configSection = 'blarifyVisualizer';
    }
    getAzureOpenAIConfig() {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return {
            apiKey: config.get('azureOpenAI.apiKey', ''),
            endpoint: config.get('azureOpenAI.endpoint', ''),
            deploymentName: config.get('azureOpenAI.deploymentName', 'gpt-4')
        };
    }
    getVisualizationConfig() {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return {
            nodeLimit: config.get('visualization.nodeLimit', 500),
            defaultLayout: config.get('visualization.defaultLayout', 'force-directed')
        };
    }
    getAutoUpdate() {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get('ingestion.autoUpdate', true);
    }
    getExcludePatterns() {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get('ingestion.excludePatterns', []);
    }
    isConfigured() {
        try {
            const azureConfig = this.getAzureOpenAIConfig();
            return !!(azureConfig.apiKey && azureConfig.endpoint);
        }
        catch (error) {
            console.error('Failed to check configuration status:', error.message);
            return false;
        }
    }
    async promptForConfiguration() {
        const configure = await vscode.window.showInformationMessage('Blarify Visualizer requires Azure OpenAI configuration for full functionality.', 'Configure', 'Later');
        if (configure === 'Configure') {
            await vscode.commands.executeCommand('workbench.action.openSettings', '@ext:blarify.blarify-visualizer');
            return true;
        }
        return false;
    }
    // Neo4j password management with enhanced error handling
    getNeo4jPassword(containerName) {
        try {
            if (!containerName) {
                throw new Error('Container name is required');
            }
            const config = vscode.workspace.getConfiguration(this.configSection);
            const passwords = config.get('neo4jPasswords', {});
            // Validate that the password is a string if it exists
            const password = passwords[containerName];
            if (password !== undefined && typeof password !== 'string') {
                throw new Error(`Invalid password format for container ${containerName}`);
            }
            return password;
        }
        catch (error) {
            console.error(`Failed to retrieve Neo4j password for ${containerName}:`, error.message);
            // Return undefined to indicate password retrieval failed
            return undefined;
        }
    }
    async saveNeo4jPassword(containerName, password) {
        try {
            if (!containerName) {
                throw new Error('Container name is required');
            }
            if (!password || typeof password !== 'string') {
                throw new Error('Valid password string is required');
            }
            const config = vscode.workspace.getConfiguration(this.configSection);
            let passwords;
            try {
                passwords = config.get('neo4jPasswords', {});
            }
            catch (getError) {
                console.warn('Failed to get existing passwords, starting with empty object:', getError.message);
                passwords = {};
            }
            passwords[containerName] = password;
            await config.update('neo4jPasswords', passwords, vscode.ConfigurationTarget.Global);
        }
        catch (error) {
            const errorMsg = `Failed to save Neo4j password for ${containerName}: ${error.message}`;
            console.error(errorMsg);
            throw new Error(errorMsg);
        }
    }
    async clearNeo4jPassword(containerName) {
        try {
            if (!containerName) {
                throw new Error('Container name is required');
            }
            const config = vscode.workspace.getConfiguration(this.configSection);
            let passwords;
            try {
                passwords = config.get('neo4jPasswords', {});
            }
            catch (getError) {
                console.warn('Failed to get existing passwords for clearing:', getError.message);
                // If we can't get existing passwords, there's nothing to clear
                return;
            }
            if (!(containerName in passwords)) {
                // Password doesn't exist, nothing to clear
                return;
            }
            delete passwords[containerName];
            await config.update('neo4jPasswords', passwords, vscode.ConfigurationTarget.Global);
        }
        catch (error) {
            const errorMsg = `Failed to clear Neo4j password for ${containerName}: ${error.message}`;
            console.error(errorMsg);
            throw new Error(errorMsg);
        }
    }
}
exports.ConfigurationManager = ConfigurationManager;
//# sourceMappingURL=configurationManager.js.map