const path = require('path');

console.log('Testing bundled neo4j-container-manager...\n');

try {
    const managerPath = path.join(__dirname, 'bundled', 'neo4j-container-manager');
    console.log(`Loading from: ${managerPath}`);
    
    const { Neo4jContainerManager } = require(managerPath);
    console.log('✓ Successfully loaded Neo4jContainerManager');
    console.log(`  Type: ${typeof Neo4jContainerManager}`);
    console.log(`  Constructor: ${Neo4jContainerManager.constructor.name}`);
    
    // Try to create an instance
    const manager = new Neo4jContainerManager({
        logger: {
            info: msg => console.log(`[INFO] ${msg}`),
            error: msg => console.error(`[ERROR] ${msg}`),
            warn: msg => console.warn(`[WARN] ${msg}`),
            debug: msg => console.log(`[DEBUG] ${msg}`)
        }
    });
    console.log('✓ Successfully created Neo4jContainerManager instance');
} catch (error) {
    console.error('✗ Failed to load neo4j-container-manager:');
    console.error(error);
}