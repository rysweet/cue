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
            
            // Try to find Blarify in different locations
            const possiblePaths = [
                // Development: extension in repo
                path.resolve(__dirname, '..', '..', 'blarify', '__main__.py'),
                // Installed: look for blarify in the workspace
                path.resolve(workspacePath, 'blarify', '__main__.py'),
                // Installed: look for blarify in parent of workspace
                path.resolve(workspacePath, '..', 'blarify', '__main__.py'),
            ];
            
            let blarifyScript: string | null = null;
            let pythonPath: string | null = null;
            
            for (const testPath of possiblePaths) {
                if (fs.existsSync(testPath)) {
                    blarifyScript = testPath;
                    pythonPath = path.dirname(path.dirname(testPath));
                    break;
                }
            }
            
            if (!blarifyScript) {
                // Try using global blarify command
                this.checkBlarifyInstalled().then(hasBlarifyCommand => {
                    if (!hasBlarifyCommand) {
                        reject(new Error('Blarify not found. Please ensure Blarify is installed or available in your workspace.'));
                        return;
                    }
                    // Continue with global blarify
                    this.runBlarifyProcess(null, null, args, workspacePath, progress, token, resolve, reject);
                }).catch(err => {
                    reject(new Error('Failed to check Blarify installation: ' + err));
                });
                return;
            }
            
            // Run with local blarify
            this.runBlarifyProcess(blarifyScript, pythonPath, args, workspacePath, progress, token, resolve, reject);
        });
    }
    
    private runBlarifyProcess(
        blarifyScript: string | null,
        pythonPath: string | null,
        args: string[],
        workspacePath: string,
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        token: vscode.CancellationToken,
        resolve: (value: any) => void,
        reject: (reason?: any) => void
    ): void {
        // Spawn Blarify process
        let blarify: any;
        if (blarifyScript) {
            // Use local blarify with PYTHONPATH
            const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
            blarify = spawn(pythonExecutable, ['-m', 'blarify', ...args], {
                cwd: workspacePath,
                env: { 
                    ...process.env,
                    PYTHONPATH: pythonPath!
                }
            });
        } else {
            // Use global blarify command
            blarify = spawn('blarify', args, {
                cwd: workspacePath,
                env: process.env
            });
        }
        
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
        // First check if Python is available
        const pythonAvailable = await new Promise<boolean>((resolve) => {
            const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
            const check = spawn(pythonExecutable, ['--version']);
            check.on('close', (code) => {
                resolve(code === 0);
            });
            check.on('error', () => {
                resolve(false);
            });
        });
        
        if (!pythonAvailable) {
            return false;
        }
        
        // Check if blarify is installed globally
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