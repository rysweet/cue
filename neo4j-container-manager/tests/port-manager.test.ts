import { PortManager } from '../src/port-manager';
import { promises as fs } from 'fs';
import * as portfinder from 'portfinder';

jest.mock('fs', () => ({
  promises: {
    mkdir: jest.fn(),
    readFile: jest.fn(),
    writeFile: jest.fn(),
  },
}));

jest.mock('portfinder');

describe('PortManager', () => {
  let portManager: PortManager;
  const testDataDir = '/tmp/test-blarify';
  const mockLogger = {
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    portManager = new PortManager(testDataDir, mockLogger);
  });
  
  describe('allocatePorts', () => {
    it('should allocate available ports', async () => {
      // Mock file system - no existing allocations
      (fs.readFile as jest.Mock).mockRejectedValue({ code: 'ENOENT' });
      (fs.mkdir as jest.Mock).mockResolvedValue(undefined);
      (fs.writeFile as jest.Mock).mockResolvedValue(undefined);
      
      // Mock portfinder
      const mockGetPort = portfinder.getPortPromise as jest.Mock;
      mockGetPort
        .mockResolvedValueOnce(7687) // bolt port
        .mockResolvedValueOnce(7474); // http port
      
      const allocation = await portManager.allocatePorts();
      
      expect(allocation).toEqual({
        boltPort: 7687,
        httpPort: 7474,
        allocatedAt: expect.any(Number),
      });
      
      expect(fs.writeFile).toHaveBeenCalled();
    });
    
    it('should find next available port if base is taken', async () => {
      // Mock existing allocations
      const existingAllocations = {
        'container-1': {
          boltPort: 7687,
          httpPort: 7474,
          allocatedAt: Date.now(),
        },
      };
      
      (fs.readFile as jest.Mock).mockResolvedValue(
        JSON.stringify(existingAllocations)
      );
      (fs.writeFile as jest.Mock).mockResolvedValue(undefined);
      
      // Mock portfinder to return incremented ports
      const mockGetPort = portfinder.getPortPromise as jest.Mock;
      mockGetPort
        .mockResolvedValueOnce(7697) // next bolt port
        .mockResolvedValueOnce(7484); // next http port
      
      const allocation = await portManager.allocatePorts();
      
      expect(allocation.boltPort).toBe(7697);
      expect(allocation.httpPort).toBe(7484);
    });
  });
  
  describe('updateAllocation', () => {
    it('should update temp allocation with container ID', async () => {
      (fs.readFile as jest.Mock).mockResolvedValue('{}');
      (fs.writeFile as jest.Mock).mockResolvedValue(undefined);
      
      // First allocate ports
      const mockGetPort = portfinder.getPortPromise as jest.Mock;
      mockGetPort.mockResolvedValue(7687);
      
      const allocation = await portManager.allocatePorts();
      
      // Update with container ID
      await portManager.updateAllocation(allocation, 'real-container-id');
      
      // Check that writeFile was called with updated data
      const lastCall = (fs.writeFile as jest.Mock).mock.calls.slice(-1)[0];
      const savedData = JSON.parse(lastCall[1]);
      
      expect(savedData['real-container-id']).toBeDefined();
      expect(savedData['real-container-id'].containerId).toBe('real-container-id');
      
      // Temp allocation should be removed
      const tempKeys = Object.keys(savedData).filter(k => k.startsWith('temp-'));
      expect(tempKeys).toHaveLength(0);
    });
  });
  
  describe('releasePorts', () => {
    it('should remove allocation for container', async () => {
      const allocations = {
        'container-1': {
          boltPort: 7687,
          httpPort: 7474,
          allocatedAt: Date.now(),
          containerId: 'container-1',
        },
      };
      
      (fs.readFile as jest.Mock).mockResolvedValue(
        JSON.stringify(allocations)
      );
      (fs.writeFile as jest.Mock).mockResolvedValue(undefined);
      
      await portManager.releasePorts('container-1');
      
      const lastCall = (fs.writeFile as jest.Mock).mock.calls.slice(-1)[0];
      const savedData = JSON.parse(lastCall[1]);
      
      expect(savedData['container-1']).toBeUndefined();
    });
  });
  
  describe('cleanup old temp allocations', () => {
    it('should remove temp allocations older than 1 hour', async () => {
      const twoHoursAgo = Date.now() - (2 * 60 * 60 * 1000);
      const tenMinutesAgo = Date.now() - (10 * 60 * 1000);
      
      const allocations = {
        'temp-old': {
          boltPort: 7687,
          httpPort: 7474,
          allocatedAt: twoHoursAgo,
        },
        'temp-recent': {
          boltPort: 7697,
          httpPort: 7484,
          allocatedAt: tenMinutesAgo,
        },
        'real-container': {
          boltPort: 7707,
          httpPort: 7494,
          allocatedAt: twoHoursAgo,
          containerId: 'real-container',
        },
      };
      
      (fs.readFile as jest.Mock).mockResolvedValue(
        JSON.stringify(allocations)
      );
      (fs.writeFile as jest.Mock).mockResolvedValue(undefined);
      
      // Trigger cleanup by loading allocations
      await (portManager as any).loadAllocations();
      
      const lastCall = (fs.writeFile as jest.Mock).mock.calls[0];
      const savedData = JSON.parse(lastCall[1]);
      
      expect(savedData['temp-old']).toBeUndefined();
      expect(savedData['temp-recent']).toBeDefined();
      expect(savedData['real-container']).toBeDefined();
    });
  });
});