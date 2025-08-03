# Testing Neo4j Password Persistence

## First Launch
1. Reload VS Code Insiders (Cmd+R)
2. Open the Output panel and select "Blarify Visualizer"
3. You should see:
   - "Creating new Neo4j instance..."
   - "Generated password for Neo4j"
   - "Saved Neo4j password to workspace settings"
   - "Neo4j started successfully"

4. Check `.vscode/settings.json` - you should see something like:
   ```json
   {
     "blarifyVisualizer.neo4j.blarify-neo4j-vscode-development.password": "generated-password-here"
   }
   ```

## Test Persistence
1. Once Neo4j starts successfully, run the ingest workspace command
2. Let it analyze and store some data
3. Reload VS Code again (Cmd+R)
4. In the output, you should now see:
   - "Found existing Neo4j instance"
   - "Found stored password, attempting to connect..."
   - "Successfully connected to existing Neo4j instance"
5. The data should still be there - no re-ingestion needed!

## Error Scenarios
- If there's an existing container with wrong password, you'll see a dialog offering to recreate
- If you choose "Cancel", the extension won't start Neo4j
- If you choose "Recreate Database", it will stop the old container and create a new one

## Notes
- Passwords are stored per workspace in `.vscode/settings.json`
- Each container name gets its own password
- The extension now properly reuses existing containers between restarts