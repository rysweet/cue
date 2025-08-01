// Debug script to understand Neo4j startup failure
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Neo4j Startup Debug Script');
console.log('==========================\n');

// Check what's in the bundled directory
const extensionPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0';
const bundledPath = path.join(extensionPath, 'bundled', 'neo4j-container-manager');

console.log(`Extension path: ${extensionPath}`);
console.log(`Bundled path: ${bundledPath}`);

// Check if the bundled neo4j-container-manager exists
if (fs.existsSync(bundledPath)) {
    console.log('✓ Bundled neo4j-container-manager found');
    
    // Check for key files
    const filesToCheck = [
        'index.js',
        'container-manager.js',
        'package.json',
        'node_modules/dockerode/package.json',
        'node_modules/neo4j-driver/package.json'
    ];
    
    console.log('\nChecking key files:');
    filesToCheck.forEach(file => {
        const filePath = path.join(bundledPath, file);
        if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            console.log(`✓ ${file} (${stats.size} bytes)`);
        } else {
            console.log(`✗ ${file} - NOT FOUND`);
        }
    });
    
    // Try to load the module
    console.log('\nTrying to load neo4j-container-manager...');
    try {
        const { Neo4jContainerManager } = require(bundledPath);
        console.log('✓ Module loaded successfully');
        console.log(`  Neo4jContainerManager type: ${typeof Neo4jContainerManager}`);
        
        // Try to create an instance
        const manager = new Neo4jContainerManager({
            logger: {
                info: msg => console.log(`[INFO] ${msg}`),
                error: msg => console.log(`[ERROR] ${msg}`),
                warn: msg => console.log(`[WARN] ${msg}`),
                debug: msg => console.log(`[DEBUG] ${msg}`)
            }
        });
        console.log('✓ Manager instance created');
        
        // Try to start a container
        console.log('\nAttempting to start Neo4j container...');
        manager.start({
            environment: 'development',
            containerPrefix: 'blarify-visualizer',
            password: 'test-password-' + Date.now(),
            username: 'neo4j'
        }).then(instance => {
            console.log('✓ Container started successfully!');
            console.log(`  URI: ${instance.uri}`);
            console.log(`  Container ID: ${instance.containerId}`);
            process.exit(0);
        }).catch(error => {
            console.log('✗ Failed to start container:');
            console.log(`  Error: ${error.message}`);
            console.log(`  Stack: ${error.stack}`);
            process.exit(1);
        });
        
    } catch (error) {
        console.log('✗ Failed to load module:');
        console.log(`  Error: ${error.message}`);
        console.log(`  Stack: ${error.stack}`);
        
        // Check if it's a module resolution issue
        if (error.code === 'MODULE_NOT_FOUND') {
            console.log('\nModule resolution details:');
            console.log(`  Require paths: ${module.paths.join('\n  ')}`);
        }
    }
} else {
    console.log('✗ Bundled neo4j-container-manager NOT FOUND');
    
    // List what's actually in the bundled directory
    const bundledDir = path.join(extensionPath, 'bundled');
    if (fs.existsSync(bundledDir)) {
        console.log('\nContents of bundled directory:');
        const contents = fs.readdirSync(bundledDir);
        contents.forEach(item => {
            console.log(`  - ${item}`);
        });
    } else {
        console.log('\n✗ Bundled directory does not exist!');
    }
}

// Check Docker
exec('docker version --format "Server: {{.Server.Version}}, Client: {{.Client.Version}}"', (err, stdout) => {
    if (err) {
        console.log('\n✗ Docker check failed:', err.message);
    } else {
        console.log('\n✓ Docker is running:', stdout.trim());
    }
});