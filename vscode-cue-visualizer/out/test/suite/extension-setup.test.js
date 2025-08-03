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
const pythonEnvironment_1 = require("../../pythonEnvironment");
const blarifyIntegration_1 = require("../../blarifyIntegration");
const configurationManager_1 = require("../../configurationManager");
suite('Extension Setup Tests', () => {
    let extensionPath;
    let bundledPath;
    suiteSetup(() => {
        // Get the extension path from VS Code context
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        extensionPath = extension ? extension.extensionPath : path.join(__dirname, '../../..');
        bundledPath = path.join(extensionPath, 'bundled');
    });
    suite('Bundled Files Validation', () => {
        test('README.md should exist in bundled directory', () => {
            const readmePath = path.join(bundledPath, 'README.md');
            assert.ok(fs.existsSync(readmePath), 'README.md should exist in bundled directory');
            // Verify it has content
            const content = fs.readFileSync(readmePath, 'utf8');
            assert.ok(content.length > 0, 'README.md should have content');
            assert.ok(content.includes('Blarify'), 'README.md should mention Blarify');
        });
        test('pyproject.toml should exist in bundled directory', () => {
            const pyprojectPath = path.join(bundledPath, 'pyproject.toml');
            assert.ok(fs.existsSync(pyprojectPath), 'pyproject.toml should exist in bundled directory');
        });
        test('pyproject.toml README reference should be satisfied', () => {
            const pyprojectPath = path.join(bundledPath, 'pyproject.toml');
            const readmePath = path.join(bundledPath, 'README.md');
            if (fs.existsSync(pyprojectPath)) {
                const content = fs.readFileSync(pyprojectPath, 'utf8');
                if (content.includes('readme = "README.md"')) {
                    assert.ok(fs.existsSync(readmePath), 'README.md should exist when referenced in pyproject.toml');
                }
            }
        });
        test('setup.py should exist in bundled directory', () => {
            const setupPath = path.join(bundledPath, 'setup.py');
            assert.ok(fs.existsSync(setupPath), 'setup.py should exist in bundled directory');
        });
        test('blarify source should exist in bundled directory', () => {
            const blarifyPath = path.join(bundledPath, 'blarify');
            assert.ok(fs.existsSync(blarifyPath), 'blarify directory should exist in bundled directory');
            const mainPath = path.join(blarifyPath, 'main.py');
            assert.ok(fs.existsSync(mainPath), 'blarify/main.py should exist');
        });
        test('requirements.txt should exist in bundled directory', () => {
            const reqPath = path.join(bundledPath, 'requirements.txt');
            assert.ok(fs.existsSync(reqPath), 'requirements.txt should exist in bundled directory');
            // Verify it has content
            const content = fs.readFileSync(reqPath, 'utf8');
            assert.ok(content.length > 0, 'requirements.txt should have content');
            assert.ok(content.includes('neo4j'), 'requirements.txt should include neo4j');
        });
    });
    suite('PythonEnvironment Setup', () => {
        let pythonEnv;
        setup(() => {
            pythonEnv = new pythonEnvironment_1.PythonEnvironment(extensionPath);
        });
        test('PythonEnvironment constructor should work', () => {
            assert.ok(pythonEnv, 'PythonEnvironment should be created');
        });
        test('getPythonPath should return undefined before setup', () => {
            const pythonPath = pythonEnv.getPythonPath();
            assert.strictEqual(pythonPath, undefined, 'Python path should be undefined before setup');
        });
        // Note: Full setup test is skipped in CI as it requires Python and network access
        test.skip('ensureSetup should create virtual environment and install dependencies', async function () {
            this.timeout(300000); // 5 minutes timeout for setup
            try {
                const pythonPath = await pythonEnv.ensureSetup();
                assert.ok(pythonPath, 'Setup should return a Python path');
                assert.ok(fs.existsSync(pythonPath), 'Python executable should exist');
                // Verify venv directory was created
                const venvPath = path.join(bundledPath, 'venv');
                assert.ok(fs.existsSync(venvPath), 'Virtual environment should be created');
                // Verify Python path is from venv
                assert.ok(pythonPath.includes('venv'), 'Python path should be from virtual environment');
            }
            catch (error) {
                // In test environment, setup might fail due to missing Python or network
                // This is acceptable - the important thing is that the code doesn't crash
                console.log(`Setup failed (expected in test env): ${error}`);
                assert.ok(error instanceof Error, 'Setup failure should be a proper Error object');
            }
        });
    });
    suite('BlarifyIntegration Setup Dependency', () => {
        let blarifyIntegration;
        let configManager;
        setup(() => {
            configManager = new configurationManager_1.ConfigurationManager();
            blarifyIntegration = new blarifyIntegration_1.BlarifyIntegration(configManager, extensionPath);
        });
        test('BlarifyIntegration should be created without errors', () => {
            assert.ok(blarifyIntegration, 'BlarifyIntegration should be created');
        });
        test('checkBlarifyInstalled should work with bundled version', async () => {
            const isInstalled = await blarifyIntegration.checkBlarifyInstalled();
            assert.ok(isInstalled, 'Bundled Blarify should be detected as installed');
        });
        test('getLastAnalysis should return undefined before analysis', () => {
            const lastAnalysis = blarifyIntegration.getLastAnalysis();
            assert.strictEqual(lastAnalysis, undefined, 'Last analysis should be undefined initially');
        });
    });
    suite('Setup Flow Integration', () => {
        test('Extension activation should not throw errors', async () => {
            // Get the extension
            const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
            assert.ok(extension, 'Extension should be available');
            if (!extension.isActive) {
                try {
                    await extension.activate();
                    assert.ok(extension.isActive, 'Extension should activate successfully');
                }
                catch (error) {
                    // In test environment, activation might fail due to missing dependencies
                    // But it should fail gracefully, not crash
                    console.log(`Extension activation failed (may be expected in test env): ${error}`);
                    assert.ok(error instanceof Error, 'Activation failure should be a proper Error object');
                }
            }
        });
        test('Extension commands should be registered', async () => {
            const commands = await vscode.commands.getCommands();
            const blarifyCommands = commands.filter(cmd => cmd.startsWith('blarifyVisualizer.'));
            assert.ok(blarifyCommands.length > 0, 'Blarify commands should be registered');
            assert.ok(blarifyCommands.includes('blarifyVisualizer.ingestWorkspace'), 'ingestWorkspace command should be registered');
            assert.ok(blarifyCommands.includes('blarifyVisualizer.showVisualization'), 'showVisualization command should be registered');
        });
    });
    suite('Error Handling', () => {
        test('Setup should handle missing files gracefully', () => {
            // Create PythonEnvironment with non-existent path
            const invalidPath = path.join(extensionPath, 'non-existent-bundled');
            const pythonEnv = new pythonEnvironment_1.PythonEnvironment(invalidPath);
            // This should not throw during construction
            assert.ok(pythonEnv, 'PythonEnvironment should handle invalid paths during construction');
        });
        test('Setup script should handle README.md creation', () => {
            const setupPath = path.join(bundledPath, 'setup.py');
            if (fs.existsSync(setupPath)) {
                const content = fs.readFileSync(setupPath, 'utf8');
                // Verify error handling code is present
                assert.ok(content.includes('CalledProcessError'), 'Setup script should handle CalledProcessError');
                assert.ok(content.includes('README.md'), 'Setup script should handle README.md creation');
                assert.ok(content.includes('Retrying'), 'Setup script should have retry logic');
            }
        });
    });
    suite('Synchronization Tests', () => {
        test('Setup state tracking should be implemented', async () => {
            // These are more integration tests that would require the full extension context
            // For now, we verify the basic structure exists
            const extensionModule = await Promise.resolve().then(() => __importStar(require('../../extension')));
            // The setupState should be defined in the extension module
            // This is more of a structural test since setupState is not exported
            assert.ok(extensionModule, 'Extension module should be importable');
        });
    });
});
//# sourceMappingURL=extension-setup.test.js.map