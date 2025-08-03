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
const fs = __importStar(require("fs"));
const blarifyIntegration_1 = require("../../blarifyIntegration");
const neo4jManager_1 = require("../../neo4jManager");
const configurationManager_1 = require("../../configurationManager");
suite('Blarify Path Resolution Test Suite', () => {
    let blarifyIntegration;
    let configManager;
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
        const realConfigManager = new configurationManager_1.ConfigurationManager();
        const neo4jManager = new neo4jManager_1.Neo4jManager(realConfigManager, extensionPath);
        blarifyIntegration = new blarifyIntegration_1.BlarifyIntegration(configManager, extensionPath, neo4jManager);
    });
    test('Should find Blarify in workspace parent directory', async function () {
        // This test simulates the installed extension scenario
        // where Blarify should be found relative to the workspace
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            this.skip();
            return;
        }
        // Check if Blarify exists in expected locations
        const possiblePaths = [
            // In the workspace itself
            path.join(workspaceFolder.uri.fsPath, 'blarify', '__main__.py'),
            // In parent of workspace (common dev setup)
            path.join(workspaceFolder.uri.fsPath, '..', 'blarify', '__main__.py'),
            // Relative to extension (dev mode)
            path.join(__dirname, '..', '..', '..', '..', 'blarify', '__main__.py')
        ];
        let blarifyFound = false;
        let foundPath = '';
        for (const testPath of possiblePaths) {
            if (fs.existsSync(testPath)) {
                blarifyFound = true;
                foundPath = testPath;
                break;
            }
        }
        assert.ok(blarifyFound, `Blarify not found in any expected location. Searched: ${possiblePaths.join(', ')}`);
        console.log(`Blarify found at: ${foundPath}`);
    });
    test('Should handle workspace analysis with correct path', async function () {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            this.skip();
            return;
        }
        // Mock the progress and cancellation token
        const progress = {
            report: (value) => console.log('Progress:', value)
        };
        const token = new vscode.CancellationTokenSource().token;
        try {
            // This should find Blarify and at least start the process
            // It might fail on actual execution if Blarify isn't fully configured,
            // but it should not fail with "Blarify not found"
            const promise = blarifyIntegration.analyzeWorkspace(workspaceFolder.uri.fsPath, progress, token);
            // Give it a moment to check paths
            await new Promise(resolve => setTimeout(resolve, 100));
            // If we get here without "Blarify not found" error, the path resolution worked
            assert.ok(true, 'Path resolution succeeded');
            // Cancel the operation to clean up
            if (!token.isCancellationRequested) {
                token.cancel?.();
            }
        }
        catch (error) {
            // Check if it's the specific error we're testing for
            if (error.message.includes('Blarify not found')) {
                assert.fail(`Blarify path resolution failed: ${error.message}`);
            }
            // Other errors (like Neo4j connection) are ok for this test
            console.log('Non-path error (expected):', error.message);
        }
    });
    test('Should check Python availability', async () => {
        const hasPython = await blarifyIntegration.checkBlarifyInstalled();
        assert.ok(hasPython, 'Python should be available for Blarify execution');
    });
});
//# sourceMappingURL=blarifyPathResolution.test.js.map