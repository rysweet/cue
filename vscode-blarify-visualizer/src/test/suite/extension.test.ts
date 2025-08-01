import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';
import * as path from 'path';
import { Neo4jManager } from '../../neo4jManager';
import { ConfigurationManager } from '../../configurationManager';
import { BlarifyIntegration } from '../../blarifyIntegration';
import { GraphDataProvider } from '../../graphDataProvider';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');
    
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('blarify.blarify-visualizer'));
    });
    
    test('Should activate successfully', async () => {
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        assert.ok(extension);
        
        // The extension should be active after activation events
        if (!extension.isActive) {
            await extension.activate();
        }
        
        assert.ok(extension.isActive);
    });
});

suite('Neo4jManager Test Suite', () => {
    let neo4jManager: Neo4jManager;
    let configManager: ConfigurationManager;
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new ConfigurationManager();
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Should check Neo4j status', async () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        neo4jManager = new Neo4jManager(configManager, extensionPath);
        
        // Test 1: No instance - should return not running
        let status = await neo4jManager.getStatus();
        assert.strictEqual(status.running, false, 'Status should be false when no instance exists');
        
        // Test 2: With instance - should return running
        (neo4jManager as any).instance = {
            uri: 'bolt://localhost:7687',
            username: 'neo4j',
            password: 'test-password',
            containerId: 'test-container',
            port: 7687
        };
        
        status = await neo4jManager.getStatus();
        assert.strictEqual(status.running, true, 'Status should be true when instance exists');
        assert.strictEqual(status.containerId, 'test-container', 'Should return container ID');
        assert.ok(status.details?.includes('7687'), 'Details should include port');
    });
    
    test.skip('Should handle container start (requires Docker)', async () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        
        // Mock the require function to avoid loading the actual module
        const mockManager = {
            listInstances: sandbox.stub().returns([]),
            startContainer: sandbox.stub().resolves({
                name: 'blarify-neo4j-vscode',
                port: 7687,
                containerId: 'test-container',
                uri: 'bolt://localhost:7687',
                username: 'neo4j',
                password: 'test-password'
            })
        };
        
        // Stub the require call
        const requireStub = sandbox.stub();
        requireStub.withArgs(path.join(extensionPath, 'bundled', 'neo4j-container-manager'))
            .returns({ Neo4jContainerManager: sandbox.stub().returns(mockManager) });
        
        // Replace the global require temporarily
        const originalRequire = require;
        (global as any).require = requireStub;
        
        try {
            neo4jManager = new Neo4jManager(configManager, extensionPath);
            
            // Mock neo4j-driver
            sandbox.stub(neo4jManager as any, 'connectToNeo4j').resolves();
            
            await neo4jManager.ensureRunning();
            
            assert.ok(mockManager.startContainer.called, 'Container should be started');
        } finally {
            // Restore original require
            (global as any).require = originalRequire;
        }
    });

    test.skip('Should start container with auto-generated password (requires Docker)', async () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        neo4jManager = new Neo4jManager(configManager, extensionPath);
        
        const mockInstance = {
            name: 'blarify-neo4j-vscode',
            port: 7688,
            containerId: 'test-container',
            uri: 'bolt://localhost:7688',
            username: 'neo4j',
            password: 'auto-generated-password-123'
        };
        
        const mockManager = {
            listInstances: sandbox.stub().returns([]),
            startContainer: sandbox.stub().resolves(mockInstance)
        };
        
        const mockDriver = {
            verifyConnectivity: sandbox.stub().resolves()
        };
        
        const neo4jDriverStub = {
            driver: sandbox.stub().returns(mockDriver),
            auth: {
                basic: sandbox.stub().returns({})
            }
        };
        
        // Mock require for neo4j-driver
        const requireStub = sandbox.stub();
        requireStub.withArgs('neo4j-driver').returns(neo4jDriverStub);
        requireStub.withArgs('../bundled/neo4j-container-manager').returns({
            Neo4jContainerManager: sandbox.stub().returns(mockManager)
        });
        (neo4jManager as any).require = requireStub;
        
        await neo4jManager.ensureRunning();
        
        // Verify container was started with correct parameters
        assert.ok(mockManager.startContainer.calledOnce);
        const startCall = mockManager.startContainer.getCall(0);
        assert.deepEqual(startCall.args[0], {
            name: 'blarify-neo4j-vscode',
            environment: 'development'
        });
        
        // Verify no password was provided (manager generates it)
        assert.ok(!startCall.args[0].password);
    });
});

suite('ConfigurationManager Test Suite', () => {
    let configManager: ConfigurationManager;
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new ConfigurationManager();
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Should retrieve Azure OpenAI config', () => {
        const getConfigStub = sandbox.stub(vscode.workspace, 'getConfiguration').returns({
            get: (key: string) => {
                const configs: { [key: string]: any } = {
                    'azureOpenAI.apiKey': 'test-key',
                    'azureOpenAI.endpoint': 'https://test.openai.azure.com',
                    'azureOpenAI.deploymentName': 'gpt-4'
                };
                return configs[key];
            }
        } as any);
        
        const config = configManager.getAzureOpenAIConfig();
        
        assert.strictEqual(config.apiKey, 'test-key');
        assert.strictEqual(config.endpoint, 'https://test.openai.azure.com');
        assert.strictEqual(config.deploymentName, 'gpt-4');
    });
    
    test('Should check if configured', () => {
        sandbox.stub(vscode.workspace, 'getConfiguration').returns({
            get: (key: string) => {
                const configs: { [key: string]: any } = {
                    'azureOpenAI.apiKey': 'test-key',
                    'azureOpenAI.endpoint': 'https://test.openai.azure.com'
                };
                return configs[key];
            }
        } as any);
        
        assert.ok(configManager.isConfigured());
    });
    
    test('Should return false when not configured', () => {
        sandbox.stub(vscode.workspace, 'getConfiguration').returns({
            get: () => ''
        } as any);
        
        assert.ok(!configManager.isConfigured());
    });
});

suite('BlarifyIntegration Test Suite', () => {
    let blarifyIntegration: BlarifyIntegration;
    let configManager: ConfigurationManager;
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new ConfigurationManager();
        blarifyIntegration = new BlarifyIntegration(configManager, path.resolve(__dirname, '..', '..', '..'));
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Should check if Blarify is installed', async () => {
        const spawnStub = sandbox.stub(require('child_process'), 'spawn');
        const processStub = {
            on: (event: string, callback: Function) => {
                if (event === 'close') {
                    callback(0);
                }
            }
        };
        spawnStub.returns(processStub);
        
        const isInstalled = await blarifyIntegration.checkBlarifyInstalled();
        assert.ok(isInstalled);
    });
    
    test('Should handle Blarify bundled with extension', async () => {
        // Blarify is now bundled with the extension, so it should always be "installed"
        const extensionPath = path.join(__dirname, '..', '..', '..');
        const blarifyPath = path.join(extensionPath, 'bundled', 'blarify', 'main.py');
        const fs = require('fs');
        
        // Check that the bundled Blarify exists
        const bundledExists = fs.existsSync(blarifyPath);
        assert.ok(bundledExists, 'Bundled Blarify should exist');
        
        // The checkBlarifyInstalled method should return true for bundled Blarify
        const isInstalled = await blarifyIntegration.checkBlarifyInstalled();
        assert.ok(isInstalled, 'Blarify should be detected as installed (bundled)');
    });
});

suite('GraphDataProvider Test Suite', () => {
    let graphDataProvider: GraphDataProvider;
    let neo4jManager: Neo4jManager;
    let configManager: ConfigurationManager;
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new ConfigurationManager();
        const extensionPath = path.join(__dirname, '..', '..', '..');
        neo4jManager = new Neo4jManager(configManager, extensionPath);
        graphDataProvider = new GraphDataProvider(neo4jManager, configManager);
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Should handle no driver connection', async () => {
        sandbox.stub(neo4jManager, 'getDriver').resolves(undefined);
        
        try {
            await graphDataProvider.getGraphData();
            assert.fail('Should have thrown error');
        } catch (error: any) {
            assert.strictEqual(error.message, 'Neo4j driver not connected');
        }
    });
    
    test('Should build overview query', async () => {
        const mockDriver = {
            session: () => ({
                run: sandbox.stub().resolves({
                    records: []
                }),
                close: sandbox.stub().resolves()
            })
        };
        
        sandbox.stub(neo4jManager, 'getDriver').resolves(mockDriver as any);
        sandbox.stub(configManager, 'getVisualizationConfig').returns({
            nodeLimit: 100,
            defaultLayout: 'force-directed'
        });
        
        const data = await graphDataProvider.getGraphData();
        
        assert.strictEqual(data.nodes.length, 0);
        assert.strictEqual(data.edges.length, 0);
        assert.ok(data.metadata);
    });
});