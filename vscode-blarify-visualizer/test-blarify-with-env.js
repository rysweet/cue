const { spawn } = require('child_process');
const path = require('path');

console.log('Testing Blarify with proper environment variables...\n');

const venvPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled/venv';
const pythonPath = path.join(venvPath, 'bin', 'python');
const blarifyPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled';
const mainPath = path.join(blarifyPath, 'blarify', 'main.py');

// Test directory
const testDir = '/tmp/blarify-ingestion-test';

console.log('Testing with environment variables:');
console.log('NEO4J_URI=bolt://localhost:7957');
console.log('NEO4J_USER=neo4j');
console.log('NEO4J_PASSWORD=test-password\n');

// Try the ingest command like the extension uses
const args = [mainPath, 'ingest', testDir, '--json'];

console.log('Command:', pythonPath, args.join(' '));
console.log('\nStarting ingestion...\n');

const child = spawn(pythonPath, args, {
    cwd: blarifyPath,
    env: {
        ...process.env,
        PYTHONPATH: blarifyPath,
        NEO4J_URI: 'bolt://localhost:7957',
        NEO4J_USER: 'neo4j',
        NEO4J_PASSWORD: 'test-password'
    }
});

let output = '';
let errorOutput = '';

child.stdout.on('data', (data) => {
    output += data.toString();
    console.log(`[STDOUT] ${data}`);
});

child.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.error(`[STDERR] ${data}`);
});

child.on('close', (code) => {
    console.log(`\nIngestion process exited with code ${code}`);
    
    if (code === 0) {
        console.log('✅ Ingestion completed successfully!');
        
        // Try to parse JSON output
        try {
            const lines = output.split('\n');
            const jsonLine = lines.find(line => line.trim().startsWith('{'));
            if (jsonLine) {
                const result = JSON.parse(jsonLine);
                console.log('\nResult summary:');
                console.log(`- Nodes: ${result.nodes ? result.nodes.length : 0}`);
                console.log(`- Edges: ${result.edges ? result.edges.length : 0}`);
            }
        } catch (parseError) {
            console.log('Could not parse JSON output');
        }
    } else {
        console.log('❌ Ingestion failed');
        console.log('Error output:', errorOutput);
    }
});