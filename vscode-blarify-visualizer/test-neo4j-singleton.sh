#!/bin/bash

echo "Neo4j Singleton Fix Test"
echo "========================"
echo ""
echo "This test verifies the singleton pattern prevents concurrent Neo4j initialization"
echo ""

# Clean up first
echo "1. Cleaning up existing containers..."
./cleanup-neo4j.sh
echo ""

# Create test workspace
TEST_DIR="/tmp/blarify-singleton-test-$$"
mkdir -p "$TEST_DIR"
echo "// Test file" > "$TEST_DIR/test.js"

echo "2. Starting VS Code with clean environment..."
echo "   Watch the Neo4j Manager output for:"
echo "   - [Neo4j Singleton] messages"
echo "   - Only ONE 'Creating new initialization promise'"
echo "   - NO timeout errors after 60 seconds"
echo ""
echo "3. Opening VS Code..."

# Open VS Code
code-insiders --new-window "$TEST_DIR"

echo ""
echo "IMPORTANT: In VS Code:"
echo "1. Open Output panel (View > Output)"
echo "2. Select 'Neo4j Manager' from dropdown"
echo "3. Look for [Neo4j Singleton] messages"
echo "4. Verify no timeout errors occur"
echo ""
echo "You can also trigger the ingestion command to see if subsequent calls reuse the promise:"
echo "Command Palette > Blarify: Analyze Workspace"