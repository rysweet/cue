import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

export class PythonEnvironment {
    private pythonPath?: string;
    private isSetup = false;
    
    constructor(private extensionPath: string) {}
    
    async ensureSetup(retryCount: number = 0): Promise<string> {
        if (this.isSetup && this.pythonPath) {
            return this.pythonPath;
        }
        
        const bundledDir = path.join(this.extensionPath, 'bundled');
        const venvDir = path.join(bundledDir, 'venv');
        
        // Check if virtual environment exists
        const pythonExe = process.platform === 'win32' 
            ? path.join(venvDir, 'Scripts', 'python.exe')
            : path.join(venvDir, 'bin', 'python');
            
        if (fs.existsSync(pythonExe)) {
            this.pythonPath = pythonExe;
            this.isSetup = true;
            return pythonExe;
        }
        
        // Run setup with retry logic
        const maxRetries = 2;
        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: retryCount > 0 ? `Setting up Blarify (Retry ${retryCount})` : "Setting up Blarify",
                cancellable: false
            }, async (progress) => {
                progress.report({ message: "Installing Python dependencies..." });
                
                const setupScript = path.join(bundledDir, 'setup.py');
                const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
                
                return new Promise<void>((resolve, reject) => {
                const setup = spawn(pythonCommand, [setupScript], {
                    cwd: bundledDir,
                    env: process.env
                });
                
                let output = '';
                let errorOutput = '';
                
                setup.stdout.on('data', (data) => {
                    output += data.toString();
                    const lines = data.toString().split('\n');
                    for (const line of lines) {
                        if (line.trim()) {
                            progress.report({ message: line.trim() });
                        }
                    }
                });
                
                setup.stderr.on('data', (data) => {
                    errorOutput += data.toString();
                });
                
                setup.on('close', (code) => {
                    if (code === 0) {
                        this.pythonPath = pythonExe;
                        this.isSetup = true;
                        resolve();
                    } else {
                        const errorMessage = errorOutput || output || 'Unknown error during setup';
                        let userFriendlyMessage = `Python setup failed (exit code ${code}): ${errorMessage}`;
                        
                        // Provide more specific error messages for common issues
                        if (errorMessage.includes('README.md')) {
                            userFriendlyMessage = `Setup failed due to missing README.md file. This is likely a bundling issue. Full error: ${errorMessage}`;
                        } else if (errorMessage.includes('pip install')) {
                            userFriendlyMessage = `Failed to install Python dependencies. Please ensure you have internet connectivity and Python is properly installed. Full error: ${errorMessage}`;
                        } else if (errorMessage.includes('permission')) {
                            userFriendlyMessage = `Permission denied during setup. Try running VS Code as administrator or check file permissions. Full error: ${errorMessage}`;
                        }
                        
                        reject(new Error(userFriendlyMessage));
                    }
                });
                
                setup.on('error', (error) => {
                    reject(new Error(`Failed to run setup: ${error.message}`));
                });
                });
            });
        } catch (error) {
            // Retry logic for transient failures
            if (retryCount < maxRetries) {
                console.log(`Setup attempt ${retryCount + 1} failed, retrying... Error: ${error}`);
                await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds before retry
                return this.ensureSetup(retryCount + 1);
            } else {
                throw error; // Re-throw after max retries
            }
        }
        
        if (!this.pythonPath) {
            throw new Error('Python setup completed but executable not found');
        }
        
        return this.pythonPath;
    }
    
    getPythonPath(): string | undefined {
        return this.pythonPath;
    }
}