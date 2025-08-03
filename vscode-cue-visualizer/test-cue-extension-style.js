const { spawn } = require('child_process');
const path = require('path');

console.log('Testing Blarify the way VS Code extension would call it...\n');

const venvPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled/venv';
const pythonPath = path.join(venvPath, 'bin', 'python');
const blarifyPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled';
const mainPath = path.join(blarifyPath, 'blarify', 'main.py');

// Test directory
const testDir = '/tmp/blarify-ingestion-test';

console.log('Testing with environment variables (how Blarify expects them):');
console.log(`ROOT_PATH=${testDir}`);
console.log('NEO4J_URI=bolt://localhost:7957');
console.log('NEO4J_USER=neo4j');
console.log('NEO4J_PASSWORD=test-password\n');

// Run main.py directly with environment variables
const args = [mainPath];

console.log('Command:', pythonPath, args.join(' '));
console.log('Working directory:', testDir);
console.log('\nStarting ingestion...\n');

const child = spawn(pythonPath, args, {
    cwd: testDir,  // Run from the workspace directory
    env: {
        ...process.env,
        PYTHONPATH: blarifyPath,
        ROOT_PATH: testDir,
        NEO4J_URI: 'bolt://localhost:7957',
        NEO4J_USER: 'neo4j',
        NEO4J_PASSWORD: 'test-password'
    }
});

let output = '';
let errorOutput = '';

child.stdout.on('data', (data) => {
    output += data.toString();
    const lines = data.toString().split('\n');
    lines.forEach(line => {
        if (line.trim()) {
            console.log(`[STDOUT] ${line}`);
        }
    });
});

child.stderr.on('data', (data) => {
    errorOutput += data.toString();
    const lines = data.toString().split('\n');
    lines.forEach(line => {
        if (line.trim()) {
            console.error(`[STDERR] ${line}`);
        }
    });
});

child.on('close', (code) => {
    console.log(`\nIngestion process exited with code ${code}`);
    
    if (code === 0) {
        console.log('✅ Ingestion completed successfully!');
        console.log('\nYou can now:');
        console.log('1. Open Neo4j Browser at http://localhost:7744');
        console.log('2. Login with username: neo4j, password: test-password');
        console.log('3. Run: MATCH (n) RETURN n LIMIT 25');
    } else {
        console.log('❌ Ingestion failed');
        if (errorOutput.includes('neo4j.exceptions.AuthError')) {
            console.log('\n⚠️  Authentication error - the password may be incorrect');
            console.log('Try restarting the Neo4j container with a fresh password');
        }
    }
});