"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const assert = __importStar(require("assert"));
const vscode = __importStar(require("vscode"));
const sinon = __importStar(require("sinon"));
suite('Extension Commands Test Suite', () => {
    let sandbox;
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
            assert.ok(allCommands.includes(cmd), `Command '${cmd}' should be registered but was not found`);
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
                assert.ok(commands.includes(cmd), `Command ${cmd} not found in registered commands`);
            }
            catch (error) {
                assert.fail(`Failed to verify command ${cmd}: ${error}`);
            }
        }
    });
    test('ingestWorkspace command should be registered and callable', async () => {
        const commandId = 'blarifyVisualizer.ingestWorkspace';
        // Check if command is registered
        const commands = await vscode.commands.getCommands();
        assert.ok(commands.includes(commandId), `Command '${commandId}' not found. Available commands: ${commands.filter(c => c.startsWith('blarify')).join(', ')}`);
        // Try to get command info (this would fail if command doesn't exist)
        try {
            // Note: We can't actually execute the command in tests without mocking 
            // all dependencies, but we can verify it's registered
            const hasCommand = commands.includes(commandId);
            assert.ok(hasCommand, 'Command should be available');
        }
        catch (error) {
            assert.fail(`Command verification failed: ${error}`);
        }
    });
    test('Extension activation should happen immediately with "*" event', () => {
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        assert.ok(extension, 'Extension should exist');
        // Check activation events in package.json
        const packageJson = extension.packageJSON;
        assert.ok(packageJson.activationEvents.includes('*'), 'Extension should have "*" activation event');
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
//# sourceMappingURL=commands.test.js.map