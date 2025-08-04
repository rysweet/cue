import * as vscode from 'vscode';

export class StatusBarManager implements vscode.Disposable {
    private statusBarItem: vscode.StatusBarItem;
    
    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'cueVisualizer.showVisualization';
        this.statusBarItem.show();
    }
    
    setStatus(text: string, icon?: string): void {
        const iconPrefix = icon ? `$(${icon}) ` : '';
        this.statusBarItem.text = `${iconPrefix}Blarify: ${text}`;
        this.statusBarItem.tooltip = `Blarify Visualizer\n${text}\nClick to open visualization`;
    }
    
    setBusy(text: string = 'Working...'): void {
        this.setStatus(text, 'sync~spin');
    }
    
    setReady(text: string = 'Ready'): void {
        this.setStatus(text, 'check');
    }
    
    setError(text: string): void {
        this.setStatus(text, 'error');
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        
        // Clear error background after 5 seconds
        setTimeout(() => {
            this.statusBarItem.backgroundColor = undefined;
        }, 5000);
    }
    
    setWarning(text: string): void {
        this.setStatus(text, 'warning');
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        
        // Clear warning background after 5 seconds
        setTimeout(() => {
            this.statusBarItem.backgroundColor = undefined;
        }, 5000);
    }
    
    dispose(): void {
        this.statusBarItem.dispose();
    }
}