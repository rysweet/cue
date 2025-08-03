#!/bin/bash

# Test script to launch VS Code Insiders in a new window and monitor Neo4j startup

echo "VS Code Extension Test - New Window"
echo "==================================="
echo ""

# Create a temporary workspace directory for testing
TEST_DIR="/tmp/blarify-test-workspace-$$"
mkdir -p "$TEST_DIR"
echo "Created test workspace: $TEST_DIR"

# Create a simple file so VS Code has something to open
echo "Test workspace for Blarify extension" > "$TEST_DIR/README.md"

# Function to monitor Docker containers
monitor_containers() {
    echo ""
    echo "Monitoring for Neo4j container..."
    local count=0
    while [ $count -lt 60 ]; do
        container=$(docker ps --filter name=blarify-visualizer-development --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | tail -n +2)
        if [ ! -z "$container" ]; then
            echo "✅ Neo4j container detected:"
            echo "$container"
            
            # Check if Neo4j is accessible
            port=$(docker ps --filter name=blarify-visualizer-development --format "{{.Ports}}" | grep -oE '0\.0\.0\.0:([0-9]+)->7474' | cut -d: -f2 | cut -d- -f1)
            if [ ! -z "$port" ]; then
                echo "Testing Neo4j on port $port..."
                if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" | grep -q "200"; then
                    echo "✅ Neo4j is accessible!"
                    return 0
                fi
            fi
        fi
        
        sleep 1
        count=$((count + 1))
        printf "."
    done
    echo ""
    echo "❌ Timeout: No Neo4j container started after 60 seconds"
    return 1
}

# Function to check VS Code logs
check_logs() {
    echo ""
    echo "Checking VS Code logs..."
    # VS Code logs are typically in ~/Library/Application Support/Code - Insiders/logs
    LOG_DIR="$HOME/Library/Application Support/Code - Insiders/logs"
    if [ -d "$LOG_DIR" ]; then
        echo "Log directory: $LOG_DIR"
        # Find the most recent renderer log
        LATEST_LOG=$(find "$LOG_DIR" -name "renderer*.log" -type f -exec ls -t {} + | head -1)
        if [ -f "$LATEST_LOG" ]; then
            echo "Latest log: $LATEST_LOG"
            echo "Last 50 lines containing 'blarify' or 'neo4j':"
            tail -n 1000 "$LATEST_LOG" | grep -i -E "(blarify|neo4j)" | tail -50
        fi
    fi
}

# Start monitoring in background
monitor_containers &
MONITOR_PID=$!

# Launch VS Code Insiders with the test workspace
echo ""
echo "Launching VS Code Insiders..."
echo "Command: code-insiders --new-window --verbose \"$TEST_DIR\""
echo ""

# Start VS Code with verbose logging
code-insiders --new-window --verbose "$TEST_DIR" 2>&1 | tee /tmp/vscode-launch-$$.log &
VSCODE_PID=$!

# Give VS Code time to start
sleep 5

echo ""
echo "VS Code launched. Waiting for extension to activate..."
echo "Check the Output panel > 'Neo4j Manager' for detailed logs"
echo ""

# Wait for monitoring to complete
wait $MONITOR_PID
MONITOR_RESULT=$?

# Check results
if [ $MONITOR_RESULT -eq 0 ]; then
    echo ""
    echo "✅ Test PASSED: Neo4j started successfully!"
    
    # Show container details
    echo ""
    echo "Container details:"
    docker ps --filter name=blarify-visualizer-development
else
    echo ""
    echo "❌ Test FAILED: Neo4j did not start"
    
    # Check logs
    check_logs
    
    # Check for any error messages in launch log
    echo ""
    echo "VS Code launch log errors:"
    grep -i -E "(error|fail|exception)" /tmp/vscode-launch-$$.log | tail -20
fi

# Cleanup
echo ""
echo "Test complete. Test workspace: $TEST_DIR"
echo "You can close the VS Code window when done."
echo ""
echo "To clean up: rm -rf $TEST_DIR"