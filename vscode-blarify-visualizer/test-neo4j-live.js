#!/usr/bin/env node

// Quick test to verify Neo4j is accessible after extension starts it
const http = require('http');

console.log('Waiting 5 seconds for Neo4j to start...');

setTimeout(() => {
    // Check if Neo4j HTTP interface is accessible
    http.get('http://localhost:7474', (res) => {
        console.log(`Neo4j HTTP Status: ${res.statusCode}`);
        if (res.statusCode === 200) {
            console.log('✅ Neo4j is running and accessible!');
            
            // Check Docker container
            const { exec } = require('child_process');
            exec('docker ps | grep blarify-visualizer-development', (err, stdout) => {
                if (stdout) {
                    console.log('✅ Docker container found:');
                    console.log(stdout);
                } else {
                    console.log('❌ No Docker container found');
                }
            });
        }
    }).on('error', (err) => {
        console.log('❌ Neo4j is not accessible:', err.message);
        console.log('Make sure VS Code extension has started Neo4j');
    });
}, 5000);