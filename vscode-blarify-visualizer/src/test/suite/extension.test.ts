import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';
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
    
    test('Should register all commands', async () => {
        const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
        await extension?.activate();
        
        const commands = await vscode.commands.getCommands();
        
        assert.ok(commands.includes('blarifyVisualizer.showVisualization'));
        assert.ok(commands.includes('blarifyVisualizer.ingestWorkspace'));
        assert.ok(commands.includes('blarifyVisualizer.updateGraph'));
        assert.ok(commands.includes('blarifyVisualizer.searchGraph'));
    });
});

suite('Neo4jManager Test Suite', () => {
    let neo4jManager: Neo4jManager;
    let configManager: ConfigurationManager;
    let sandbox: sinon.SinonSandbox;
    
    setup(() => {
        sandbox = sinon.createSandbox();
        configManager = new ConfigurationManager();
        sandbox.stub(configManager, 'getNeo4jConfig').returns({
            uri: 'bolt://localhost:7687',
            username: 'neo4j',
            password: 'test'
        });
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Should check Neo4j status', async () => {
        neo4jManager = new Neo4jManager(configManager);
        const dockerStub = {
            listContainers: sandbox.stub().resolves([])
        };
        (neo4jManager as any).docker = dockerStub;
        
        const status = await neo4jManager.getStatus();
        assert.strictEqual(status.running, false);
    });
    
    test('Should handle container start', async () => {
        neo4jManager = new Neo4jManager(configManager);
        const containerStub = {
            start: sandbox.stub().resolves(),
            id: 'test-container-id'
        };
        
        const dockerStub = {
            listContainers: sandbox.stub().resolves([]),
            getImage: sandbox.stub().returns({
                inspect: sandbox.stub().resolves({})
            }),
            createContainer: sandbox.stub().resolves(containerStub),
            getContainer: sandbox.stub().returns(containerStub)
        };
        
        (neo4jManager as any).docker = dockerStub;
        sandbox.stub(neo4jManager as any, 'waitForNeo4j').resolves();
        sandbox.stub(neo4jManager as any, 'connectDriver').resolves();
        
        await neo4jManager.ensureRunning();
        
        assert.ok(dockerStub.createContainer.called);
        assert.ok(containerStub.start.called);
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
        blarifyIntegration = new BlarifyIntegration(configManager);
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
    
    test('Should handle Blarify not installed', async () => {
        const spawnStub = sandbox.stub(require('child_process'), 'spawn');
        const processStub = {
            on: (event: string, callback: Function) => {
                if (event === 'error') {
                    callback(new Error('ENOENT'));
                }
            }
        };
        spawnStub.returns(processStub);
        
        const isInstalled = await blarifyIntegration.checkBlarifyInstalled();
        assert.ok(!isInstalled);
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
        neo4jManager = new Neo4jManager(configManager);
        graphDataProvider = new GraphDataProvider(neo4jManager, configManager);
    });
    
    teardown(() => {
        sandbox.restore();
    });
    
    test('Should handle no driver connection', async () => {
        sandbox.stub(neo4jManager, 'getDriver').returns(undefined);
        
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
        
        sandbox.stub(neo4jManager, 'getDriver').returns(mockDriver as any);
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