import { Neo4jContainerManager } from '../src/container-manager';
import { Neo4jContainerInstance } from '../src/types';
import Docker from 'dockerode';

// Skip these tests in CI or if Docker is not available
const describeIntegration = process.env.CI ? describe.skip : describe;

describeIntegration('Neo4j Container Manager Integration', () => {
  let manager: Neo4jContainerManager;
  let testInstances: Neo4jContainerInstance[] = [];
  
  beforeAll(async () => {
    // Check if Docker is available
    try {
      const docker = new Docker();
      await docker.ping();
    } catch (error) {
      console.log('Docker not available, skipping integration tests');
      return;
    }
    
    manager = new Neo4jContainerManager({ debug: true });
  });
  
  afterAll(async () => {
    // Clean up all test containers
    for (const instance of testInstances) {
      try {
        await instance.stop();
      } catch (error) {
        // Ignore cleanup errors
      }
    }
    
    // Additional cleanup
    if (manager) {
      await manager.cleanup(0); // Clean up all test containers
    }
  });
  
  test('should start and stop a development container', async () => {
    const instance = await manager.start({
      environment: 'development',
      password: 'test-password-dev',
    });
    
    testInstances.push(instance);
    
    expect(instance.uri).toMatch(/bolt:\/\/localhost:\d+/);
    expect(instance.httpUri).toMatch(/http:\/\/localhost:\d+/);
    expect(await instance.isRunning()).toBe(true);
    
    // Test Neo4j connectivity
    const session = instance.driver!.session();
    try {
      const result = await session.run('RETURN 1 as num');
      expect(result.records[0].get('num')).toBe(1);
    } finally {
      await session.close();
    }
    
    // Stop the container
    await instance.stop();
    expect(await instance.isRunning()).toBe(false);
  }, 60000);
  
  test('should reuse existing development container', async () => {
    // Start first instance
    const instance1 = await manager.start({
      environment: 'development',
      password: 'test-password-dev',
    });
    
    testInstances.push(instance1);
    
    // Create some data
    const session1 = instance1.driver!.session();
    try {
      await session1.run('CREATE (n:TestNode {id: 1})');
    } finally {
      await session1.close();
    }
    
    // Start second instance - should reuse
    const instance2 = await manager.start({
      environment: 'development',
      password: 'test-password-dev',
    });
    
    expect(instance2.containerId).toBe(instance1.containerId);
    expect(instance2.uri).toBe(instance1.uri);
    
    // Verify data persists
    const session2 = instance2.driver!.session();
    try {
      const result = await session2.run('MATCH (n:TestNode) RETURN count(n) as count');
      expect(result.records[0].get('count').toNumber()).toBe(1);
    } finally {
      await session2.close();
    }
  }, 30000);
  
  test('should isolate test containers', async () => {
    // Start two test containers
    const test1 = await manager.start({
      environment: 'test',
      password: 'test-password-1',
    });
    
    const test2 = await manager.start({
      environment: 'test',
      password: 'test-password-2',
    });
    
    testInstances.push(test1, test2);
    
    // Containers should be different
    expect(test1.containerId).not.toBe(test2.containerId);
    expect(test1.uri).not.toBe(test2.uri);
    
    // Create data in first container
    const session1 = test1.driver!.session();
    try {
      await session1.run('CREATE (n:TestNode {container: 1})');
    } finally {
      await session1.close();
    }
    
    // Verify isolation - second container should not have the data
    const session2 = test2.driver!.session();
    try {
      const result = await session2.run('MATCH (n:TestNode) RETURN count(n) as count');
      expect(result.records[0].get('count').toNumber()).toBe(0);
    } finally {
      await session2.close();
    }
  }, 60000);
  
  test('should handle port conflicts gracefully', async () => {
    const instances: Neo4jContainerInstance[] = [];
    
    // Start multiple containers to test port allocation
    for (let i = 0; i < 3; i++) {
      const instance = await manager.start({
        environment: 'test',
        password: `test-password-${i}`,
      });
      instances.push(instance);
      testInstances.push(instance);
    }
    
    // All should have different ports
    const ports = instances.map(i => new URL(i.uri).port);
    expect(new Set(ports).size).toBe(3);
    
    // All should be running
    for (const instance of instances) {
      expect(await instance.isRunning()).toBe(true);
    }
  }, 90000);
  
  test('should export and import data', async () => {
    const instance = await manager.start({
      environment: 'test',
      password: 'test-password-export',
    });
    
    testInstances.push(instance);
    
    // Create some test data
    const session = instance.driver!.session();
    try {
      await session.run(`
        CREATE (n1:Person {name: 'Alice', age: 30})
        CREATE (n2:Person {name: 'Bob', age: 25})
        CREATE (n1)-[:KNOWS]->(n2)
      `);
    } finally {
      await session.close();
    }
    
    // Export data
    const exportPath = `/tmp/neo4j-test-export-${Date.now()}.tar.gz`;
    await instance.exportData(exportPath);
    
    // Start a new container
    const newInstance = await manager.start({
      environment: 'test',
      password: 'test-password-import',
    });
    
    testInstances.push(newInstance);
    
    // Import data
    await newInstance.importData(exportPath);
    
    // Verify data
    const newSession = newInstance.driver!.session();
    try {
      const result = await newSession.run(`
        MATCH (p:Person)
        RETURN count(p) as count
      `);
      expect(result.records[0].get('count').toNumber()).toBe(2);
      
      const relResult = await newSession.run(`
        MATCH ()-[r:KNOWS]->()
        RETURN count(r) as count
      `);
      expect(relResult.records[0].get('count').toNumber()).toBe(1);
    } finally {
      await newSession.close();
    }
    
    // Cleanup
    await require('fs').promises.unlink(exportPath);
  }, 120000);
  
  test('should get container stats', async () => {
    const instance = await manager.start({
      environment: 'test',
      password: 'test-password-stats',
    });
    
    testInstances.push(instance);
    
    // Run some queries to generate activity
    const session = instance.driver!.session();
    try {
      for (let i = 0; i < 10; i++) {
        await session.run(`CREATE (n:TestNode {id: ${i}})`);
      }
    } finally {
      await session.close();
    }
    
    // Get stats
    const stats = await instance.getStats();
    
    expect(stats.memoryUsage).toBeGreaterThan(0);
    expect(stats.memoryLimit).toBeGreaterThan(0);
    expect(stats.cpuUsage).toBeGreaterThanOrEqual(0);
  }, 30000);
});