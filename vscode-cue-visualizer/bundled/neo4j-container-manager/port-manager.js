"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PortManager = void 0;
const fs_1 = require("fs");
const path_1 = __importDefault(require("path"));
const portfinder = __importStar(require("portfinder"));
const PORT_FILE = 'ports.json';
const BASE_BOLT_PORT = 7687;
const BASE_HTTP_PORT = 7474;
const PORT_INCREMENT = 10;
class PortManager {
    constructor(dataDir, logger) {
        this.dataDir = dataDir;
        this.logger = logger;
        this.allocations = new Map();
        this.portFile = path_1.default.join(dataDir, PORT_FILE);
        this.loadAllocations();
    }
    /**
     * Allocate ports for a new container
     */
    async allocatePorts() {
        await this.loadAllocations();
        // Find available ports
        const boltPort = await this.findAvailablePort(BASE_BOLT_PORT);
        const httpPort = await this.findAvailablePort(BASE_HTTP_PORT);
        const allocation = {
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
    async updateAllocation(allocation, containerId) {
        // Find and remove temp allocation
        let tempKey = null;
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
    async releasePorts(containerId) {
        this.allocations.delete(containerId);
        await this.saveAllocations();
        this.logger.info('Released ports for container', { containerId });
    }
    /**
     * Get allocated ports for a container
     */
    getAllocation(containerId) {
        return this.allocations.get(containerId);
    }
    /**
     * Find an available port starting from base
     */
    async findAvailablePort(basePort) {
        const allocatedPorts = new Set();
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
    async loadAllocations() {
        try {
            await fs_1.promises.mkdir(this.dataDir, { recursive: true });
            const data = await fs_1.promises.readFile(this.portFile, 'utf-8');
            const allocations = JSON.parse(data);
            this.allocations.clear();
            for (const [key, value] of Object.entries(allocations)) {
                this.allocations.set(key, value);
            }
            // Clean up old temp allocations (older than 1 hour)
            const oneHourAgo = Date.now() - (60 * 60 * 1000);
            const toDelete = [];
            for (const [key, allocation] of this.allocations.entries()) {
                if (key.startsWith('temp-') && allocation.allocatedAt < oneHourAgo) {
                    toDelete.push(key);
                }
            }
            if (toDelete.length > 0) {
                toDelete.forEach(key => this.allocations.delete(key));
                await this.saveAllocations();
            }
        }
        catch (error) {
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
    async saveAllocations() {
        try {
            await fs_1.promises.mkdir(this.dataDir, { recursive: true });
            const data = {};
            for (const [key, value] of this.allocations.entries()) {
                data[key] = value;
            }
            await fs_1.promises.writeFile(this.portFile, JSON.stringify(data, null, 2), 'utf-8');
        }
        catch (error) {
            this.logger.error('Failed to save port allocations', { error });
            throw error;
        }
    }
}
exports.PortManager = PortManager;
//# sourceMappingURL=port-manager.js.map