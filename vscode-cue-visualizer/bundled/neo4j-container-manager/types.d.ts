import { Driver } from 'neo4j-driver';
export type Environment = 'development' | 'test' | 'production';
export interface Neo4jContainerConfig {
    /** Environment for the container */
    environment: Environment;
    /** Custom data directory path */
    dataPath?: string;
    /** Neo4j password (required) */
    password: string;
    /** Neo4j username (default: neo4j) */
    username?: string;
    /** Plugins to install (e.g., ['apoc', 'graph-data-science']) */
    plugins?: string[];
    /** Memory limit (e.g., '2G') */
    memory?: string;
    /** Custom container name prefix */
    containerPrefix?: string;
    /** Enable debug logging */
    debug?: boolean;
}
export interface Neo4jContainerInstance {
    /** Bolt connection URI */
    uri: string;
    /** HTTP connection URI */
    httpUri: string;
    /** Docker container ID */
    containerId: string;
    /** Docker volume name for data persistence */
    volume: string;
    /** Environment this instance is for */
    environment: Environment;
    /** Neo4j driver instance */
    driver?: Driver;
    /** Stop the container */
    stop(): Promise<void>;
    /** Check if container is running */
    isRunning(): Promise<boolean>;
    /** Export data to a file */
    exportData(path: string): Promise<void>;
    /** Import data from a file */
    importData(path: string): Promise<void>;
    /** Get container stats */
    getStats(): Promise<ContainerStats>;
}
export interface ContainerStats {
    /** Memory usage in bytes */
    memoryUsage: number;
    /** Memory limit in bytes */
    memoryLimit: number;
    /** CPU usage percentage */
    cpuUsage: number;
    /** Disk usage in bytes */
    diskUsage?: number;
    /** Network I/O */
    networkIO?: {
        rx: number;
        tx: number;
    };
}
export interface PortAllocation {
    /** Bolt protocol port */
    boltPort: number;
    /** HTTP port */
    httpPort: number;
    /** Allocated at timestamp */
    allocatedAt: number;
    /** Container ID using these ports */
    containerId?: string;
}
export interface VolumeInfo {
    /** Volume name */
    name: string;
    /** Environment */
    environment: Environment;
    /** Created timestamp */
    createdAt: number;
    /** Last used timestamp */
    lastUsed: number;
    /** Size in bytes (if available) */
    size?: number;
}
export interface ExportMetadata {
    /** Neo4j version */
    neo4jVersion: string;
    /** Export timestamp */
    exportedAt: number;
    /** Environment exported from */
    environment: Environment;
    /** Node count */
    nodeCount: number;
    /** Relationship count */
    relationshipCount: number;
    /** Database size in bytes */
    databaseSize: number;
    /** Export format version */
    formatVersion: string;
}
export interface ImportOptions {
    /** Validate data before import */
    validate?: boolean;
    /** Create backup before import */
    backup?: boolean;
    /** Force import even if versions don't match */
    force?: boolean;
}
export interface ContainerManagerOptions {
    /** Base directory for storing metadata */
    dataDir?: string;
    /** Docker socket path (default: /var/run/docker.sock) */
    dockerSocket?: string;
    /** Enable debug logging */
    debug?: boolean;
    /** Custom logger instance */
    logger?: Logger;
}
export interface Logger {
    debug(message: string, meta?: any): void;
    info(message: string, meta?: any): void;
    warn(message: string, meta?: any): void;
    error(message: string, meta?: any): void;
}
//# sourceMappingURL=types.d.ts.map