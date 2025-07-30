import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { ConfigurationManager } from './configurationManager';

export interface BlarifyResult {
    nodes: any[];
    edges: any[];
}

export class BlarifyIntegration {
    private lastAnalysis?: number;
    
    constructor(private configManager: ConfigurationManager) {}
    
    async analyzeWorkspace(
        workspacePath: string,
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        token: vscode.CancellationToken
    ): Promise<BlarifyResult> {
        return new Promise((resolve, reject) => {
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
            
            // Use the local Blarify installation from the current repo
            const extensionPath = path.resolve(__dirname, '..');
            const blarifyPath = path.resolve(extensionPath, '..', 'blarify');
            const blarifyScript = path.join(blarifyPath, '__main__.py');
            
            // Check if local Blarify exists
            if (!fs.existsSync(blarifyScript)) {
                reject(new Error(`Blarify not found at ${blarifyScript}. Make sure the extension is in the same repository as Blarify.`));
                return;
            }
            
            // Spawn Blarify process using Python
            const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
            const blarify = spawn(pythonExecutable, ['-m', 'blarify', ...args], {
                cwd: workspacePath,
                env: { 
                    ...process.env,
                    PYTHONPATH: path.resolve(extensionPath, '..')
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
                } catch (error) {
                    reject(new Error(`Failed to parse Blarify output: ${error}`));
                }
            });
            
            blarify.on('error', (error) => {
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
        });
    }
    
    async checkBlarifyInstalled(): Promise<boolean> {
        // Check if local Blarify exists in the repo
        const extensionPath = path.resolve(__dirname, '..');
        const blarifyPath = path.resolve(extensionPath, '..', 'blarify', '__main__.py');
        
        if (fs.existsSync(blarifyPath)) {
            // Also check if Python is available
            return new Promise((resolve) => {
                const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
                const check = spawn(pythonExecutable, ['--version']);
                check.on('close', (code) => {
                    resolve(code === 0);
                });
                check.on('error', () => {
                    resolve(false);
                });
            });
        }
        
        // Fallback to checking if blarify is installed globally
        return new Promise((resolve) => {
            const check = spawn('blarify', ['--version']);
            check.on('close', (code) => {
                resolve(code === 0);
            });
            check.on('error', () => {
                resolve(false);
            });
        });
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