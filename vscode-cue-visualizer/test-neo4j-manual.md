# Testing Neo4j Startup Manually

1. Open VS Code Insiders
2. Open the Output panel (View > Output)
3. Select "Neo4j Manager" from the dropdown
4. Open Command Palette (Cmd+Shift+P)
5. Run "Blarify Visualizer: Restart Neo4j"
6. Watch the output for any errors

## Expected Behavior
- Neo4j should start successfully
- If there's an existing container with wrong password, it should handle it gracefully
- Password should be saved to workspace settings

## Debugging
- Check Docker containers: `docker ps -a | grep blarify`
- Check container logs: `docker logs blarify-visualizer-development`
- Clear stored passwords in VS Code settings if needed