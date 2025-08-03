import { PortAllocation, Logger } from './types';
export declare class PortManager {
    private dataDir;
    private logger;
    private portFile;
    private allocations;
    constructor(dataDir: string, logger: Logger);
    /**
     * Allocate ports for a new container
     */
    allocatePorts(): Promise<PortAllocation>;
    /**
     * Update allocation with actual container ID
     */
    updateAllocation(allocation: PortAllocation, containerId: string): Promise<void>;
    /**
     * Release ports for a container
     */
    releasePorts(containerId: string): Promise<void>;
    /**
     * Get allocated ports for a container
     */
    getAllocation(containerId: string): PortAllocation | undefined;
    /**
     * Find an available port starting from base
     */
    private findAvailablePort;
    /**
     * Load allocations from disk
     */
    private loadAllocations;
    /**
     * Save allocations to disk
     */
    private saveAllocations;
}
//# sourceMappingURL=port-manager.d.ts.map