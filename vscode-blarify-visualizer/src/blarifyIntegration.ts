import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { ConfigurationManager } from './configurationManager';
import { PythonEnvironment } from './pythonEnvironment';

export interface BlarifyResult {
    nodes: any[];
    edges: any[];
}

export class BlarifyIntegration {
    private lastAnalysis?: number;
    private pythonEnv: PythonEnvironment;
    
    constructor(
        private configManager: ConfigurationManager,
        private extensionPath: string
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
            
            // Prepare Blarify command
            const excludePatterns = this.configManager.getExcludePatterns();
            const args = ['ingest', workspacePath, '--json'];
            
            // Add Azure OpenAI config if available
            const azureConfig = this.configManager.getAzureOpenAIConfig();
            if (azureConfig.apiKey) {
                args.push(
                    '--enable-llm-descriptions',
                    '--azure-api-key', azureConfig.apiKey,
                    '--azure-endpoint', azureConfig.endpoint,
                    '--azure-deployment', azureConfig.deploymentName
                );
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
    
    private runBlarifyProcess(
        pythonPath: string,
        blarifyPath: string,
        args: string[],
        workspacePath: string,
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        token: vscode.CancellationToken,
        resolve: (value: any) => void,
        reject: (reason?: any) => void
    ): void {
        // Spawn Blarify process using bundled Python
        // We need to run blarify's main.py directly since it's not installed as a package
        const blarifyMainPath = path.join(this.extensionPath, 'bundled', 'blarify', 'main.py');
        const blarify = spawn(pythonPath, [blarifyMainPath, ...args], {
            cwd: workspacePath,
            env: { 
                ...process.env,
                PYTHONPATH: path.join(this.extensionPath, 'bundled')
            }
        });
        
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