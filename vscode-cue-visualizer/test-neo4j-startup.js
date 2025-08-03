#!/usr/bin/env node

// Test script to verify Neo4j startup works correctly
const { exec } = require('child_process');
const http = require('http');

console.log('Neo4j Startup Test\n==================');

function checkContainer() {
    return new Promise((resolve) => {
        exec('docker ps | grep blarify-visualizer-development', (err, stdout) => {
            resolve(stdout.trim());
        });
    });
}

function checkNeo4j(port = 7474) {
    return new Promise((resolve) => {
        http.get(`http://localhost:${port}`, (res) => {
            resolve(res.statusCode === 200);
        }).on('error', () => {
            resolve(false);
        });
    });
}

async function waitForNeo4j(maxWait = 30000) {
    const start = Date.now();
    while (Date.now() - start < maxWait) {
        const container = await checkContainer();
        if (container) {
            console.log('✓ Container found:', container.split(/\s+/)[0]);
            
            // Extract port from container info
            const portMatch = container.match(/0\.0\.0\.0:(\d+)->7474/);
            if (portMatch) {
                const port = portMatch[1];
                console.log(`✓ HTTP port mapped to: ${port}`);
                
                if (await checkNeo4j(port)) {
                    console.log('✓ Neo4j is accessible!');
                    return true;
                }
            }
        }
        
        await new Promise(r => setTimeout(r, 1000));
        process.stdout.write('.');
    }
    return false;
}

console.log('Instructions:');
console.log('1. Open VS Code Insiders');
console.log('2. The extension should auto-start Neo4j during setup');
console.log('3. This script will monitor for the container\n');

console.log('Waiting for Neo4j container...');
waitForNeo4j().then(success => {
    if (success) {
        console.log('\n✅ Test PASSED: Neo4j started successfully!');
    } else {
        console.log('\n❌ Test FAILED: Neo4j did not start within 30 seconds');
        console.log('\nTroubleshooting:');
        console.log('- Check VS Code Output > Neo4j Manager for logs');
        console.log('- Run: docker ps -a | grep blarify');
        console.log('- Check if extension is installed and activated');
    }
    process.exit(success ? 0 : 1);
});