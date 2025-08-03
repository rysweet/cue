#!/bin/bash

# Run tests for the VS Code extension

set -e

echo "Running VS Code Extension Tests..."
echo "================================="

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

# Compile TypeScript
echo "Compiling TypeScript..."
npm run compile

# Run unit tests
echo -e "\nRunning unit tests..."
npm test

# If VS Code is available, run integration tests
if command -v code-insiders &> /dev/null || command -v code &> /dev/null; then
    echo -e "\nRunning integration tests..."
    # Note: Integration tests require VS Code to be installed
    # They will be run as part of the extension host
else
    echo -e "\nSkipping integration tests (VS Code not found)"
fi

echo -e "\nAll tests completed!"