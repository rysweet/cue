import Docker from 'dockerode';
import { promises as fs } from 'fs';
import path from 'path';
import tar from 'tar';
import { pipeline } from 'stream/promises';
import { createReadStream, createWriteStream } from 'fs';
import { ExportMetadata, ImportOptions, Logger, Environment } from './types';

const EXPORT_FORMAT_VERSION = '1.0.0';

export class DataManager {
  constructor(
    private docker: Docker,
    private logger: Logger
  ) {}
  
  /**
   * Export data from a container
   */
  async exportData(containerId: string, exportPath: string): Promise<void> {
    this.logger.info('Exporting data', { containerId, exportPath });
    
    try {
      const container = this.docker.getContainer(containerId);
      const info = await container.inspect();
      
      // Ensure container is running
      if (!info.State.Running) {
        throw new Error('Container must be running to export data');
      }
      
      // Create export directory
      const exportDir = path.dirname(exportPath);
      await fs.mkdir(exportDir, { recursive: true });
      
      // Get database stats
      const stats = await this.getDatabaseStats(container);
      
      // Create metadata
      const metadata: ExportMetadata = {
        neo4jVersion: info.Config.Image || 'unknown',
        exportedAt: Date.now(),
        environment: (info.Config.Labels?.['blarify.environment'] || 'development') as Environment,
        nodeCount: stats.nodeCount,
        relationshipCount: stats.relationshipCount,
        databaseSize: stats.databaseSize,
        formatVersion: EXPORT_FORMAT_VERSION,
      };
      
      // Create temp directory for export
      const tempDir = path.join(exportDir, `.export-${Date.now()}`);
      await fs.mkdir(tempDir, { recursive: true });
      
      try {
        // Write metadata
        await fs.writeFile(
          path.join(tempDir, 'metadata.json'),
          JSON.stringify(metadata, null, 2)
        );
        
        // Export Neo4j data using neo4j-admin
        await this.runNeo4jAdmin(container, [
          'database',
          'dump',
          'neo4j',
          '--to-path=/export',
        ]);
        
        // Copy exported data from container
        const stream = await container.getArchive({ path: '/export' });
        const extractPath = path.join(tempDir, 'data.tar');
        await pipeline(
          stream,
          createWriteStream(extractPath)
        );
        
        // Extract the tar file
        await tar.extract({
          file: extractPath,
          cwd: tempDir,
        });
        
        // Remove the intermediate tar
        await fs.unlink(extractPath);
        
        // Create final archive
        await tar.create(
          {
            gzip: true,
            file: exportPath,
            cwd: tempDir,
          },
          ['.']
        );
        
        this.logger.info('Export completed', { exportPath, metadata });
        
      } finally {
        // Cleanup temp directory
        await fs.rm(tempDir, { recursive: true, force: true });
      }
      
    } catch (error) {
      this.logger.error('Export failed', { containerId, exportPath, error });
      throw error;
    }
  }
  
  /**
   * Import data into a container
   */
  async importData(
    containerId: string,
    importPath: string,
    options: ImportOptions = {}
  ): Promise<void> {
    this.logger.info('Importing data', { containerId, importPath, options });
    
    try {
      const container = this.docker.getContainer(containerId);
      const info = await container.inspect();
      
      // Ensure container is running
      if (!info.State.Running) {
        throw new Error('Container must be running to import data');
      }
      
      // Verify import file exists
      await fs.access(importPath);
      
      // Create temp directory for import
      const tempDir = path.join(path.dirname(importPath), `.import-${Date.now()}`);
      await fs.mkdir(tempDir, { recursive: true });
      
      try {
        // Extract archive
        await tar.extract({
          file: importPath,
          cwd: tempDir,
        });
        
        // Read metadata
        const metadataPath = path.join(tempDir, 'metadata.json');
        const metadataContent = await fs.readFile(metadataPath, 'utf-8');
        const metadata: ExportMetadata = JSON.parse(metadataContent);
        
        // Validate if requested
        if (options.validate && !options.force) {
          await this.validateImport(info, metadata);
        }
        
        // Create backup if requested
        if (options.backup) {
          const backupPath = importPath.replace(/\.tar\.gz$/, '-backup.tar.gz');
          await this.exportData(containerId, backupPath);
        }
        
        // Stop Neo4j database
        await this.runCypher(container, 'STOP DATABASE neo4j');
        
        // Wait for database to stop
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Clear existing data
        const rmExec = await container.exec({
          Cmd: ['rm', '-rf', '/data/databases/neo4j'],
          AttachStdout: true,
          AttachStderr: true,
        });
        await rmExec.start({});
        
        // Copy import data to container
        const exportDir = path.join(tempDir, 'export');
        const files = await fs.readdir(exportDir);
        const dumpFile = files.find(f => f.endsWith('.dump'));
        
        if (!dumpFile) {
          throw new Error('No dump file found in export');
        }
        
        // Create tar of dump file
        const dumpTarPath = path.join(tempDir, 'dump.tar');
        await tar.create(
          {
            file: dumpTarPath,
            cwd: exportDir,
          },
          [dumpFile]
        );
        
        // Copy to container
        await container.putArchive(
          createReadStream(dumpTarPath),
          { path: '/import' }
        );
        
        // Import using neo4j-admin
        await this.runNeo4jAdmin(container, [
          'database',
          'load',
          'neo4j',
          '--from-path=/import',
          `--from-file=${dumpFile}`,
          '--overwrite-destination=true',
        ]);
        
        // Start database
        await this.runCypher(container, 'START DATABASE neo4j');
        
        this.logger.info('Import completed', { metadata });
        
      } finally {
        // Cleanup temp directory
        await fs.rm(tempDir, { recursive: true, force: true });
      }
      
    } catch (error) {
      this.logger.error('Import failed', { containerId, importPath, error });
      throw error;
    }
  }
  
  /**
   * Get database statistics
   */
  private async getDatabaseStats(container: Docker.Container): Promise<{
    nodeCount: number;
    relationshipCount: number;
    databaseSize: number;
  }> {
    try {
      // Get counts using Cypher
      const nodeCountResult = await this.runCypher(
        container,
        'MATCH (n) RETURN count(n) as count'
      );
      const relCountResult = await this.runCypher(
        container,
        'MATCH ()-[r]->() RETURN count(r) as count'
      );
      
      // Parse results (this is simplified - real implementation would parse properly)
      const nodeCount = this.parseCount(nodeCountResult);
      const relationshipCount = this.parseCount(relCountResult);
      
      // Get database size from file system
      const sizeResult = await this.execCommand(container, [
        'du', '-sb', '/data/databases/neo4j'
      ]);
      const databaseSize = parseInt(sizeResult.split('\t')[0], 10) || 0;
      
      return {
        nodeCount,
        relationshipCount,
        databaseSize,
      };
      
    } catch (error) {
      this.logger.warn('Failed to get database stats', { error });
      return {
        nodeCount: 0,
        relationshipCount: 0,
        databaseSize: 0,
      };
    }
  }
  
  /**
   * Run neo4j-admin command
   */
  private async runNeo4jAdmin(
    container: Docker.Container,
    args: string[]
  ): Promise<void> {
    const exec = await container.exec({
      Cmd: ['neo4j-admin', ...args],
      AttachStdout: true,
      AttachStderr: true,
    });
    
    const stream = await exec.start({});
    
    return new Promise((resolve, reject) => {
      let output = '';
      let error = '';
      
      stream.on('data', (chunk: Buffer) => {
        const data = chunk.toString();
        if (chunk[0] === 1) {
          output += data.slice(8); // stdout
        } else if (chunk[0] === 2) {
          error += data.slice(8); // stderr
        }
      });
      
      stream.on('end', async () => {
        const inspectResult = await exec.inspect();
        if (inspectResult.ExitCode !== 0) {
          reject(new Error(`neo4j-admin failed: ${error}`));
        } else {
          resolve();
        }
      });
    });
  }
  
  /**
   * Run Cypher query
   */
  private async runCypher(
    container: Docker.Container,
    query: string
  ): Promise<string> {
    return this.execCommand(container, [
      'cypher-shell',
      '-u', 'neo4j',
      '-p', 'neo4j', // This should come from config
      query,
    ]);
  }
  
  /**
   * Execute command in container
   */
  private async execCommand(
    container: Docker.Container,
    cmd: string[]
  ): Promise<string> {
    const exec = await container.exec({
      Cmd: cmd,
      AttachStdout: true,
      AttachStderr: true,
    });
    
    const stream = await exec.start({});
    
    return new Promise((resolve, reject) => {
      let output = '';
      let error = '';
      
      stream.on('data', (chunk: Buffer) => {
        const data = chunk.toString();
        if (chunk[0] === 1) {
          output += data.slice(8); // stdout
        } else if (chunk[0] === 2) {
          error += data.slice(8); // stderr
        }
      });
      
      stream.on('end', async () => {
        const inspectResult = await exec.inspect();
        if (inspectResult.ExitCode !== 0) {
          reject(new Error(`Command failed: ${error}`));
        } else {
          resolve(output);
        }
      });
    });
  }
  
  /**
   * Parse count from Cypher result
   */
  private parseCount(result: string): number {
    const match = result.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }
  
  /**
   * Validate import compatibility
   */
  private async validateImport(
    containerInfo: Docker.ContainerInspectInfo,
    metadata: ExportMetadata
  ): Promise<void> {
    // Check Neo4j version compatibility
    const containerVersion = containerInfo.Config.Image || '';
    const exportVersion = metadata.neo4jVersion;
    
    if (!this.areVersionsCompatible(containerVersion, exportVersion)) {
      throw new Error(
        `Version mismatch: container ${containerVersion} vs export ${exportVersion}`
      );
    }
    
    // Check format version
    if (metadata.formatVersion !== EXPORT_FORMAT_VERSION) {
      throw new Error(
        `Format version mismatch: expected ${EXPORT_FORMAT_VERSION}, got ${metadata.formatVersion}`
      );
    }
  }
  
  /**
   * Check if Neo4j versions are compatible
   */
  private areVersionsCompatible(version1: string, version2: string): boolean {
    // Extract major versions
    const major1 = version1.match(/neo4j:(\d+)/)?.[1];
    const major2 = version2.match(/neo4j:(\d+)/)?.[1];
    
    // Major versions must match
    return major1 === major2;
  }
}