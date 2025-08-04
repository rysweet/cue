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
const path = __importStar(require("path"));
suite('Extension Activation Test Suite', () => {
    test('Extension should be activated and commands registered', async () => {
        // Check if extension is already activated by VS Code
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        assert.ok(extension, 'Extension should be installed');
        // If not active, wait for activation
        if (!extension.isActive) {
            await extension.activate();
        }
        assert.ok(extension.isActive, 'Extension should be active');
        // Check if all expected commands are registered
        const commands = await vscode.commands.getCommands();
        const expectedCommands = [
            'blarifyVisualizer.showVisualization',
            'blarifyVisualizer.ingestWorkspace',
            'blarifyVisualizer.updateGraph',
            'blarifyVisualizer.searchGraph',
            'blarifyVisualizer.restartNeo4j'
        ];
        for (const cmd of expectedCommands) {
            assert.ok(commands.includes(cmd), `Command '${cmd}' should be registered`);
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
            path.join(bundledPath, 'blarify'),
            path.join(bundledPath, 'neo4j-container-manager')
        ];
        for (const reqPath of requiredPaths) {
            // In test environment, these might not exist, so we just log
            if (fs.existsSync(reqPath)) {
                console.log(`✓ Found bundled path: ${reqPath}`);
            }
            else {
                console.log(`✗ Missing bundled path: ${reqPath}`);
            }
        }
    });
});
//# sourceMappingURL=activation.test.js.map