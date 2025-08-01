// Debug script to run in VS Code Developer Console
// Open VS Code Developer Tools: Cmd+Shift+P > Developer: Toggle Developer Tools
// Run this script in the Console tab

(async () => {
    console.log('=== Blarify Extension Debug ===');
    
    // Check if extension is present
    const ext = vscode.extensions.getExtension('blarify.blarify-visualizer');
    console.log('Extension found:', !!ext);
    
    if (ext) {
        console.log('Extension path:', ext.extensionPath);
        console.log('Extension kind:', ext.extensionKind);
        console.log('Is active:', ext.isActive);
        
        // Check if main module exists
        try {
            const mainPath = require.resolve(ext.extensionPath + '/out/extension.js');
            console.log('Main module found at:', mainPath);
        } catch (e) {
            console.error('Main module not found:', e.message);
        }
        
        // Try to activate if not active
        if (!ext.isActive) {
            try {
                console.log('Attempting to activate...');
                const api = await ext.activate();
                console.log('Activation result:', api);
            } catch (e) {
                console.error('Activation failed:', e);
                console.error('Stack:', e.stack);
            }
        }
        
        // Check exports
        if (ext.isActive && ext.exports) {
            console.log('Extension exports:', Object.keys(ext.exports));
        }
    }
    
    // List all commands
    const allCommands = await vscode.commands.getCommands();
    const blarifyCommands = allCommands.filter(cmd => cmd.includes('blarify'));
    console.log('Blarify commands:', blarifyCommands);
    
    // Check for errors in extension host log
    console.log('Check the Extension Host log for errors: View > Output > Extension Host');
})();