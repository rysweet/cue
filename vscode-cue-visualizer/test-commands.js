const vscode = require('vscode');

async function testCommands() {
    console.log('Testing Blarify extension commands...\n');
    
    // Wait a bit for extension to fully activate
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Get all commands
    const allCommands = await vscode.commands.getCommands();
    const blarifyCommands = allCommands.filter(cmd => cmd.includes('blarify'));
    
    console.log('Found Blarify commands:');
    blarifyCommands.forEach(cmd => console.log(`  - ${cmd}`));
    
    // Expected commands
    const expectedCommands = [
        'blarifyVisualizer.showVisualization',
        'blarifyVisualizer.ingestWorkspace',
        'blarifyVisualizer.updateGraph',
        'blarifyVisualizer.searchGraph',
        'blarifyVisualizer.restartNeo4j'
    ];
    
    console.log('\nChecking expected commands:');
    for (const cmd of expectedCommands) {
        const found = allCommands.includes(cmd);
        console.log(`  ${found ? '✓' : '✗'} ${cmd}`);
    }
    
    // Check extension output
    const outputChannel = vscode.window.createOutputChannel('Blarify Test');
    outputChannel.appendLine('Test completed. Check the Blarify Visualizer output channel for activation logs.');
    outputChannel.show();
}

// Run when VS Code is ready
if (vscode.window.activeTextEditor) {
    testCommands();
} else {
    vscode.window.onDidChangeActiveTextEditor(() => {
        testCommands();
    });
}