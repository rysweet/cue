#!/bin/bash

echo "Starting integration tests for MCP Blarify Server..."
echo "==========================================="

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start Neo4j if not already running
echo "Starting Neo4j container..."
docker-compose up -d

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
sleep 10

# Check Neo4j health
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:7474 > /dev/null 2>&1; then
        echo "Neo4j is ready!"
        break
    fi
    echo "Waiting for Neo4j... (attempt $((attempt+1))/$max_attempts)"
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Neo4j failed to start"
    docker-compose logs neo4j
    exit 1
fi

# Set up test data
echo "Setting up test graph data..."
python tests/setup_test_graph.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to set up test graph"
    exit 1
fi

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/test_integration.py -v

# Store test result
TEST_RESULT=$?

# Show logs if tests failed
if [ $TEST_RESULT -ne 0 ]; then
    echo "Tests failed! Showing Neo4j logs..."
    docker-compose logs --tail=50 neo4j
fi

# Cleanup (optional - comment out to keep Neo4j running)
# echo "Stopping Neo4j..."
# docker-compose down

echo "==========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "Integration tests passed!"
else
    echo "Integration tests failed!"
fi

exit $TEST_RESULT