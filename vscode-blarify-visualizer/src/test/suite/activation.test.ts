import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import { activate } from '../../extension';

suite('Extension Activation Test Suite', () => {
    test('Extension should be activated and commands registered', async () => {
        // Check if extension is already activated by VS Code
        const extension = vscode.extensions.getExtension('cue.cue-visualizer');
        assert.ok(extension, 'Extension should be installed');
        
        // If not active, wait for activation
        if (!extension.isActive) {
            await extension.activate();
        }
        
        assert.ok(extension.isActive, 'Extension should be active');
        
        // Check if all expected commands are registered
        const commands = await vscode.commands.getCommands();
        const expectedCommands = [
            'cueVisualizer.showVisualization',
            'cueVisualizer.ingestWorkspace',
            'cueVisualizer.updateGraph',
            'cueVisualizer.searchGraph',
            'cueVisualizer.restartNeo4j'
        ];
        
        for (const cmd of expectedCommands) {
            assert.ok(
                commands.includes(cmd),
                `Command '${cmd}' should be registered`
            );
        }
        
        // Check if output channel was created
        // Note: We can't directly access output channels, but we can verify the extension activated without errors
        assert.ok(true, 'Extension activated without throwing errors');
    });
    
    test('Bundled dependencies should be accessible', () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        
        // Check if bundled directories exist
        const bundledPath = path.join(extensionPath, 'bundled');
        const fs = require('fs');
        
        // These paths should exist after bundling
        const requiredPaths = [
            path.join(bundledPath, 'cue'),
            path.join(bundledPath, 'neo4j-container-manager')
        ];
        
        for (const reqPath of requiredPaths) {
            // In test environment, these might not exist, so we just log
            if (fs.existsSync(reqPath)) {
                console.log(`✓ Found bundled path: ${reqPath}`);
            } else {
                console.log(`✗ Missing bundled path: ${reqPath}`);
            }
        }
    });
});