import Docker from 'dockerode';
import { Environment, VolumeInfo, Logger } from './types';
export declare class VolumeManager {
    private docker;
    private logger;
    constructor(docker: Docker, logger: Logger);
    /**
     * Create a volume for the given environment
     */
    createVolume(environment: Environment): Promise<VolumeInfo>;
    /**
     * Find volume for a container
     */
    findVolumeForContainer(containerId: string): Promise<string>;
    /**
     * List all managed volumes
     */
    listVolumes(): Promise<VolumeInfo[]>;
    /**
     * Clean up old volumes
     */
    cleanup(keepDays?: number): Promise<void>;
    /**
     * Get volume size
     */
    getVolumeSize(volumeName: string): Promise<number | undefined>;
    /**
     * Find volume by name
     */
    private findVolume;
    /**
     * Get volume name for environment
     */
    private getVolumeName;
    /**
     * Convert Docker volume to VolumeInfo
     */
    private getVolumeInfo;
}
//# sourceMappingURL=volume-manager.d.ts.map