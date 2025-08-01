"""Neo4j container management for MCP server."""

import os
import subprocess
import json
import logging
import atexit
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class Neo4jContainerManager:
    """Python wrapper for @blarify/neo4j-container-manager."""
    
    def __init__(self, data_dir: Optional[str] = None, debug: bool = False):
        """Initialize the container manager.
        
        Args:
            data_dir: Directory for persisting Neo4j data
            debug: Enable debug logging
        """
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".blarify", "neo4j")
        self.debug = debug
        self.container_info: Optional[Dict[str, Any]] = None
        
        # Ensure neo4j-container-manager is available
        self._ensure_manager_installed()
        
        # Register cleanup on exit
        atexit.register(self._cleanup)
    
    def _ensure_manager_installed(self):
        """Ensure neo4j-container-manager is installed."""
        # Check if it's installed locally
        local_path = Path(__file__).parent.parent.parent / "neo4j-container-manager"
        if local_path.exists():
            # It's available as a sibling directory
            self.manager_path = str(local_path)
            return
        
        # Otherwise assume it's installed as an npm package
        try:
            result = subprocess.run(
                ["npm", "list", "@blarify/neo4j-container-manager", "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.manager_path = "@blarify/neo4j-container-manager"
                return
        except Exception:
            pass
        
        raise RuntimeError(
            "neo4j-container-manager not found. Please install it:\n"
            "npm install @blarify/neo4j-container-manager"
        )
    
    def start(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a Neo4j container.
        
        Args:
            config: Container configuration dict with keys:
                - environment: 'development', 'test', or 'production'
                - password: Authentication credential for Neo4j
                - username: Neo4j username (default: 'neo4j')
                - plugins: List of plugins to install (e.g., ['apoc'])
                - memory: Memory limit (e.g., '2G')
        
        Returns:
            Container information including URI and port
        """
        # Create a temporary Node.js script to interact with the manager
        script = f"""
const {{ Neo4jContainerManager }} = require('{self.manager_path}');

async function start() {{
    const manager = new Neo4jContainerManager({{
        dataDir: '{self.data_dir}',
        debug: {str(self.debug).lower()}
    }});
    
    const config = {json.dumps(config)};
    const instance = await manager.start(config);
    
    // Return simplified info
    console.log(JSON.stringify({{
        containerId: instance.containerId,
        uri: instance.uri,
        boltPort: instance.port,
        httpPort: instance.httpPort,
        httpsPort: instance.httpsPort
    }}));
}}

start().catch(err => {{
    console.error(JSON.stringify({{error: err.message}}));
    process.exit(1);
}});
"""
        
        result = self._run_node_script(script)
        if "error" in result:
            raise RuntimeError(f"Failed to start Neo4j: {result['error']}")
        
        self.container_info = result
        logger.info(f"Neo4j started at {result['uri']}")
        return result
    
    def stop(self):
        """Stop the running Neo4j container."""
        if not self.container_info:
            return
        
        script = f"""
const {{ Neo4jContainerManager }} = require('{self.manager_path}');

async function stop() {{
    const manager = new Neo4jContainerManager({{
        dataDir: '{self.data_dir}',
        debug: {str(self.debug).lower()}
    }});
    
    const instances = await manager.list();
    for (const instance of instances) {{
        if (instance.containerId === '{self.container_info['containerId']}') {{
            await instance.stop();
            console.log(JSON.stringify({{success: true}}));
            return;
        }}
    }}
    console.log(JSON.stringify({{success: false, error: 'Container not found'}}));
}}

stop().catch(err => {{
    console.error(JSON.stringify({{error: err.message}}));
    process.exit(1);
}});
"""
        
        result = self._run_node_script(script)
        if result.get("success"):
            logger.info("Neo4j container stopped")
            self.container_info = None
    
    def get_uri(self) -> Optional[str]:
        """Get the Neo4j connection URI."""
        return self.container_info["uri"] if self.container_info else None
    
    def is_running(self) -> bool:
        """Check if container is running."""
        if not self.container_info:
            return False
        
        script = f"""
const {{ Neo4jContainerManager }} = require('{self.manager_path}');

async function check() {{
    const manager = new Neo4jContainerManager({{
        dataDir: '{self.data_dir}',
        debug: {str(self.debug).lower()}
    }});
    
    const instances = await manager.list();
    for (const instance of instances) {{
        if (instance.containerId === '{self.container_info['containerId']}') {{
            const running = await instance.isRunning();
            console.log(JSON.stringify({{running}}));
            return;
        }}
    }}
    console.log(JSON.stringify({{running: false}}));
}}

check().catch(err => {{
    console.error(JSON.stringify({{error: err.message}}));
    process.exit(1);
}});
"""
        
        result = self._run_node_script(script)
        return result.get("running", False)
    
    def _run_node_script(self, script: str) -> Dict[str, Any]:
        """Run a Node.js script and return the JSON output."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ["node", temp_file],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(self.manager_path) if os.path.isdir(self.manager_path) else None
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Node script failed: {result.stderr}")
            
            return json.loads(result.stdout.strip())
        finally:
            os.unlink(temp_file)
    
    def _cleanup(self):
        """Cleanup on exit."""
        if self.container_info:
            try:
                self.stop()
            except Exception as e:
                logger.error(f"Error stopping container on exit: {e}")