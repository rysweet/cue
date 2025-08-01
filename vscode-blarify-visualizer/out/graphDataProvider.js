"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GraphDataProvider = void 0;
class GraphDataProvider {
    constructor(neo4jManager, configManager) {
        this.neo4jManager = neo4jManager;
        this.configManager = configManager;
    }
    async getGraphData(options = {}) {
        const driver = await this.neo4jManager.getDriver();
        if (!driver) {
            throw new Error('Neo4j driver not connected');
        }
        const session = driver.session();
        try {
            const nodeLimit = options.nodeLimit || this.configManager.getVisualizationConfig().nodeLimit;
            // Build query based on options
            let query;
            let params = { limit: nodeLimit };
            if (options.searchQuery) {
                query = this.buildSearchQuery(options.searchQuery);
                params.searchQuery = options.searchQuery;
            }
            else if (options.startNodeId) {
                query = this.buildNeighborhoodQuery(options.depth || 2);
                params.startNodeId = options.startNodeId;
                params.depth = options.depth || 2;
            }
            else {
                query = this.buildOverviewQuery(options);
                if (options.nodeTypes) {
                    params.nodeTypes = options.nodeTypes;
                }
            }
            // Execute query
            const result = await session.run(query, params);
            // Process results
            const nodes = [];
            const edges = [];
            const nodeMap = new Map();
            const edgeSet = new Set();
            result.records.forEach((record) => {
                // Process nodes
                if (record.has('nodes')) {
                    const nodesData = record.get('nodes');
                    nodesData.forEach((nodeData) => {
                        const node = this.processNode(nodeData);
                        if (!nodeMap.has(node.id)) {
                            nodeMap.set(node.id, node);
                        }
                    });
                }
                // Process relationships
                if (record.has('relationships')) {
                    const relsData = record.get('relationships');
                    relsData.forEach((relData) => {
                        const edge = this.processEdge(relData);
                        const edgeKey = `${edge.source}-${edge.type}-${edge.target}`;
                        if (!edgeSet.has(edgeKey)) {
                            edgeSet.add(edgeKey);
                            edges.push(edge);
                        }
                    });
                }
            });
            nodes.push(...nodeMap.values());
            // Get metadata
            const metadata = await this.getGraphMetadata(session);
            return {
                nodes,
                edges,
                metadata: {
                    nodeCount: nodes.length,
                    edgeCount: edges.length,
                    nodeTypes: [...new Set(nodes.map(n => n.type))],
                    edgeTypes: [...new Set(edges.map(e => e.type))]
                }
            };
        }
        finally {
            await session.close();
        }
    }
    buildOverviewQuery(options) {
        let whereClause = '';
        if (options.nodeTypes && options.nodeTypes.length > 0) {
            whereClause = 'WHERE any(label IN labels(n) WHERE label IN $nodeTypes)';
        }
        return `
            MATCH (n:NODE) ${whereClause}
            WITH n LIMIT $limit
            OPTIONAL MATCH (n)-[r]-(m:NODE)
            WHERE id(m) IN [id(x) | x IN collect(n)]
            RETURN 
                collect(DISTINCT n) + collect(DISTINCT m) as nodes,
                collect(DISTINCT r) as relationships
        `;
    }
    buildSearchQuery(searchQuery) {
        return `
            MATCH (n:NODE)
            WHERE n.name CONTAINS $searchQuery
               OR n.path CONTAINS $searchQuery
               OR any(label IN labels(n) WHERE label CONTAINS $searchQuery)
            WITH n LIMIT $limit
            OPTIONAL MATCH (n)-[r]-(m:NODE)
            RETURN 
                collect(DISTINCT n) + collect(DISTINCT m) as nodes,
                collect(DISTINCT r) as relationships
        `;
    }
    buildNeighborhoodQuery(depth) {
        return `
            MATCH (start:NODE {node_id: $startNodeId})
            CALL apoc.path.subgraphAll(start, {
                maxLevel: $depth,
                labelFilter: '+NODE'
            })
            YIELD nodes, relationships
            RETURN nodes, relationships
        `;
    }
    processNode(nodeData) {
        const properties = nodeData.properties || {};
        const labels = nodeData.labels || [];
        // Extract main type (exclude 'NODE' label)
        const type = labels.find((l) => l !== 'NODE') || 'UNKNOWN';
        return {
            id: properties.node_id || nodeData.identity.toString(),
            label: properties.name || properties.path || type,
            type,
            properties
        };
    }
    processEdge(relData) {
        const properties = relData.properties || {};
        return {
            id: relData.identity.toString(),
            source: relData.start.toString(),
            target: relData.end.toString(),
            type: relData.type,
            properties
        };
    }
    async getGraphMetadata(session) {
        const metadataQuery = `
            MATCH (n:NODE)
            WITH labels(n) as labels
            UNWIND labels as label
            WITH label WHERE label <> 'NODE'
            RETURN label, count(*) as count
            ORDER BY count DESC
        `;
        const result = await session.run(metadataQuery);
        const nodeTypes = {};
        result.records.forEach((record) => {
            nodeTypes[record.get('label')] = record.get('count').toNumber();
        });
        return { nodeTypes };
    }
    async getNodeDetails(nodeId) {
        const driver = await this.neo4jManager.getDriver();
        if (!driver) {
            return null;
        }
        const session = driver.session();
        try {
            const result = await session.run('MATCH (n:NODE {node_id: $nodeId}) RETURN n', { nodeId });
            if (result.records.length > 0) {
                return this.processNode(result.records[0].get('n'));
            }
            return null;
        }
        finally {
            await session.close();
        }
    }
    async getNodeNeighbors(nodeId, depth = 1) {
        return this.getGraphData({
            startNodeId: nodeId,
            depth
        });
    }
}
exports.GraphDataProvider = GraphDataProvider;
//# sourceMappingURL=graphDataProvider.js.map