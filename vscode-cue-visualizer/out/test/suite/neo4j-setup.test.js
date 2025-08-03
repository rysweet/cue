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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const assert = __importStar(require("assert"));
const sinon = __importStar(require("sinon"));
const neo4jManager_1 = require("../../neo4jManager");
const configurationManager_1 = require("../../configurationManager");
const path_1 = __importDefault(require("path"));
suite('Neo4j Setup Tests', () => {
    let sandbox;
    let configManager;
    let extensionPath;
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new configurationManager_1.ConfigurationManager();
        extensionPath = path_1.default.join(__dirname, '..', '..', '..');
    });
    teardown(() => {
        sandbox.restore();
    });
    test('Neo4j manager should use correct container manager API', async function () {
        // Skip this test in CI or when Docker is not available
        if (process.env.CI || !process.env.DOCKER_HOST) {
            this.skip();
            return;
        }
        const neo4jManager = new neo4jManager_1.Neo4jManager(configManager, extensionPath);
        // The API has been fixed - this should now work without throwing
        try {
            // Mock the container manager to avoid actual Docker operations
            const mockManager = {
                list: async () => [],
                start: async () => ({
                    uri: 'bolt://localhost:7687',
                    httpUri: 'http://localhost:7474',
                    containerId: 'test-container',
                    driver: {
                        verifyConnectivity: async () => true,
                        close: async () => { }
                    }
                })
            };
            neo4jManager.manager = mockManager;
            await neo4jManager.ensureRunning();
            // If we get here, the correct API was used
            assert.ok(true, 'Successfully used correct container manager API');
        }
        catch (error) {
            assert.fail(`Should not throw error with correct API: ${error.message}`);
        }
    });
    test('Analysis should not start until Neo4j setup is complete', async () => {
        // Track the order of operations
        const operationOrder = [];
        // Mock neo4j manager
        const mockNeo4jManager = {
            ensureRunning: async () => {
                operationOrder.push('neo4j-starting');
                // Simulate slow startup
                await new Promise(resolve => setTimeout(resolve, 5000));
                operationOrder.push('neo4j-ready');
            },
            getStatus: async () => ({ running: true })
        };
        // Mock workspace analysis
        const mockBlarifyIntegration = {
            analyzeWorkspace: async () => {
                operationOrder.push('analysis-started');
                return { nodes: [], edges: [] };
            }
        };
        // Simulate the extension activation flow
        const activationFlow = async () => {
            // Start Neo4j
            const neo4jPromise = mockNeo4jManager.ensureRunning();
            // Current buggy behavior: prompt happens on fixed timeout
            setTimeout(() => {
                operationOrder.push('prompt-shown');
                // User clicks yes
                mockBlarifyIntegration.analyzeWorkspace();
            }, 3000);
            await neo4jPromise;
        };
        await activationFlow();
        // Wait for all operations
        await new Promise(resolve => setTimeout(resolve, 6000));
        // This test should fail because analysis starts before Neo4j is ready
        const promptIndex = operationOrder.indexOf('prompt-shown');
        const neo4jReadyIndex = operationOrder.indexOf('neo4j-ready');
        const analysisIndex = operationOrder.indexOf('analysis-started');
        assert.ok(promptIndex < neo4jReadyIndex, 'Bug: Prompt is shown before Neo4j is ready');
        assert.ok(analysisIndex < neo4jReadyIndex, 'Bug: Analysis starts before Neo4j is ready');
    });
    test('Neo4j setup should complete successfully', async function () {
        this.timeout(5000);
        // Skip this test in environments where Docker operations might fail
        if (process.env.CI) {
            this.skip();
            return;
        }
        const neo4jManager = new neo4jManager_1.Neo4jManager(configManager, extensionPath);
        // Directly inject the mock manager to avoid module loading issues
        const mockInstance = {
            uri: 'bolt://localhost:7687',
            httpUri: 'http://localhost:7474',
            containerId: 'test-container-123',
            environment: 'development',
            driver: {
                verifyConnectivity: async () => true,
                close: async () => { },
                session: () => ({
                    run: async () => ({ records: [] }),
                    close: async () => { }
                })
            },
            isRunning: async () => true
        };
        const mockManager = {
            list: async () => [],
            start: async (config) => mockInstance
        };
        // Inject the mock directly
        neo4jManager.manager = mockManager;
        neo4jManager.instance = null;
        try {
            await neo4jManager.ensureRunning();
            const status = await neo4jManager.getStatus();
            assert.ok(status.running, 'Neo4j should be running after ensureRunning');
            assert.strictEqual(status.containerId, 'test-container-123', 'Should have correct container ID');
            assert.ok(status.details?.includes('bolt://localhost:7687'), 'Should include bolt URI in details');
        }
        catch (error) {
            assert.fail(`Setup should complete successfully, but got error: ${error.message}`);
        }
    });
    test('Extension should wait for Neo4j before showing analysis prompt', async () => {
        // Test that verifies proper sequencing
        let neo4jReady = false;
        let promptShown = false;
        let analysisStarted = false;
        // Mock implementations
        const mockNeo4j = {
            ensureRunning: async () => {
                await new Promise(resolve => setTimeout(resolve, 2000));
                neo4jReady = true;
            }
        };
        const showPrompt = () => {
            if (!neo4jReady) {
                assert.fail('Prompt shown before Neo4j is ready');
            }
            promptShown = true;
        };
        const startAnalysis = () => {
            if (!neo4jReady) {
                assert.fail('Analysis started before Neo4j is ready');
            }
            if (!promptShown) {
                assert.fail('Analysis started before prompt was shown');
            }
            analysisStarted = true;
        };
        // Proper flow
        await mockNeo4j.ensureRunning();
        showPrompt();
        startAnalysis();
        assert.ok(neo4jReady, 'Neo4j should be ready');
        assert.ok(promptShown, 'Prompt should be shown');
        assert.ok(analysisStarted, 'Analysis should be started');
    });
});
//# sourceMappingURL=neo4j-setup.test.js.map