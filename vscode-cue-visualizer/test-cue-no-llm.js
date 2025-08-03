const { spawn } = require('child_process');
const path = require('path');

console.log('Testing Blarify WITHOUT LLM features...\n');

const venvPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled/venv';
const pythonPath = path.join(venvPath, 'bin', 'python');
const blarifyPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled';
const mainPath = path.join(blarifyPath, 'blarify', 'main.py');

// Test directory
const testDir = '/tmp/blarify-ingestion-test';

console.log('Testing with environment variables:');
console.log(`ROOT_PATH=${testDir}`);
console.log('NEO4J_URI=bolt://localhost:7957');
console.log('NEO4J_USER=neo4j');
console.log('NEO4J_PASSWORD=test-password');
console.log('ENABLE_LLM_DESCRIPTIONS=false\n');

// Run main.py directly with environment variables
const args = [mainPath];

console.log('Command:', pythonPath, args.join(' '));
console.log('Working directory:', testDir);
console.log('\nStarting ingestion...\n');

const child = spawn(pythonPath, args, {
    cwd: testDir,
    env: {
        ...process.env,
        PYTHONPATH: blarifyPath,
        ROOT_PATH: testDir,
        NEO4J_URI: 'bolt://localhost:7957',
        NEO4J_USER: 'neo4j',
        NEO4J_PASSWORD: 'test-password',
        ENABLE_LLM_DESCRIPTIONS: 'false'
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
    // Only show non-INFO messages for cleaner output
    const lines = data.toString().split('\n');
    lines.forEach(line => {
        if (line.trim() && !line.includes('INFO:')) {
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
        console.log('4. Or run: MATCH (n) RETURN labels(n), count(*) AS count');
    } else {
        console.log('❌ Ingestion failed');
        if (errorOutput.includes('AuthError')) {
            console.log('\n⚠️  Authentication error - checking container...');
            const { execSync } = require('child_process');
            try {
                const logs = execSync('docker logs blarify-visualizer-development --tail 5', { encoding: 'utf8' });
                console.log('Recent Neo4j logs:', logs);
            } catch (e) {}
        }
    }
});