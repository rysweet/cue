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
                    info: () => { },
                    error: () => { },
                    warn: () => { },
                    debug: () => { }
                }
            });
            assert.ok(manager, 'Should be able to create Neo4jContainerManager instance');
        }
        catch (error) {
            assert.fail(`Failed to load neo4j-container-manager: ${error}`);
        }
    });
    test('blarify module should exist', () => {
        const extensionPath = path.join(__dirname, '..', '..', '..');
        const blarifyPath = path.join(extensionPath, 'bundled', 'blarify');
        const fs = require('fs');
        assert.ok(fs.existsSync(blarifyPath), 'Blarify directory should exist');
        assert.ok(fs.existsSync(path.join(blarifyPath, 'main.py')), 'Blarify main.py should exist');
        assert.ok(fs.existsSync(path.join(blarifyPath, '__init__.py')), 'Blarify __init__.py should exist');
    });
    test('required dependencies should be available', () => {
        // Test that the extension's dependencies can be loaded
        const deps = ['dockerode', 'neo4j-driver', 'portfinder', 'tar', 'winston'];
        for (const dep of deps) {
            try {
                require(dep);
                assert.ok(true, `${dep} loaded successfully`);
            }
            catch (error) {
                assert.fail(`Failed to load dependency ${dep}: ${error}`);
            }
        }
    });
});
//# sourceMappingURL=bundled-modules.test.js.map