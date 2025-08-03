const { execSync } = require('child_process');
const path = require('path');

console.log('Testing Blarify Ingestion...\n');

// Test Python environment
const venvPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled/venv';
const pythonPath = path.join(venvPath, 'bin', 'python');
const blarifyPath = '/Users/ryan/.vscode-insiders/extensions/blarify.blarify-visualizer-0.1.0/bundled';

console.log('1. Checking Python environment...');
try {
    const version = execSync(`${pythonPath} --version`, { encoding: 'utf8' });
    console.log(`   ✅ Python found: ${version.trim()}`);
} catch (error) {
    console.error('   ❌ Python not found:', error.message);
    process.exit(1);
}

console.log('\n2. Checking Blarify installation...');
try {
    const blarifyCheck = execSync(`${pythonPath} -c "import blarify; print(blarify.__file__)"`, {
        encoding: 'utf8',
        cwd: blarifyPath
    });
    console.log(`   ✅ Blarify module found: ${blarifyCheck.trim()}`);
} catch (error) {
    console.error('   ❌ Blarify import failed:', error.message);
    process.exit(1);
}

console.log('\n3. Testing Blarify CLI...');
try {
    const helpOutput = execSync(`${pythonPath} -m blarify --help`, {
        encoding: 'utf8',
        cwd: blarifyPath
    });
    console.log('   ✅ Blarify CLI is accessible');
    console.log('   Available commands:', helpOutput.split('\n').find(line => line.includes('Commands:')));
} catch (error) {
    console.error('   ❌ Blarify CLI failed:', error.message);
}

console.log('\n4. Testing workspace analysis (dry run)...');
const testWorkspace = '/tmp/blarify-test-workspace-50844';
try {
    // Just check if the command would work, don't actually run full analysis
    const testCmd = `${pythonPath} -m blarify create ${testWorkspace} --neo4j-uri bolt://localhost:7957 --neo4j-user neo4j --neo4j-password test-password --dry-run 2>&1 || true`;
    console.log(`   Command: ${testCmd}`);
    
    const output = execSync(testCmd, {
        encoding: 'utf8',
        cwd: blarifyPath,
        env: {
            ...process.env,
            PYTHONPATH: blarifyPath
        }
    });
    
    if (output.includes('error') || output.includes('Error')) {
        console.log('   ⚠️  Command returned errors:', output.substring(0, 200));
    } else {
        console.log('   ✅ Blarify command structure is valid');
    }
} catch (error) {
    console.error('   ❌ Analysis command failed:', error.message);
}

console.log('\n5. Checking Neo4j connectivity...');
try {
    const curlCheck = execSync('curl -s -o /dev/null -w "%{http_code}" http://localhost:7744', { encoding: 'utf8' });
    if (curlCheck.trim() === '200') {
        console.log('   ✅ Neo4j is accessible on port 7744');
    } else {
        console.log('   ❌ Neo4j returned status:', curlCheck);
    }
} catch (error) {
    console.error('   ❌ Neo4j connection failed:', error.message);
}

console.log('\n✅ Ingestion test complete!');