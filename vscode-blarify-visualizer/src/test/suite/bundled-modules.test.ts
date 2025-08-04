import * as assert from 'assert';
import * as path from 'path';

suite('Bundled Modules Test Suite', () => {
    test('neo4j-container-manager should load successfully', () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        const managerPath = path.join(extensionPath, 'bundled', 'neo4j-container-manager');
        
        try {
            const { Neo4jContainerManager } = require(managerPath);
            assert.ok(Neo4jContainerManager, 'Neo4jContainerManager should be exported');
            assert.strictEqual(typeof Neo4jContainerManager, 'function', 'Neo4jContainerManager should be a constructor');
            
            // Try to create an instance with mock logger
            const manager = new Neo4jContainerManager({
                logger: {
                    info: () => {},
                    error: () => {},
                    warn: () => {},
                    debug: () => {}
                }
            });
            assert.ok(manager, 'Should be able to create Neo4jContainerManager instance');
        } catch (error) {
            assert.fail(`Failed to load neo4j-container-manager: ${error}`);
        }
    });
    
    test('cue module should exist', () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        const cuePath = path.join(extensionPath, 'bundled', 'cue');
        const fs = require('fs');
        
        assert.ok(fs.existsSync(cuePath), 'Blarify directory should exist');
        assert.ok(fs.existsSync(path.join(cuePath, 'main.py')), 'Blarify main.py should exist');
        assert.ok(fs.existsSync(path.join(cuePath, '__init__.py')), 'Blarify __init__.py should exist');
    });
    
    test('required dependencies should be available', () => {
        // Test that the extension's dependencies can be loaded
        const deps = ['dockerode', 'neo4j-driver', 'portfinder', 'tar', 'winston'];
        
        for (const dep of deps) {
            try {
                require(dep);
                assert.ok(true, `${dep} loaded successfully`);
            } catch (error) {
                assert.fail(`Failed to load dependency ${dep}: ${error}`);
            }
        }
    });
});