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
    getNeo4jConfig() {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return {
            uri: config.get('neo4j.uri', 'bolt://localhost:7687'),
            username: config.get('neo4j.username', 'neo4j'),
            password: config.get('neo4j.password', '')
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
        const azureConfig = this.getAzureOpenAIConfig();
        return !!(azureConfig.apiKey && azureConfig.endpoint);
    }
    async promptForConfiguration() {
        const configure = await vscode.window.showInformationMessage('Blarify Visualizer requires Azure OpenAI configuration for full functionality.', 'Configure', 'Later');
        if (configure === 'Configure') {
            await vscode.commands.executeCommand('workbench.action.openSettings', '@ext:blarify.blarify-visualizer');
            return true;
        }
        return false;
    }
}
exports.ConfigurationManager = ConfigurationManager;
//# sourceMappingURL=configurationManager.js.map