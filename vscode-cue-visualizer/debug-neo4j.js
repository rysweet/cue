// Debug script to check where blarify-neo4j-test is coming from
const Docker = require('dockerode');

async function checkContainers() {
    const docker = new Docker();
    
    console.log('=== Checking Docker containers ===');
    
    const containers = await docker.listContainers({ all: true });
    const blarifyContainers = containers.filter(c => 
        c.Names.some(name => name.includes('blarify'))
    );
    
    console.log(`Found ${blarifyContainers.length} blarify containers:`);
    blarifyContainers.forEach(c => {
        console.log(`\nContainer ID: ${c.Id}`);
        console.log(`Names: ${c.Names.join(', ')}`);
        console.log(`Image: ${c.Image}`);
        console.log(`State: ${c.State}`);
        console.log(`Status: ${c.Status}`);
        console.log(`Created: ${new Date(c.Created * 1000).toLocaleString()}`);
        console.log(`Command: ${c.Command}`);
        console.log(`Labels:`, c.Labels);
    });
    
    // Check environment variables
    console.log('\n=== Environment Variables ===');
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('VSCODE_PID:', process.env.VSCODE_PID);
    console.log('EXTENSION_MODE:', process.env.EXTENSION_MODE);
}

checkContainers().catch(console.error);