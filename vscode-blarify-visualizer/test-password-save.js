const vscode = require('vscode');
const path = require('path');

async function testPasswordSave() {
    console.log('Testing password save functionality...');
    
    const config = vscode.workspace.getConfiguration('blarifyVisualizer');
    const containerName = 'blarify-visualizer-development';
    const testPassword = 'test-password-' + Date.now();
    
    // Get current passwords
    const currentPasswords = config.get('neo4jPasswords', {});
    console.log('Current passwords:', currentPasswords);
    
    // Save new password
    currentPasswords[containerName] = testPassword;
    
    try {
        await config.update('neo4jPasswords', currentPasswords, vscode.ConfigurationTarget.Global);
        console.log('Password saved successfully');
        
        // Verify it was saved
        const savedPasswords = config.get('neo4jPasswords', {});
        console.log('Saved passwords:', savedPasswords);
        
        if (savedPasswords[containerName] === testPassword) {
            console.log('✓ Password persistence test PASSED');
        } else {
            console.log('✗ Password persistence test FAILED');
        }
    } catch (error) {
        console.error('Error saving password:', error);
    }
}

// Run if this is the main module
if (require.main === module) {
    testPasswordSave();
}

module.exports = { testPasswordSave };