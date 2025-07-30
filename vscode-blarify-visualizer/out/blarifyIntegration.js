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
exports.BlarifyIntegration = void 0;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
class BlarifyIntegration {
    constructor(configManager) {
        this.configManager = configManager;
    }
    async analyzeWorkspace(workspacePath, progress, token) {
        return new Promise((resolve, reject) => {
            // Prepare Blarify command
            const excludePatterns = this.configManager.getExcludePatterns();
            const args = ['ingest', workspacePath, '--json'];
            // Add Azure OpenAI config if available
            const azureConfig = this.configManager.getAzureOpenAIConfig();
            if (azureConfig.apiKey) {
                args.push('--enable-llm-descriptions', '--azure-api-key', azureConfig.apiKey, '--azure-endpoint', azureConfig.endpoint, '--azure-deployment', azureConfig.deploymentName);
            }
            // Add exclude patterns
            if (excludePatterns.length > 0) {
                args.push('--names-to-skip', ...excludePatterns);
            }
            // Always enable documentation nodes
            args.push('--enable-documentation-nodes');
            // Spawn Blarify process
            const blarify = (0, child_process_1.spawn)('blarify', args, {
                cwd: workspacePath,
                env: { ...process.env }
            });
            let output = '';
            let errorOutput = '';
            blarify.stdout.on('data', (data) => {
                output += data.toString();
                // Try to parse progress messages
                const lines = data.toString().split('\n');
                for (const line of lines) {
                    if (line.includes('Processing')) {
                        progress.report({ message: line.trim() });
                    }
                }
            });
            blarify.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });
            blarify.on('close', (code) => {
                if (token.isCancellationRequested) {
                    reject(new Error('Analysis cancelled'));
                    return;
                }
                if (code !== 0) {
                    reject(new Error(`Blarify exited with code ${code}: ${errorOutput}`));
                    return;
                }
                try {
                    // Parse JSON output
                    const result = JSON.parse(output);
                    this.lastAnalysis = Date.now();
                    resolve(result);
                }
                catch (error) {
                    reject(new Error(`Failed to parse Blarify output: ${error}`));
                }
            });
            blarify.on('error', (error) => {
                if (error.message.includes('ENOENT')) {
                    reject(new Error('Blarify not found. Please install it: pip install blarify'));
                }
                else {
                    reject(error);
                }
            });
            // Handle cancellation
            token.onCancellationRequested(() => {
                blarify.kill();
            });
        });
    }
    async checkBlarifyInstalled() {
        return new Promise((resolve) => {
            const check = (0, child_process_1.spawn)('blarify', ['--version']);
            check.on('close', (code) => {
                resolve(code === 0);
            });
            check.on('error', () => {
                resolve(false);
            });
        });
    }
    getLastAnalysis() {
        return this.lastAnalysis;
    }
    async installBlarify() {
        const terminal = vscode.window.createTerminal('Blarify Installation');
        terminal.show();
        terminal.sendText('pip install blarify');
        // Wait for user to complete installation
        await vscode.window.showInformationMessage('Installing Blarify. Click OK when installation is complete.', 'OK');
    }
}
exports.BlarifyIntegration = BlarifyIntegration;
//# sourceMappingURL=blarifyIntegration.js.map