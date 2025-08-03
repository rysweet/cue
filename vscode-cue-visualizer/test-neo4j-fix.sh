#!/bin/bash

echo "Testing Neo4j connection fix..."
echo "1. Opening VS Code with a workspace to trigger extension activation"
echo "2. Watch for [Neo4j Singleton] messages in the output"
echo ""

# Kill any existing VS Code instances to ensure clean start
pkill -f "Code - Insiders" || true
sleep 2

# Open VS Code with the current directory as workspace
echo "Opening VS Code..."
code-insiders . &

echo ""
echo "Monitor the output in VS Code:"
echo "1. View -> Output"
echo "2. Select 'Neo4j Manager' from dropdown"
echo "3. Look for [Neo4j Singleton] messages"
echo ""
echo "Expected behavior:"
echo "- Should see '[Neo4j Singleton] ensureNeo4jRunning called'"
echo "- Should see '[Neo4j Singleton] Creating new initialization promise' once"
echo "- May see '[Neo4j Singleton] Returning existing initialization promise' if multiple calls"
echo "- Should NOT see timeout errors after 60 seconds"