// Simple test to check if the extension is loading
const vscode = require('vscode');

async function testExtension() {
    console.log('Testing Blarify Visualizer extension...');
    
    // Check if extension is installed
    const extension = vscode.extensions.getExtension('blarify.blarify-visualizer');
    console.log('Extension found:', !!extension);
    
    if (extension) {
        console.log('Extension ID:', extension.id);
        console.log('Extension path:', extension.extensionPath);
        console.log('Is active:', extension.isActive);
        
        // Try to activate
        if (!extension.isActive) {
            console.log('Activating extension...');
            try {
                await extension.activate();
                console.log('Extension activated successfully');
            } catch (error) {
                console.error('Failed to activate:', error);
            }
        }
        
        // Check commands
        const commands = await vscode.commands.getCommands();
        const blarifyCommands = commands.filter(cmd => cmd.startsWith('blarifyVisualizer.'));
        console.log('Blarify commands found:', blarifyCommands);
    } else {
        console.log('Extension not found. Available extensions:');
        vscode.extensions.all.forEach(ext => {
            if (ext.id.includes('blarify')) {
                console.log(' -', ext.id);
            }
        });
    }
}

testExtension();