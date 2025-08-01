import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { ConfigurationManager } from './configurationManager';
import { PythonEnvironment } from './pythonEnvironment';
import { Neo4jManager } from './neo4jManager';

export interface BlarifyResult {
    nodes: any[];
    edges: any[];
}

export class BlarifyIntegration {
    private static readonly DEFAULT_CONTAINER_NAME = 'blarify-visualizer-development';
    private lastAnalysis?: number;
    private pythonEnv: PythonEnvironment;
    
    constructor(
        private configManager: ConfigurationManager,
        private extensionPath: string,
        private neo4jManager?: Neo4jManager
    ) {
        this.pythonEnv = new PythonEnvironment(extensionPath);
    }
    
    async analyzeWorkspace(
        workspacePath: string,
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        token: vscode.CancellationToken
    ): Promise<BlarifyResult> {
        return new Promise(async (resolve, reject) => {
            console.log(`BlarifyIntegration: Analyzing workspace at: ${workspacePath}`);
            console.log(`Extension path: ${this.extensionPath}`);
            
            // Ensure Python environment is set up
            let pythonPath: string;
            try {
                pythonPath = await this.pythonEnv.ensureSetup();
                console.log(`Using Python from: ${pythonPath}`);
            } catch (error) {
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
    private async getNeo4jConnectionDetails(): Promise<{uri: string, user: string, password: string}> {
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
            const containerName = BlarifyIntegration.DEFAULT_CONTAINER_NAME;
            const savedPassword = this.configManager.getNeo4jPassword(containerName);
            
            return {
                uri: 'bolt://localhost:7957', // Standard Neo4j bolt port
                user: 'neo4j',
                password: savedPassword || 'test-password'
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            console.warn(`Failed to get Neo4j connection details: ${errorMessage}. Using default connection settings (bolt://localhost:7957).`);
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
    private async buildEnvironmentVariables(
        workspacePath: string,
        azureConfig: any,
        excludePatterns: string[]
    ): Promise<NodeJS.ProcessEnv> {
        // Get Neo4j connection details
        const neo4jConfig = await this.getNeo4jConnectionDetails();
        
        const baseEnv: NodeJS.ProcessEnv = {
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
        } else {
            baseEnv.ENABLE_LLM_DESCRIPTIONS = 'false';
        }
        
        // Add exclude patterns if any
        if (excludePatterns.length > 0) {
            baseEnv.NAMES_TO_SKIP = excludePatterns.join(',');
        }
        
        return baseEnv;
    }
    
    private async runBlarifyProcess(
        pythonPath: string,
        blarifyPath: string,
        workspacePath: string,
        azureConfig: any,
        excludePatterns: string[],
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        token: vscode.CancellationToken,
        resolve: (value: any) => void,
        reject: (reason?: any) => void
    ): Promise<void> {
        try {
            // Build environment variables for Blarify execution
            const env = await this.buildEnvironmentVariables(workspacePath, azureConfig, excludePatterns);
            
            // Spawn Blarify process using bundled Python with environment variables
            // We need to run blarify's main.py directly since it's not installed as a package
            const blarifyMainPath = path.join(this.extensionPath, 'bundled', 'blarify', 'main.py');
            const blarify = spawn(pythonPath, [blarifyMainPath], {
                cwd: workspacePath,
                env: env
            });
            
            this.handleBlarifyProcess(blarify, progress, token, resolve, reject);
        } catch (error) {
            reject(new Error(`Failed to build environment variables: ${error}`));
        }
    }
    
    private handleBlarifyProcess(
        blarify: any,
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        token: vscode.CancellationToken,
        resolve: (value: any) => void,
        reject: (reason?: any) => void
    ): void {
        
        let output = '';
        let errorOutput = '';
        
        blarify.stdout.on('data', (data: Buffer) => {
            output += data.toString();
            
            // Try to parse progress messages
            const lines = data.toString().split('\n');
            for (const line of lines) {
                if (line.includes('Processing')) {
                    progress.report({ message: line.trim() });
                }
            }
        });
        
        blarify.stderr.on('data', (data: Buffer) => {
            errorOutput += data.toString();
        });
        
        blarify.on('close', (code: number | null) => {
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
            } catch (error) {
                reject(new Error(`Failed to parse Blarify output: ${error}`));
            }
        });
        
        blarify.on('error', (error: Error) => {
            if (error.message.includes('ENOENT')) {
                reject(new Error('Python not found. Please ensure Python 3 is installed and in your PATH'));
            } else {
                reject(error);
            }
        });
        
        // Handle cancellation
        token.onCancellationRequested(() => {
            blarify.kill();
        });
    }
    
    async checkBlarifyInstalled(): Promise<boolean> {
        // With bundled Blarify, we just need to check if the bundled directory exists
        const bundledBlarifyPath = path.join(this.extensionPath, 'bundled', 'blarify', 'main.py');
        return fs.existsSync(bundledBlarifyPath);
    }
    
    getLastAnalysis(): number | undefined {
        return this.lastAnalysis;
    }
    
    async installBlarify(): Promise<void> {
        const terminal = vscode.window.createTerminal('Blarify Installation');
        terminal.show();
        terminal.sendText('pip install blarify');
        
        // Wait for user to complete installation
        await vscode.window.showInformationMessage(
            'Installing Blarify. Click OK when installation is complete.',
            'OK'
        );
    }
}