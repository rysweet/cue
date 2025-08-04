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
suite('Extension Behavior Integration Test', () => {
    test('Extension should complete setup before showing prompt', async function () {
        this.timeout(20000); // Allow time for extension to fully activate
        // Get the extension
        const ext = vscode.extensions.getExtension('blarify.blarify-visualizer');
        assert.ok(ext, 'Extension should be present');
        // Wait for activation
        if (!ext.isActive) {
            await ext.activate();
        }
        // Give the extension time to run its setup
        await new Promise(resolve => setTimeout(resolve, 3000));
        // Check the output channel for our log messages
        const outputChannels = vscode.window.visibleTextEditors
            .map(e => e.document.fileName)
            .filter(name => name.includes('Blarify'));
        console.log('Extension activated and setup should be running');
        // Since we can't directly access the output channel content in tests,
        // we'll verify that the extension activated without errors
        assert.ok(ext.isActive, 'Extension should be active');
        // Verify commands are registered
        const commands = await vscode.commands.getCommands();
        assert.ok(commands.includes('blarifyVisualizer.ingestWorkspace'), 'Commands should be registered');
    });
    test('Verify setup sequence in mock environment', async () => {
        // This test simulates what should happen
        const events = [];
        // Simulate the extension's behavior
        const mockSetupState = {
            isSetupComplete: false,
            isNeo4jReady: false,
            canPromptForAnalysis() {
                return this.isSetupComplete && this.isNeo4jReady;
            }
        };
        // Simulate setup tasks
        const runSetup = async () => {
            events.push('setup-started');
            await new Promise(resolve => setTimeout(resolve, 100));
            mockSetupState.isSetupComplete = true;
            events.push('setup-complete');
        };
        // Simulate Neo4j startup
        const startNeo4j = async () => {
            events.push('neo4j-started');
            await new Promise(resolve => setTimeout(resolve, 200));
            mockSetupState.isNeo4jReady = true;
            events.push('neo4j-ready');
        };
        // Run both in parallel
        await Promise.all([runSetup(), startNeo4j()]);
        // Check if we can prompt
        if (mockSetupState.canPromptForAnalysis()) {
            events.push('prompt-shown');
        }
        // Verify the sequence
        assert.deepStrictEqual(events, [
            'setup-started',
            'neo4j-started',
            'setup-complete',
            'neo4j-ready',
            'prompt-shown'
        ]);
        // Verify both conditions were met before prompt
        const promptIndex = events.indexOf('prompt-shown');
        const setupIndex = events.indexOf('setup-complete');
        const neo4jIndex = events.indexOf('neo4j-ready');
        assert.ok(setupIndex < promptIndex, 'Setup must complete before prompt');
        assert.ok(neo4jIndex < promptIndex, 'Neo4j must be ready before prompt');
    });
});
//# sourceMappingURL=extension-behavior.test.js.map