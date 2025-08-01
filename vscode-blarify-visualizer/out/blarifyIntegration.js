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
    constructor(configManager, extensionPath, neo4jManager) {
        this.configManager = configManager;
        this.extensionPath = extensionPath;
        this.neo4jManager = neo4jManager;
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
            // Prepare configuration for environment variables
            const excludePatterns = this.configManager.getExcludePatterns();
            const azureConfig = this.configManager.getAzureOpenAIConfig();
            // Use bundled Blarify
            const bundledBlarifyPath = path.join(this.extensionPath, 'bundled', 'blarify');
            console.log(`Using bundled Blarify from: ${bundledBlarifyPath}`);
            // Run with bundled Python environment using environment variables
            await this.runBlarifyProcess(pythonPath, bundledBlarifyPath, workspacePath, azureConfig, excludePatterns, progress, token, resolve, reject);
        });
    }
    /**
     * Gets Neo4j connection details from the manager.
     */
    async getNeo4jConnectionDetails() {
        if (!this.neo4jManager) {
            // Fallback to default values used in test files
            return {
                uri: 'bolt://localhost:7957',
                user: 'neo4j',
                password: 'test-password'
            };
        }
        try {
            // Ensure Neo4j is running first
            await this.neo4jManager.ensureRunning();
            // Get the instance details - we need to access the private instance
            // For now, use the default pattern from test files
            const containerName = 'blarify-visualizer-development';
            const savedPassword = this.configManager.getNeo4jPassword(containerName);
            return {
                uri: 'bolt://localhost:7957',
                user: 'neo4j',
                password: savedPassword || 'test-password'
            };
        }
        catch (error) {
            console.warn('Failed to get Neo4j connection details, using defaults:', error);
            return {
                uri: 'bolt://localhost:7957',
                user: 'neo4j',
                password: 'test-password'
            };
        }
    }
    /**
     * Builds environment variables for Blarify execution.
     *
     * Blarify is invoked using environment variables instead of command-line arguments:
     * - ROOT_PATH: The workspace path to analyze
     * - NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD: Database connection
     * - AZURE_*: LLM configuration if enabled
     * - NAMES_TO_SKIP: Comma-separated exclude patterns
     * - ENABLE_*: Feature toggles
     */
    async buildEnvironmentVariables(workspacePath, azureConfig, excludePatterns) {
        // Get Neo4j connection details
        const neo4jConfig = await this.getNeo4jConnectionDetails();
        const baseEnv = {
            ...process.env,
            PYTHONPATH: path.join(this.extensionPath, 'bundled'),
            ROOT_PATH: workspacePath,
            NEO4J_URI: neo4jConfig.uri,
            NEO4J_USER: neo4jConfig.user,
            NEO4J_PASSWORD: neo4jConfig.password,
            ENABLE_DOCUMENTATION_NODES: 'true'
        };
        // Add Azure OpenAI configuration if available
        if (azureConfig.apiKey) {
            baseEnv.ENABLE_LLM_DESCRIPTIONS = 'true';
            baseEnv.AZURE_API_KEY = azureConfig.apiKey;
            baseEnv.AZURE_ENDPOINT = azureConfig.endpoint;
            baseEnv.AZURE_DEPLOYMENT = azureConfig.deploymentName;
        }
        else {
            baseEnv.ENABLE_LLM_DESCRIPTIONS = 'false';
        }
        // Add exclude patterns if any
        if (excludePatterns.length > 0) {
            baseEnv.NAMES_TO_SKIP = excludePatterns.join(',');
        }
        return baseEnv;
    }
    async runBlarifyProcess(pythonPath, blarifyPath, workspacePath, azureConfig, excludePatterns, progress, token, resolve, reject) {
        try {
            // Build environment variables for Blarify execution
            const env = await this.buildEnvironmentVariables(workspacePath, azureConfig, excludePatterns);
            // Spawn Blarify process using bundled Python with environment variables
            // We need to run blarify's main.py directly since it's not installed as a package
            const blarifyMainPath = path.join(this.extensionPath, 'bundled', 'blarify', 'main.py');
            const blarify = (0, child_process_1.spawn)(pythonPath, [blarifyMainPath], {
                cwd: workspacePath,
                env: env
            });
            this.handleBlarifyProcess(blarify, progress, token, resolve, reject);
        }
        catch (error) {
            reject(new Error(`Failed to build environment variables: ${error}`));
        }
    }
    handleBlarifyProcess(blarify, progress, token, resolve, reject) {
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