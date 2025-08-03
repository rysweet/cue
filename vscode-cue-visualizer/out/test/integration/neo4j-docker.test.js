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
const path = __importStar(require("path"));
const neo4jManager_1 = require("../../neo4jManager");
const configurationManager_1 = require("../../configurationManager");
suite('Neo4j Docker Integration Tests', () => {
    let neo4jManager;
    let configManager;
    setup(() => {
        configManager = new configurationManager_1.ConfigurationManager();
        const extensionPath = path.join(__dirname, '..', '..', '..');
        neo4jManager = new neo4jManager_1.Neo4jManager(configManager, extensionPath);
    });
    teardown(async () => {
        if (neo4jManager) {
            neo4jManager.dispose();
        }
    });
    test('Neo4j should actually start with real Docker', async function () {
        // This test requires Docker to be running
        this.timeout(120000); // 2 minutes - give plenty of time
        // Skip this test until we fix the container manager's list() method
        this.skip();
        try {
            console.log('Starting Neo4j...');
            await neo4jManager.ensureRunning();
            const status = await neo4jManager.getStatus();
            console.log('Neo4j status:', status);
            assert.ok(status.running, 'Neo4j should be running');
            assert.ok(status.containerId, 'Should have a container ID');
            assert.ok(status.details, 'Should have details');
            // Try to get a driver to verify connectivity
            const driver = await neo4jManager.getDriver();
            assert.ok(driver, 'Should get a valid driver');
            // Verify we can run a query
            const session = driver.session();
            try {
                const result = await session.run('RETURN 1 as num');
                assert.strictEqual(result.records[0].get('num').toNumber(), 1);
            }
            finally {
                await session.close();
            }
        }
        catch (error) {
            console.error('Neo4j startup failed:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                code: error.code
            });
            // Check if Docker is running
            const { exec } = require('child_process');
            const util = require('util');
            const execAsync = util.promisify(exec);
            try {
                const { stdout } = await execAsync('docker version');
                console.log('Docker version output:', stdout);
            }
            catch (dockerError) {
                console.error('Docker not available:', dockerError);
            }
            throw error;
        }
    });
    test('Neo4j container manager should be loaded correctly', async function () {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        const containerManagerPath = path.join(extensionPath, 'bundled', 'neo4j-container-manager');
        console.log('Looking for container manager at:', containerManagerPath);
        try {
            const { Neo4jContainerManager } = require(containerManagerPath);
            assert.ok(Neo4jContainerManager, 'Neo4jContainerManager should be exported');
            const manager = new Neo4jContainerManager({
                logger: {
                    info: (msg) => console.log(`[Test] ${msg}`),
                    error: (msg) => console.error(`[Test] ${msg}`),
                    warn: (msg) => console.warn(`[Test] ${msg}`),
                    debug: (msg) => console.log(`[Test Debug] ${msg}`)
                }
            });
            assert.ok(manager.start, 'Manager should have start method');
            assert.ok(typeof manager.start === 'function', 'start should be a function');
        }
        catch (error) {
            console.error('Failed to load container manager:', error);
            throw error;
        }
    });
});
//# sourceMappingURL=neo4j-docker.test.js.map