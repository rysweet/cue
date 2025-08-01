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
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const child_process_1 = require("child_process");
const pythonEnvironment_1 = require("./pythonEnvironment");
class BlarifyIntegration {
    constructor(configManager, extensionPath) {
        this.configManager = configManager;
        this.extensionPath = extensionPath;
        this.pythonEnv = new pythonEnvironment_1.PythonEnvironment(extensionPath);
    }
    async analyzeWorkspace(workspacePath, progress, token) {
        return new Promise(async (resolve, reject) => {
            console.log(`BlarifyIntegration: Analyzing workspace at: ${workspacePath}`);
            console.log(`Extension path: ${this.extensionPath}`);
            // Ensure Python environment is set up
            let pythonPath;
            try {
                pythonPath = await this.pythonEnv.ensureSetup();
                console.log(`Using Python from: ${pythonPath}`);
            }
            catch (error) {
                reject(new Error(`Failed to set up Python environment: ${error}`));
                return;
            }
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
            // Use bundled Blarify
            const bundledBlarifyPath = path.join(this.extensionPath, 'bundled', 'blarify');
            console.log(`Using bundled Blarify from: ${bundledBlarifyPath}`);
            // Run with bundled Python environment
            this.runBlarifyProcess(pythonPath, bundledBlarifyPath, args, workspacePath, progress, token, resolve, reject);
        });
    }
    runBlarifyProcess(pythonPath, blarifyPath, args, workspacePath, progress, token, resolve, reject) {
        // Spawn Blarify process using bundled Python
        // We need to run blarify's main.py directly since it's not installed as a package
        const blarifyMainPath = path.join(this.extensionPath, 'bundled', 'blarify', 'main.py');
        const blarify = (0, child_process_1.spawn)(pythonPath, [blarifyMainPath, ...args], {
            cwd: workspacePath,
            env: {
                ...process.env,
                PYTHONPATH: path.join(this.extensionPath, 'bundled')
            }
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
                reject(new Error('Python not found. Please ensure Python 3 is installed and in your PATH'));
            }
            else {
                reject(error);
            }
        });
        // Handle cancellation
        token.onCancellationRequested(() => {
            blarify.kill();
        });
    }
    async checkBlarifyInstalled() {
        // With bundled Blarify, we just need to check if the bundled directory exists
        const bundledBlarifyPath = path.join(this.extensionPath, 'bundled', 'blarify', 'main.py');
        return fs.existsSync(bundledBlarifyPath);
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