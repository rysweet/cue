const { spawn } = require('child_process');
const path = require('path');

console.log('Testing Real Blarify Ingestion...\n');

const venvPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled/venv';
const pythonPath = path.join(venvPath, 'bin', 'python');
const blarifyPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled';
const mainPath = path.join(blarifyPath, 'blarify', 'main.py');

console.log('Testing actual workspace ingestion...');
console.log('Python:', pythonPath);
console.log('Script:', mainPath);
console.log('Working dir:', blarifyPath);

// Create a small test workspace
const fs = require('fs');
const testDir = '/tmp/blarify-ingestion-test';
if (!fs.existsSync(testDir)) {
    fs.mkdirSync(testDir, { recursive: true });
}

// Create a simple Python file to analyze
fs.writeFileSync(path.join(testDir, 'test.py'), `
def hello_world():
    """A simple test function"""
    print("Hello, World!")

class TestClass:
    """A test class"""
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
`);

const args = [
    mainPath,
    'create',
    testDir,
    '--neo4j-uri', 'bolt://localhost:7957',
    '--neo4j-user', 'neo4j',
    '--neo4j-password', 'test-password'
];

console.log('\nCommand:', pythonPath, args.join(' '));
console.log('\nStarting ingestion...\n');

const child = spawn(pythonPath, args, {
    cwd: blarifyPath,
    env: {
        ...process.env,
        PYTHONPATH: blarifyPath
    }
});

child.stdout.on('data', (data) => {
    console.log(`[STDOUT] ${data}`);
});

child.stderr.on('data', (data) => {
    console.error(`[STDERR] ${data}`);
});

child.on('close', (code) => {
    console.log(`\nIngestion process exited with code ${code}`);
    
    if (code === 0) {
        console.log('✅ Ingestion completed successfully!');
        console.log('\nTest workspace analyzed:', testDir);
        console.log('You can query Neo4j at http://localhost:7744 to see the results');
    } else {
        console.log('❌ Ingestion failed with exit code:', code);
    }
});