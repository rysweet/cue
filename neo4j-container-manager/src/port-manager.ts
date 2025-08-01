import { promises as fs } from 'fs';
import path from 'path';
import * as portfinder from 'portfinder';
import { PortAllocation, Logger } from './types';

const PORT_FILE = 'ports.json';
const BASE_BOLT_PORT = 7687;
const BASE_HTTP_PORT = 7474;
const PORT_INCREMENT = 10;

export class PortManager {
  private portFile: string;
  private allocations: Map<string, PortAllocation> = new Map();
  
  constructor(
    private dataDir: string,
    private logger: Logger
  ) {
    this.portFile = path.join(dataDir, PORT_FILE);
    this.loadAllocations();
  }
  
  /**
   * Allocate ports for a new container
   */
  async allocatePorts(): Promise<PortAllocation> {
    await this.loadAllocations();
    
    // Find available ports
    const boltPort = await this.findAvailablePort(BASE_BOLT_PORT);
    const httpPort = await this.findAvailablePort(BASE_HTTP_PORT);
    
    const allocation: PortAllocation = {
      boltPort,
      httpPort,
      allocatedAt: Date.now(),
    };
    
    // Generate temporary ID
    const tempId = `temp-${Date.now()}`;
    this.allocations.set(tempId, allocation);
    await this.saveAllocations();
    
    this.logger.info('Allocated ports', { boltPort, httpPort });
    
    return allocation;
  }
  
  /**
   * Update allocation with actual container ID
   */
  async updateAllocation(allocation: PortAllocation, containerId: string): Promise<void> {
    // Find and remove temp allocation
    let tempKey: string | null = null;
    for (const [key, alloc] of this.allocations.entries()) {
      if (alloc.boltPort === allocation.boltPort && key.startsWith('temp-')) {
        tempKey = key;
        break;
      }
    }
    
    if (tempKey) {
      this.allocations.delete(tempKey);
    }
    
    // Add with real container ID
    allocation.containerId = containerId;
    this.allocations.set(containerId, allocation);
    await this.saveAllocations();
  }
  
  /**
   * Release ports for a container
   */
  async releasePorts(containerId: string): Promise<void> {
    this.allocations.delete(containerId);
    await this.saveAllocations();
    this.logger.info('Released ports for container', { containerId });
  }
  
  /**
   * Get allocated ports for a container
   */
  getAllocation(containerId: string): PortAllocation | undefined {
    return this.allocations.get(containerId);
  }
  
  /**
   * Find an available port starting from base
   */
  private async findAvailablePort(basePort: number): Promise<number> {
    const allocatedPorts = new Set<number>();
    
    // Collect all allocated ports
    for (const allocation of this.allocations.values()) {
      allocatedPorts.add(allocation.boltPort);
      allocatedPorts.add(allocation.httpPort);
    }
    
    // Find available port
    let port = basePort;
    while (allocatedPorts.has(port)) {
      port += PORT_INCREMENT;
    }
    
    // Verify with portfinder
    const availablePort = await portfinder.getPortPromise({ port });
    
    return availablePort;
  }
  
  /**
   * Load allocations from disk
   */
  private async loadAllocations(): Promise<void> {
    try {
      await fs.mkdir(this.dataDir, { recursive: true });
      const data = await fs.readFile(this.portFile, 'utf-8');
      const allocations = JSON.parse(data);
      
      this.allocations.clear();
      for (const [key, value] of Object.entries(allocations)) {
        this.allocations.set(key, value as PortAllocation);
      }
      
      // Clean up old temp allocations (older than 1 hour)
      const oneHourAgo = Date.now() - (60 * 60 * 1000);
      const toDelete: string[] = [];
      
      for (const [key, allocation] of this.allocations.entries()) {
        if (key.startsWith('temp-') && allocation.allocatedAt < oneHourAgo) {
          toDelete.push(key);
        }
      }
      
      if (toDelete.length > 0) {
        toDelete.forEach(key => this.allocations.delete(key));
        await this.saveAllocations();
      }
      
    } catch (error: any) {
      if (error.code !== 'ENOENT') {
        this.logger.error('Failed to load port allocations', { error });
      }
      // Start with empty allocations
      this.allocations.clear();
    }
  }
  
  /**
   * Save allocations to disk
   */
  private async saveAllocations(): Promise<void> {
    try {
      await fs.mkdir(this.dataDir, { recursive: true });
      
      const data: Record<string, PortAllocation> = {};
      for (const [key, value] of this.allocations.entries()) {
        data[key] = value;
      }
      
      await fs.writeFile(
        this.portFile,
        JSON.stringify(data, null, 2),
        'utf-8'
      );
    } catch (error) {
      this.logger.error('Failed to save port allocations', { error });
      throw error;
    }
  }
}