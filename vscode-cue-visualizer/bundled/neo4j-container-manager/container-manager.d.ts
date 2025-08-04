import { EventEmitter } from 'events';
import { Neo4jContainerConfig, Neo4jContainerInstance, ContainerManagerOptions } from './types';
export declare class Neo4jContainerManager extends EventEmitter {
    private docker;
    private portManager;
    private volumeManager;
    private dataManager;
    private logger;
    private instances;
    private isShuttingDown;
    constructor(options?: ContainerManagerOptions);
    /**
     * Start a Neo4j container with the given configuration
     */
    start(config: Neo4jContainerConfig): Promise<Neo4jContainerInstance>;
    /**
     * Stop a specific container
     */
    stop(containerId: string): Promise<void>;
    /**
     * Stop all managed containers
     */
    stopAll(): Promise<void>;
    /**
     * List all managed containers
     */
    list(): Promise<Neo4jContainerInstance[]>;
    /**
     * Clean up old test containers and volumes
     */
    cleanup(keepDays?: number): Promise<void>;
    /**
     * Create a new container
     */
    private createNewContainer;
    /**
     * Reuse an existing container
     */
    private reuseExistingContainer;
    /**
     * Create instance object
     */
    private createInstance;
    /**
     * Wait for Neo4j to be ready
     */
    private waitForNeo4j;
    /**
     * Wait for container to be running
     */
    private waitForContainerRunning;
    /**
     * Get container stats
     */
    private getContainerStats;
    /**
     * Find existing container by name
     */
    private findExistingContainer;
    /**
     * Extract ports from container info
     */
    private extractPorts;
    /**
     * Check if container is an old test container
     */
    private isOldTestContainer;
    /**
     * Get container name
     */
    private getContainerName;
    /**
     * Get instance key
     */
    private getInstanceKey;
    /**
     * Parse memory limit string
     */
    private parseMemoryLimit;
    /**
     * Register process shutdown handlers
     */
    private registerShutdownHandlers;
}
//# sourceMappingURL=container-manager.d.ts.map