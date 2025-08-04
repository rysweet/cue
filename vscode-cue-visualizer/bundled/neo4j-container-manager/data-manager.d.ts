import Docker from 'dockerode';
import { ImportOptions, Logger } from './types';
export declare class DataManager {
    private docker;
    private logger;
    constructor(docker: Docker, logger: Logger);
    /**
     * Export data from a container
     */
    exportData(containerId: string, exportPath: string): Promise<void>;
    /**
     * Import data into a container
     */
    importData(containerId: string, importPath: string, options?: ImportOptions): Promise<void>;
    /**
     * Get database statistics
     */
    private getDatabaseStats;
    /**
     * Run neo4j-admin command
     */
    private runNeo4jAdmin;
    /**
     * Run Cypher query
     */
    private runCypher;
    /**
     * Execute command in container
     */
    private execCommand;
    /**
     * Parse count from Cypher result
     */
    private parseCount;
    /**
     * Validate import compatibility
     */
    private validateImport;
    /**
     * Check if Neo4j versions are compatible
     */
    private areVersionsCompatible;
}
//# sourceMappingURL=data-manager.d.ts.map