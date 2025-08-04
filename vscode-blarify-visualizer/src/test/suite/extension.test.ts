import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';
import * as path from 'path';
import { Neo4jManager } from '../../neo4jManager';
import { ConfigurationManager } from '../../configurationManager';
import { BlarifyIntegration } from '../../cueIntegration';
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
        assert.ok(vscode.extensions.getExtension('cue.cue-visualizer'));
    });
    
    test('Should activate successfully', async () => {
        const extension = vscode.extensions.getExtension('cue.cue-visualizer');
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
                name: 'cue-neo4j-vscode',
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
            name: 'cue-neo4j-vscode',
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
            name: 'cue-neo4j-vscode',
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
    let cueIntegration: BlarifyIntegration;
    let configManager: ConfigurationManager;
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new ConfigurationManager();
        const extensionPath = path.resolve(__dirname, '..', '..', '..');
        const neo4jManager = new Neo4jManager(configManager, extensionPath);
        cueIntegration = new BlarifyIntegration(configManager, extensionPath, neo4jManager);
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
        
        const isInstalled = await cueIntegration.checkBlarifyInstalled();
        assert.ok(isInstalled);
    });
    
    test('Should handle Blarify bundled with extension', async () => {
        // Blarify is now bundled with the extension, so it should always be "installed"
        const extensionPath = path.join(__dirname, '..', '..', '..');
        const cuePath = path.join(extensionPath, 'bundled', 'cue', 'main.py');
        const fs = require('fs');
        
        // Check that the bundled Blarify exists
        const bundledExists = fs.existsSync(cuePath);
        assert.ok(bundledExists, 'Bundled Blarify should exist');
        
        // The checkBlarifyInstalled method should return true for bundled Blarify
        const isInstalled = await cueIntegration.checkBlarifyInstalled();
        assert.ok(isInstalled, 'Blarify should be detected as installed (bundled)');
    });
    
    test('Should build environment variables correctly', async () => {
        const childProcess = require('child_process');
        const spawnStub = sandbox.stub(childProcess, 'spawn');
        
        // Mock configuration
        sandbox.stub(configManager, 'getExcludePatterns').returns(['node_modules', '.git']);
        sandbox.stub(configManager, 'getAzureOpenAIConfig').returns({
            apiKey: 'test-key',
            endpoint: 'https://test.openai.azure.com',
            deploymentName: 'gpt-4'
        });
        sandbox.stub(configManager, 'getNeo4jPassword').returns('test-password');
        
        // Mock the Neo4j manager to avoid connection attempts
        const extensionPath = path.resolve(__dirname, '..', '..', '..');
        const mockNeo4jManager = new Neo4jManager(configManager, extensionPath);
        sandbox.stub(mockNeo4jManager, 'ensureRunning').resolves();
        
        // Create new BlarifyIntegration instance with mocked Neo4j manager
        const testBlarifyIntegration = new BlarifyIntegration(configManager, extensionPath, mockNeo4jManager);
        
        // Create mock process and progress
        const mockProcess = {
            stdout: { on: sandbox.stub() },
            stderr: { on: sandbox.stub() },
            on: sandbox.stub().callsArgWith(1, 0), // Simulate successful exit
            kill: sandbox.stub()
        };
        spawnStub.returns(mockProcess);
        
        const progress = { report: sandbox.stub() };
        const token = { 
            isCancellationRequested: false,
            onCancellationRequested: sandbox.stub()
        };
        
        try {
            await testBlarifyIntegration.analyzeWorkspace('/test/workspace', progress as any, token as any);
        } catch (error) {
            // Ignore JSON parsing errors, we just want to verify spawn was called correctly
        }
        
        // Verify spawn was called with correct arguments
        assert.ok(spawnStub.calledOnce, 'spawn should be called once');
        const spawnCall = spawnStub.getCall(0);
        
        // Check arguments: should only have main.py path, no 'ingest' command
        const args = spawnCall.args[1];
        assert.ok(args.length === 1, `Expected 1 argument, got ${args.length}: ${JSON.stringify(args)}`);
        assert.ok(args[0].endsWith('main.py'), 'Should call main.py directly');
        assert.ok(!args.includes('ingest'), 'Should not include ingest command');
        
        // Check environment variables
        const options = spawnCall.args[2];
        const env = options.env;
        
        assert.strictEqual(env.ROOT_PATH, '/test/workspace', 'ROOT_PATH should be set');
        assert.strictEqual(env.NEO4J_URI, 'bolt://localhost:7957', 'NEO4J_URI should be set');
        assert.strictEqual(env.NEO4J_USER, 'neo4j', 'NEO4J_USER should be set');
        assert.strictEqual(env.NEO4J_PASSWORD, 'test-password', 'NEO4J_PASSWORD should be set');
        assert.strictEqual(env.ENABLE_DOCUMENTATION_NODES, 'true', 'ENABLE_DOCUMENTATION_NODES should be true');
        assert.strictEqual(env.ENABLE_LLM_DESCRIPTIONS, 'true', 'ENABLE_LLM_DESCRIPTIONS should be true');
        assert.strictEqual(env.AZURE_API_KEY, 'test-key', 'AZURE_API_KEY should be set');
        assert.strictEqual(env.AZURE_ENDPOINT, 'https://test.openai.azure.com', 'AZURE_ENDPOINT should be set');
        assert.strictEqual(env.AZURE_DEPLOYMENT, 'gpt-4', 'AZURE_DEPLOYMENT should be set');
        assert.strictEqual(env.NAMES_TO_SKIP, 'node_modules,.git', 'NAMES_TO_SKIP should be comma-separated');
        assert.ok(env.PYTHONPATH?.includes('bundled'), 'PYTHONPATH should include bundled directory');
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