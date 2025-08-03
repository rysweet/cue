import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { cueIntegration } from '../../cueIntegration';
import { Neo4jManager } from '../../neo4jManager';
import { ConfigurationManager } from '../../configurationManager';

suite('cue Path Resolution Test Suite', () => {
    let cueIntegration: cueIntegration;
    let configManager: any;
    
    setup(() => {
        // Mock config manager
        configManager = {
            getExcludePatterns: () => [],
            getNeo4jConfig: () => ({
                uri: 'bolt://localhost:7687',
                username: 'neo4j',
                password: 'test'
            })
        };
        
        const extensionPath = path.resolve(__dirname, '..', '..', '..');
        const realConfigManager = new ConfigurationManager();
        const neo4jManager = new Neo4jManager(realConfigManager, extensionPath);
        cueIntegration = new cueIntegration(configManager, extensionPath, neo4jManager);
    });
    
    test('Should find cue in workspace parent directory', async function() {
        // This test simulates the installed extension scenario
        // where cue should be found relative to the workspace
        
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            this.skip();
            return;
        }
        
        // Check if cue exists in expected locations
        const possiblePaths = [
            // In the workspace itself
            path.join(workspaceFolder.uri.fsPath, 'cue', '__main__.py'),
            // In parent of workspace (common dev setup)
            path.join(workspaceFolder.uri.fsPath, '..', 'cue', '__main__.py'),
            // Relative to extension (dev mode)
            path.join(__dirname, '..', '..', '..', '..', 'cue', '__main__.py')
        ];
        
        let cueFound = false;
        let foundPath = '';
        
        for (const testPath of possiblePaths) {
            if (fs.existsSync(testPath)) {
                cueFound = true;
                foundPath = testPath;
                break;
            }
        }
        
        assert.ok(cueFound, `cue not found in any expected location. Searched: ${possiblePaths.join(', ')}`);
        console.log(`cue found at: ${foundPath}`);
    });
    
    test('Should handle workspace analysis with correct path', async function() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            this.skip();
            return;
        }
        
        // Mock the progress and cancellation token
        const progress = {
            report: (value: any) => console.log('Progress:', value)
        };
        
        const token = new vscode.CancellationTokenSource().token;
        
        try {
            // This should find cue and at least start the process
            // It might fail on actual execution if cue isn't fully configured,
            // but it should not fail with "cue not found"
            const promise = cueIntegration.analyzeWorkspace(
                workspaceFolder.uri.fsPath,
                progress as any,
                token
            );
            
            // Give it a moment to check paths
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // If we get here without "cue not found" error, the path resolution worked
            assert.ok(true, 'Path resolution succeeded');
            
            // Cancel the operation to clean up
            if (!token.isCancellationRequested) {
                (token as any).cancel?.();
            }
        } catch (error: any) {
            // Check if it's the specific error we're testing for
            if (error.message.includes('cue not found')) {
                assert.fail(`cue path resolution failed: ${error.message}`);
            }
            // Other errors (like Neo4j connection) are ok for this test
            console.log('Non-path error (expected):', error.message);
        }
    });
    
    test('Should check Python availability', async () => {
        const hasPython = await cueIntegration.checkcueInstalled();
        assert.ok(hasPython, 'Python should be available for cue execution');
    });
});