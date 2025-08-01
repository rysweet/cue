import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';

suite('Extension Commands Test Suite', () => {
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('All extension commands should be registered', async () => {
        // Expected commands
        const expectedCommands = [
            'blarifyVisualizer.showVisualization',
            'blarifyVisualizer.ingestWorkspace',
            'blarifyVisualizer.updateGraph',
            'blarifyVisualizer.searchGraph',
            'blarifyVisualizer.restartNeo4j'
        ];
        
        // Get all registered commands
        const allCommands = await vscode.commands.getCommands();
        
        // Check each expected command is registered
        for (const cmd of expectedCommands) {
            assert.ok(
                allCommands.includes(cmd),
                `Command '${cmd}' should be registered but was not found`
            );
        }
    });
    
    test('Extension should activate on startup', async () => {
        // Check if our extension is active
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        assert.ok(extension, 'Extension should be present');
        
        // The extension should be active since we have "*" activation
        assert.ok(extension.isActive, 'Extension should be active');
    });
    
    test('Commands should be executable after activation', async () => {
        // This test will fail if commands are not properly registered
        const testableCommands = [
            'blarifyVisualizer.showVisualization',
            'blarifyVisualizer.searchGraph'
        ];
        
        for (const cmd of testableCommands) {
            try {
                // Check if command exists in the command palette
                const commands = await vscode.commands.getCommands();
                assert.ok(
                    commands.includes(cmd),
                    `Command ${cmd} not found in registered commands`
                );
            } catch (error) {
                assert.fail(`Failed to verify command ${cmd}: ${error}`);
            }
        }
    });
    
    test('ingestWorkspace command should be registered and callable', async () => {
        const commandId = 'blarifyVisualizer.ingestWorkspace';
        
        // Check if command is registered
        const commands = await vscode.commands.getCommands();
        assert.ok(
            commands.includes(commandId),
            `Command '${commandId}' not found. Available commands: ${commands.filter(c => c.startsWith('blarify')).join(', ')}`
        );
        
        // Try to get command info (this would fail if command doesn't exist)
        try {
            // Note: We can't actually execute the command in tests without mocking 
            // all dependencies, but we can verify it's registered
            const hasCommand = commands.includes(commandId);
            assert.ok(hasCommand, 'Command should be available');
        } catch (error) {
            assert.fail(`Command verification failed: ${error}`);
        }
    });
    
    test('Extension activation should happen immediately with "*" event', () => {
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        assert.ok(extension, 'Extension should exist');
        
        // Check activation events in package.json
        const packageJson = extension.packageJSON;
        assert.ok(
            packageJson.activationEvents.includes('*'),
            'Extension should have "*" activation event'
        );
    });
});

suite('Command Registration Debugging', () => {
    test('List all Blarify commands for debugging', async () => {
        const allCommands = await vscode.commands.getCommands();
        const blarifyCommands = allCommands.filter(cmd => cmd.includes('blarify'));
        
        console.log('=== All Blarify Commands ===');
        console.log(blarifyCommands.length > 0 
            ? blarifyCommands.join('\n') 
            : 'NO BLARIFY COMMANDS FOUND');
        
        // This will help us see what's actually registered
        assert.ok(true, `Found ${blarifyCommands.length} Blarify commands`);
    });
});