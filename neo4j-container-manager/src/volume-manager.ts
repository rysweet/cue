import Docker from 'dockerode';
import { Environment, VolumeInfo, Logger } from './types';

const VOLUME_PREFIX = 'blarify-neo4j';
const VOLUME_LABEL_KEY = 'com.blarify.neo4j';

export class VolumeManager {
  constructor(
    private docker: Docker,
    private logger: Logger
  ) {}
  
  /**
   * Create a volume for the given environment
   */
  async createVolume(environment: Environment): Promise<VolumeInfo> {
    const volumeName = this.getVolumeName(environment);
    
    try {
      // Check if volume already exists
      const existingVolume = await this.findVolume(volumeName);
      if (existingVolume) {
        this.logger.info('Reusing existing volume', { volumeName });
        return this.getVolumeInfo(existingVolume);
      }
      
      // Create new volume
      await this.docker.createVolume({
        Name: volumeName,
        Labels: {
          [VOLUME_LABEL_KEY]: 'true',
          [`${VOLUME_LABEL_KEY}.environment`]: environment,
          [`${VOLUME_LABEL_KEY}.created`]: new Date().toISOString(),
        },
      });
      
      this.logger.info('Created volume', { volumeName });
      
      return {
        name: volumeName,
        environment,
        createdAt: Date.now(),
        lastUsed: Date.now(),
      };
      
    } catch (error) {
      this.logger.error('Failed to create volume', { volumeName, error });
      throw error;
    }
  }
  
  /**
   * Find volume for a container
   */
  async findVolumeForContainer(containerId: string): Promise<string> {
    try {
      const container = this.docker.getContainer(containerId);
      const info = await container.inspect();
      
      // Look for our volume in mounts
      const mount = info.Mounts?.find(m => 
        m.Type === 'volume' && 
        m.Name?.startsWith(VOLUME_PREFIX)
      );
      
      if (mount) {
        return mount.Name!;
      }
      
      // Fallback: try to find by container labels
      const environment = info.Config?.Labels?.['blarify.environment'] as Environment;
      if (environment) {
        const volumeName = this.getVolumeName(environment);
        const volume = await this.findVolume(volumeName);
        if (volume) {
          return volumeName;
        }
      }
      
      throw new Error('No volume found for container');
      
    } catch (error) {
      this.logger.error('Failed to find volume for container', { containerId, error });
      throw error;
    }
  }
  
  /**
   * List all managed volumes
   */
  async listVolumes(): Promise<VolumeInfo[]> {
    try {
      const { Volumes } = await this.docker.listVolumes({
        filters: JSON.stringify({
          label: [VOLUME_LABEL_KEY],
        }),
      });
      
      return Volumes.map(v => this.getVolumeInfo(v));
      
    } catch (error) {
      this.logger.error('Failed to list volumes', { error });
      throw error;
    }
  }
  
  /**
   * Clean up old volumes
   */
  async cleanup(keepDays: number = 7): Promise<void> {
    const cutoffTime = Date.now() - (keepDays * 24 * 60 * 60 * 1000);
    
    try {
      const volumes = await this.listVolumes();
      
      for (const volumeInfo of volumes) {
        // Only clean up test volumes older than cutoff
        if (volumeInfo.environment === 'test' && volumeInfo.lastUsed < cutoffTime) {
          try {
            const volume = this.docker.getVolume(volumeInfo.name);
            await volume.remove();
            this.logger.info('Removed old volume', { name: volumeInfo.name });
          } catch (error: any) {
            if (error.statusCode === 409) {
              this.logger.warn('Volume in use, skipping', { name: volumeInfo.name });
            } else {
              this.logger.error('Failed to remove volume', { name: volumeInfo.name, error });
            }
          }
        }
      }
      
    } catch (error) {
      this.logger.error('Failed to cleanup volumes', { error });
      throw error;
    }
  }
  
  /**
   * Get volume size
   */
  async getVolumeSize(volumeName: string): Promise<number | undefined> {
    try {
      const volume = this.docker.getVolume(volumeName);
      const info = await volume.inspect();
      
      // Size might not be available on all Docker versions
      return info.UsageData?.Size;
      
    } catch (error) {
      this.logger.warn('Failed to get volume size', { volumeName, error });
      return undefined;
    }
  }
  
  /**
   * Find volume by name
   */
  private async findVolume(name: string): Promise<Docker.VolumeInspectInfo | null> {
    try {
      const volume = this.docker.getVolume(name);
      return await volume.inspect();
    } catch (error: any) {
      if (error.statusCode === 404) {
        return null;
      }
      throw error;
    }
  }
  
  /**
   * Get volume name for environment
   */
  private getVolumeName(environment: Environment): string {
    if (environment === 'test') {
      // Test volumes get unique names
      return `${VOLUME_PREFIX}-test-${Date.now()}`;
    }
    return `${VOLUME_PREFIX}-${environment}-data`;
  }
  
  /**
   * Convert Docker volume to VolumeInfo
   */
  private getVolumeInfo(volume: Docker.VolumeInspectInfo): VolumeInfo {
    const labels = volume.Labels || {};
    const environment = (labels[`${VOLUME_LABEL_KEY}.environment`] || 'development') as Environment;
    const created = labels[`${VOLUME_LABEL_KEY}.created`];
    
    return {
      name: volume.Name,
      environment,
      createdAt: created ? new Date(created).getTime() : Date.now(),
      lastUsed: Date.now(), // Would need to track this separately
      size: volume.UsageData?.Size,
    };
  }
}