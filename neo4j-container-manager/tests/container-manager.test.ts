import { Neo4jContainerManager } from '../src/container-manager';
import { Neo4jContainerConfig } from '../src/types';
import Docker from 'dockerode';

// Mock dependencies
jest.mock('dockerode');
jest.mock('../src/port-manager');
jest.mock('../src/volume-manager');
jest.mock('../src/data-manager');

describe('Neo4jContainerManager', () => {
  let manager: Neo4jContainerManager;
  let mockDocker: jest.Mocked<Docker>;
  
  beforeEach(() => {
    jest.clearAllMocks();
    manager = new Neo4jContainerManager({ debug: false });
    mockDocker = (manager as any).docker;
  });
  
  describe('start', () => {
    const config: Neo4jContainerConfig = {
      environment: 'test',
      password: 'test-password',
    };
    
    it('should reuse existing running container', async () => {
      // Mock existing container
      const mockContainer = {
        id: 'existing-container',
        start: jest.fn(),
        inspect: jest.fn().mockResolvedValue({
          State: { Running: true },
        }),
      };
      
      mockDocker.listContainers = jest.fn().mockResolvedValue([
        {
          Id: 'existing-container',
          Names: ['/blarify-neo4j-test'],
          State: 'running',
          Ports: [
            { PrivatePort: 7687, PublicPort: 7687 },
            { PrivatePort: 7474, PublicPort: 7474 },
          ],
        },
      ]);
      
      mockDocker.getContainer = jest.fn().mockReturnValue(mockContainer);
      
      // Mock volume manager
      const mockVolumeManager = (manager as any).volumeManager;
      mockVolumeManager.findVolumeForContainer = jest.fn().mockResolvedValue('test-volume');
      
      // Mock Neo4j connectivity (this would need proper mocking in real tests)
      const neo4jDriver = require('neo4j-driver');
      neo4jDriver.driver = jest.fn().mockReturnValue({
        verifyConnectivity: jest.fn().mockResolvedValue(true),
        close: jest.fn(),
      });
      
      const instance = await manager.start(config);
      
      expect(instance).toBeDefined();
      expect(instance.uri).toBe('bolt://localhost:7687');
      expect(mockContainer.start).not.toHaveBeenCalled();
    });
    
    it('should create new container if none exists', async () => {
      mockDocker.listContainers = jest.fn().mockResolvedValue([]);
      
      const mockContainer = {
        id: 'new-container',
        start: jest.fn(),
      };
      
      mockDocker.createContainer = jest.fn().mockResolvedValue(mockContainer);
      mockDocker.getContainer = jest.fn().mockReturnValue({
        inspect: jest.fn().mockResolvedValue({
          State: { Running: true },
        }),
      });
      
      // Mock port manager
      const mockPortManager = (manager as any).portManager;
      mockPortManager.allocatePorts = jest.fn().mockResolvedValue({
        boltPort: 7697,
        httpPort: 7484,
      });
      mockPortManager.updateAllocation = jest.fn();
      
      // Mock volume manager
      const mockVolumeManager = (manager as any).volumeManager;
      mockVolumeManager.createVolume = jest.fn().mockResolvedValue({
        name: 'test-volume',
      });
      
      // Mock Neo4j connectivity
      const neo4jDriver = require('neo4j-driver');
      neo4jDriver.driver = jest.fn().mockReturnValue({
        verifyConnectivity: jest.fn().mockResolvedValue(true),
        close: jest.fn(),
      });
      
      const instance = await manager.start(config);
      
      expect(mockDocker.createContainer).toHaveBeenCalled();
      expect(mockContainer.start).toHaveBeenCalled();
      expect(instance.uri).toBe('bolt://localhost:7697');
    });
    
    it('should throw error if password not provided', async () => {
      const invalidConfig: Neo4jContainerConfig = {
        environment: 'test',
        password: '',
      };
      
      await expect(manager.start(invalidConfig)).rejects.toThrow();
    });
  });
  
  describe('stop', () => {
    it('should stop running container', async () => {
      const mockContainer = {
        stop: jest.fn(),
      };
      
      mockDocker.getContainer = jest.fn().mockReturnValue(mockContainer);
      
      // Mock port manager
      const mockPortManager = (manager as any).portManager;
      mockPortManager.releasePorts = jest.fn();
      
      await manager.stop('test-container');
      
      expect(mockContainer.stop).toHaveBeenCalledWith({ t: 30 });
      expect(mockPortManager.releasePorts).toHaveBeenCalledWith('test-container');
    });
    
    it('should handle container not found', async () => {
      mockDocker.getContainer = jest.fn().mockReturnValue({
        stop: jest.fn().mockRejectedValue({ statusCode: 404 }),
      });
      
      // Should not throw
      await expect(manager.stop('non-existent')).resolves.not.toThrow();
    });
  });
  
  describe('cleanup', () => {
    it('should remove old test containers', async () => {
      const oldContainer = {
        Id: 'old-test-container',
        Names: ['/blarify-neo4j-test-123'],
        Created: Math.floor((Date.now() - 10 * 24 * 60 * 60 * 1000) / 1000), // 10 days ago
      };
      
      mockDocker.listContainers = jest.fn().mockResolvedValue([oldContainer]);
      
      const mockContainer = {
        remove: jest.fn(),
      };
      
      mockDocker.getContainer = jest.fn().mockReturnValue(mockContainer);
      
      // Mock volume manager
      const mockVolumeManager = (manager as any).volumeManager;
      mockVolumeManager.cleanup = jest.fn();
      
      await manager.cleanup(7);
      
      expect(mockContainer.remove).toHaveBeenCalledWith({ force: true });
      expect(mockVolumeManager.cleanup).toHaveBeenCalledWith(7);
    });
    
    it('should not remove recent containers', async () => {
      const recentContainer = {
        Id: 'recent-test-container',
        Names: ['/blarify-neo4j-test-456'],
        Created: Math.floor((Date.now() - 1 * 24 * 60 * 60 * 1000) / 1000), // 1 day ago
      };
      
      mockDocker.listContainers = jest.fn().mockResolvedValue([recentContainer]);
      mockDocker.getContainer = jest.fn();
      
      await manager.cleanup(7);
      
      expect(mockDocker.getContainer).not.toHaveBeenCalled();
    });
  });
});