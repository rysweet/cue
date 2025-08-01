import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

export class PythonEnvironment {
    private pythonPath?: string;
    private isSetup = false;
    
    constructor(private extensionPath: string) {}
    
    async ensureSetup(): Promise<string> {
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
        
        // Run setup
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Setting up Blarify",
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
                        reject(new Error(`Setup failed: ${errorOutput || output}`));
                    }
                });
                
                setup.on('error', (error) => {
                    reject(new Error(`Failed to run setup: ${error.message}`));
                });
            });
        });
        
        if (!this.pythonPath) {
            throw new Error('Python setup completed but executable not found');
        }
        
        return this.pythonPath;
    }
    
    getPythonPath(): string | undefined {
        return this.pythonPath;
    }
}