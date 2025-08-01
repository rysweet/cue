import Docker from 'dockerode';
import neo4j from 'neo4j-driver';
import { EventEmitter } from 'events';
import path from 'path';
import os from 'os';
import {
  Neo4jContainerConfig,
  Neo4jContainerInstance,
  Environment,
  ContainerManagerOptions,
  Logger,
  ContainerStats,
} from './types';
import { PortManager } from './port-manager';
import { VolumeManager } from './volume-manager';
import { DataManager } from './data-manager';
import { createLogger } from './logger';

const DEFAULT_NEO4J_IMAGE = 'neo4j:5-community';
const CONTAINER_PREFIX = 'blarify-neo4j';
const HEALTH_CHECK_INTERVAL = 1000; // 1 second
const HEALTH_CHECK_TIMEOUT = 60000; // 60 seconds
const SHUTDOWN_TIMEOUT = 30000; // 30 seconds

export class Neo4jContainerManager extends EventEmitter {
  private docker: Docker;
  private portManager: PortManager;
  private volumeManager: VolumeManager;
  private dataManager: DataManager;
  private logger: Logger;
  private instances: Map<string, Neo4jContainerInstance> = new Map();
  private isShuttingDown = false;

  constructor(options: ContainerManagerOptions = {}) {
    super();
    
    this.docker = new Docker({
      socketPath: options.dockerSocket || '/var/run/docker.sock',
    });
    
    const dataDir = options.dataDir || path.join(os.homedir(), '.blarify');
    this.logger = options.logger || createLogger(options.debug);
    
    this.portManager = new PortManager(dataDir, this.logger);
    this.volumeManager = new VolumeManager(this.docker, this.logger);
    this.dataManager = new DataManager(this.docker, this.logger);
    
    // Register shutdown handlers
    this.registerShutdownHandlers();
  }

  /**
   * Start a Neo4j container with the given configuration
   */
  async start(config: Neo4jContainerConfig): Promise<Neo4jContainerInstance> {
    this.logger.info('Starting Neo4j container', { environment: config.environment });
    
    try {
      // Check if we already have an instance for this environment
      const existingKey = this.getInstanceKey(config.environment, config.containerPrefix);
      if (this.instances.has(existingKey)) {
        const instance = this.instances.get(existingKey)!;
        if (await instance.isRunning()) {
          this.logger.info('Reusing existing container', { containerId: instance.containerId });
          return instance;
        }
      }
      
      // Check for existing containers
      const containerName = this.getContainerName(config.environment, config.containerPrefix);
      const existingContainer = await this.findExistingContainer(containerName);
      
      if (existingContainer) {
        const instance = await this.reuseExistingContainer(existingContainer, config);
        this.instances.set(existingKey, instance);
        return instance;
      }
      
      // Create new container
      const instance = await this.createNewContainer(config);
      this.instances.set(existingKey, instance);
      return instance;
      
    } catch (error) {
      this.logger.error('Failed to start Neo4j container', { error });
      throw error;
    }
  }

  /**
   * Stop a specific container
   */
  async stop(containerId: string): Promise<void> {
    this.logger.info('Stopping container', { containerId });
    
    try {
      const container = this.docker.getContainer(containerId);
      
      // Stop with timeout
      await container.stop({ t: SHUTDOWN_TIMEOUT / 1000 });
      
      // Release ports
      await this.portManager.releasePorts(containerId);
      
      // Remove from instances
      for (const [key, instance] of this.instances.entries()) {
        if (instance.containerId === containerId) {
          this.instances.delete(key);
          break;
        }
      }
      
      this.logger.info('Container stopped successfully', { containerId });
    } catch (error: any) {
      if (error.statusCode === 404) {
        this.logger.warn('Container not found', { containerId });
      } else if (error.statusCode === 304) {
        this.logger.info('Container already stopped', { containerId });
      } else {
        throw error;
      }
    }
  }

  /**
   * Stop all managed containers
   */
  async stopAll(): Promise<void> {
    this.logger.info('Stopping all containers');
    
    const promises: Promise<void>[] = [];
    for (const instance of this.instances.values()) {
      promises.push(this.stop(instance.containerId));
    }
    
    await Promise.all(promises);
  }

  /**
   * List all managed containers
   */
  async list(): Promise<Neo4jContainerInstance[]> {
    return Array.from(this.instances.values());
  }

  /**
   * Clean up old test containers and volumes
   */
  async cleanup(keepDays: number = 7): Promise<void> {
    this.logger.info('Cleaning up old containers and volumes', { keepDays });
    
    const cutoffTime = Date.now() - (keepDays * 24 * 60 * 60 * 1000);
    
    // Clean up containers
    const containers = await this.docker.listContainers({ all: true });
    for (const containerInfo of containers) {
      if (this.isOldTestContainer(containerInfo, cutoffTime)) {
        try {
          const container = this.docker.getContainer(containerInfo.Id);
          await container.remove({ force: true });
          this.logger.info('Removed old container', { id: containerInfo.Id });
        } catch (error) {
          this.logger.error('Failed to remove container', { id: containerInfo.Id, error });
        }
      }
    }
    
    // Clean up volumes
    await this.volumeManager.cleanup(keepDays);
  }

  /**
   * Create a new container
   */
  private async createNewContainer(config: Neo4jContainerConfig): Promise<Neo4jContainerInstance> {
    // Allocate ports
    const ports = await this.portManager.allocatePorts();
    
    // Create volume
    const volume = await this.volumeManager.createVolume(config.environment);
    
    // Container configuration
    const containerName = this.getContainerName(config.environment, config.containerPrefix);
    const username = config.username || 'neo4j';
    
    const createOptions: Docker.ContainerCreateOptions = {
      name: containerName,
      Image: DEFAULT_NEO4J_IMAGE,
      Env: [
        `NEO4J_AUTH=${username}/${config.password}`,
        'NEO4J_PLUGINS=["apoc"]',
        'NEO4J_apoc_export_file_enabled=true',
        'NEO4J_apoc_import_file_enabled=true',
        'NEO4J_apoc_import_file_use__neo4j__config=true',
        ...(config.plugins || []).map(p => `NEO4J_PLUGINS=["${p}"]`),
      ],
      HostConfig: {
        PortBindings: {
          '7474/tcp': [{ HostPort: ports.httpPort.toString() }],
          '7687/tcp': [{ HostPort: ports.boltPort.toString() }],
        },
        Mounts: [{
          Type: 'volume',
          Source: volume.name,
          Target: '/data',
        }],
        Memory: config.memory ? this.parseMemoryLimit(config.memory) : undefined,
        AutoRemove: false,
      },
      Labels: {
        'blarify.environment': config.environment,
        'blarify.created': new Date().toISOString(),
      },
    };
    
    // Create and start container
    const container = await this.docker.createContainer(createOptions);
    await container.start();
    
    // Update port allocation
    await this.portManager.updateAllocation(ports, container.id);
    
    // Wait for Neo4j to be ready
    await this.waitForNeo4j(ports.boltPort, username, config.password);
    
    // Create instance
    const instance = this.createInstance(
      container.id,
      ports,
      volume.name,
      config.environment,
      username,
      config.password
    );
    
    this.logger.info('Container created successfully', {
      containerId: container.id,
      environment: config.environment,
      ports,
    });
    
    return instance;
  }

  /**
   * Reuse an existing container
   */
  private async reuseExistingContainer(
    containerInfo: Docker.ContainerInfo,
    config: Neo4jContainerConfig
  ): Promise<Neo4jContainerInstance> {
    const container = this.docker.getContainer(containerInfo.Id);
    
    // Start if not running
    if (containerInfo.State !== 'running') {
      await container.start();
      await this.waitForContainerRunning(container);
    }
    
    // Extract ports from container info
    const ports = this.extractPorts(containerInfo);
    
    // Find volume
    const volumeName = await this.volumeManager.findVolumeForContainer(containerInfo.Id);
    
    // Wait for Neo4j
    const username = config.username || 'neo4j';
    await this.waitForNeo4j(ports.boltPort, username, config.password);
    
    // Create instance
    return this.createInstance(
      containerInfo.Id,
      ports,
      volumeName,
      config.environment,
      username,
      config.password
    );
  }

  /**
   * Create instance object
   */
  private createInstance(
    containerId: string,
    ports: { boltPort: number; httpPort: number },
    volume: string,
    environment: Environment,
    username: string,
    password: string
  ): Neo4jContainerInstance {
    const uri = `bolt://localhost:${ports.boltPort}`;
    const httpUri = `http://localhost:${ports.httpPort}`;
    
    const driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
    
    const instance: Neo4jContainerInstance = {
      uri,
      httpUri,
      containerId,
      volume,
      environment,
      driver,
      stop: async () => {
        await driver.close();
        await this.stop(containerId);
      },
      isRunning: async () => {
        try {
          const container = this.docker.getContainer(containerId);
          const info = await container.inspect();
          return info.State.Running;
        } catch {
          return false;
        }
      },
      exportData: async (path: string) => {
        await this.dataManager.exportData(containerId, path);
      },
      importData: async (path: string) => {
        await this.dataManager.importData(containerId, path);
      },
      getStats: async () => {
        return this.getContainerStats(containerId);
      },
    };
    
    return instance;
  }

  /**
   * Wait for Neo4j to be ready
   */
  private async waitForNeo4j(port: number, username: string, password: string): Promise<void> {
    const uri = `bolt://localhost:${port}`;
    const startTime = Date.now();
    
    while (Date.now() - startTime < HEALTH_CHECK_TIMEOUT) {
      try {
        const driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
        await driver.verifyConnectivity();
        await driver.close();
        return;
      } catch (error) {
        await new Promise(resolve => setTimeout(resolve, HEALTH_CHECK_INTERVAL));
      }
    }
    
    throw new Error(`Neo4j failed to start within ${HEALTH_CHECK_TIMEOUT}ms`);
  }

  /**
   * Wait for container to be running
   */
  private async waitForContainerRunning(container: Docker.Container): Promise<void> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < HEALTH_CHECK_TIMEOUT) {
      const info = await container.inspect();
      if (info.State.Running) {
        return;
      }
      await new Promise(resolve => setTimeout(resolve, HEALTH_CHECK_INTERVAL));
    }
    
    throw new Error('Container failed to start');
  }

  /**
   * Get container stats
   */
  private async getContainerStats(containerId: string): Promise<ContainerStats> {
    const container = this.docker.getContainer(containerId);
    const stats = await container.stats({ stream: false });
    
    // Calculate CPU usage
    const cpuDelta = stats.cpu_stats.cpu_usage.total_usage - stats.precpu_stats.cpu_usage.total_usage;
    const systemDelta = stats.cpu_stats.system_cpu_usage - stats.precpu_stats.system_cpu_usage;
    const cpuUsage = (cpuDelta / systemDelta) * stats.cpu_stats.online_cpus * 100;
    
    return {
      memoryUsage: stats.memory_stats.usage || 0,
      memoryLimit: stats.memory_stats.limit || 0,
      cpuUsage,
      networkIO: stats.networks ? {
        rx: Object.values(stats.networks).reduce((sum: number, net: any) => sum + net.rx_bytes, 0),
        tx: Object.values(stats.networks).reduce((sum: number, net: any) => sum + net.tx_bytes, 0),
      } : undefined,
    };
  }

  /**
   * Find existing container by name
   */
  private async findExistingContainer(name: string): Promise<Docker.ContainerInfo | null> {
    const containers = await this.docker.listContainers({ all: true });
    return containers.find(c => c.Names.some(n => n === `/${name}`)) || null;
  }

  /**
   * Extract ports from container info
   */
  private extractPorts(containerInfo: Docker.ContainerInfo): { boltPort: number; httpPort: number } {
    const ports = containerInfo.Ports || [];
    let boltPort = 7687;
    let httpPort = 7474;
    
    for (const port of ports) {
      if (port.PrivatePort === 7687 && port.PublicPort) {
        boltPort = port.PublicPort;
      } else if (port.PrivatePort === 7474 && port.PublicPort) {
        httpPort = port.PublicPort;
      }
    }
    
    return { boltPort, httpPort };
  }

  /**
   * Check if container is an old test container
   */
  private isOldTestContainer(containerInfo: Docker.ContainerInfo, cutoffTime: number): boolean {
    const isTest = containerInfo.Names.some(n => n.includes(`${CONTAINER_PREFIX}-test`));
    const created = containerInfo.Created * 1000;
    return isTest && created < cutoffTime;
  }

  /**
   * Get container name
   */
  private getContainerName(environment: Environment, prefix?: string): string {
    const basePrefix = prefix || CONTAINER_PREFIX;
    if (environment === 'test') {
      return `${basePrefix}-test-${Date.now()}`;
    }
    return `${basePrefix}-${environment}`;
  }

  /**
   * Get instance key
   */
  private getInstanceKey(environment: Environment, prefix?: string): string {
    const basePrefix = prefix || CONTAINER_PREFIX;
    return `${basePrefix}-${environment}`;
  }

  /**
   * Parse memory limit string
   */
  private parseMemoryLimit(memory: string): number {
    const match = memory.match(/^(\d+)([kmg]?)$/i);
    if (!match) {
      throw new Error(`Invalid memory limit: ${memory}`);
    }
    
    const value = parseInt(match[1], 10);
    const unit = match[2].toLowerCase();
    
    switch (unit) {
      case 'k': return value * 1024;
      case 'm': return value * 1024 * 1024;
      case 'g': return value * 1024 * 1024 * 1024;
      default: return value;
    }
  }

  /**
   * Register process shutdown handlers
   */
  private registerShutdownHandlers(): void {
    const shutdownHandler = async () => {
      if (this.isShuttingDown) return;
      this.isShuttingDown = true;
      
      this.logger.info('Shutting down Neo4j containers');
      
      try {
        await this.stopAll();
      } catch (error) {
        this.logger.error('Error during shutdown', { error });
      }
      
      process.exit(0);
    };
    
    process.on('SIGINT', shutdownHandler);
    process.on('SIGTERM', shutdownHandler);
    process.on('beforeExit', shutdownHandler);
  }
}