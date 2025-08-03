#!/bin/bash
# cleanup-neo4j.sh
echo "Cleaning up Neo4j containers and volumes..."

# Stop and remove containers
docker ps -a --filter name=blarify-visualizer --format "{{.ID}}" | \
    xargs -r docker rm -f 2>/dev/null || true

# Remove volumes
docker volume ls --filter name=blarify --format "{{.Name}}" | \
    xargs -r docker volume rm 2>/dev/null || true

echo "Cleanup complete"