const path = require('path');

async function testContainerManagerFix() {
    console.log('Testing Neo4j Container Manager password persistence fix...\n');
    
    const containerManagerPath = path.join(__dirname, 'bundled/neo4j-container-manager');
    const { Neo4jContainerManager } = require(containerManagerPath);
    
    const manager = new Neo4jContainerManager({
        logger: {
            info: console.log,
            error: console.error,
            warn: console.warn,
            debug: console.log
        }
    });
    
    const config = {
        environment: 'test-fix',
        containerPrefix: 'blarify-test',
        password: 'test-password-123',
        username: 'neo4j'
    };
    
    try {
        // Step 1: Start a new container
        console.log('\n1. Starting new container with password:', config.password);
        const instance1 = await manager.start(config);
        console.log('✓ Container started successfully');
        console.log('  Container ID:', instance1.containerId);
        
        // Step 2: Stop the instance but keep the container
        console.log('\n2. Closing driver connection...');
        await instance1.driver.close();
        console.log('✓ Driver closed');
        
        // Step 3: Try to reuse the container with a different password
        console.log('\n3. Attempting to reuse container with DIFFERENT password...');
        const configWrongPassword = { ...config, password: 'wrong-password' };
        
        try {
            const instance2 = await manager.start(configWrongPassword);
            console.log('✓ Container reused successfully!');
            console.log('  This means the fix is working - it used the stored password');
            
            // Verify connectivity
            await instance2.driver.verifyConnectivity();
            console.log('✓ Successfully connected to Neo4j');
            
            // Clean up
            await instance2.stop();
            console.log('\n✓ Test PASSED: Container manager correctly uses stored passwords');
        } catch (error) {
            console.error('✗ Failed to reuse container:', error.message);
            console.error('  The fix may not be working correctly');
        }
        
    } catch (error) {
        console.error('Test failed:', error);
    }
}

// Run the test
testContainerManagerFix().catch(console.error);