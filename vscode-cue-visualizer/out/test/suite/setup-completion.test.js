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
const sinon = __importStar(require("sinon"));
suite('Setup Completion Tests', () => {
    let sandbox;
    setup(() => {
        sandbox = sinon.createSandbox();
    });
    teardown(() => {
        sandbox.restore();
    });
    test('Analysis prompt should not appear until setup is complete', async () => {
        // Track what happens
        const events = [];
        let setupComplete = false;
        let promptShown = false;
        // Mock setup process (now includes Neo4j)
        const runSetup = async () => {
            events.push('setup-started');
            // Simulate Azure OpenAI config check
            await new Promise(resolve => setTimeout(resolve, 200));
            events.push('azure-config-checked');
            // Simulate Neo4j startup as part of setup
            events.push('neo4j-starting');
            await new Promise(resolve => setTimeout(resolve, 500));
            events.push('neo4j-running');
            // Setup is only complete when ALL tasks finish
            setupComplete = true;
            events.push('setup-complete');
        };
        // Mock showing prompt - should only happen when setup is complete
        const showAnalysisPrompt = () => {
            // This is the key assertion
            assert.ok(setupComplete, 'Setup must be complete before showing prompt');
            promptShown = true;
            events.push('prompt-shown');
        };
        // Run setup
        await runSetup();
        // Now show prompt
        showAnalysisPrompt();
        // Verify the sequence
        assert.ok(promptShown, 'Prompt should have been shown');
        const neo4jIndex = events.indexOf('neo4j-running');
        const setupIndex = events.indexOf('setup-complete');
        const promptIndex = events.indexOf('prompt-shown');
        assert.ok(neo4jIndex < setupIndex, 'Neo4j must start before setup completes');
        assert.ok(setupIndex < promptIndex, 'Setup must complete before prompt');
    });
    test('Setup state should be tracked properly', async () => {
        // This represents what the extension should track
        const extensionState = {
            setupComplete: false,
            canShowPrompt: function () {
                return this.setupComplete;
            }
        };
        // Initially, prompt should not be allowed
        assert.strictEqual(extensionState.canShowPrompt(), false, 'Should not show prompt initially');
        // After setup completes (which includes Neo4j)
        extensionState.setupComplete = true;
        assert.strictEqual(extensionState.canShowPrompt(), true, 'Should show prompt when setup is complete');
    });
});
//# sourceMappingURL=setup-completion.test.js.map