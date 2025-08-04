"""MCP Server for Blarify Neo4j Graph."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
from neo4j import GraphDatabase
from pydantic import BaseModel, Field

from src.config import Config
from src.tools.context_tools import ContextTools
from src.tools.planning_tools import PlanningTools
from src.neo4j_container import Neo4jContainerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GetContextForFilesArgs(BaseModel):
    """Arguments for getContextForFiles tool."""
    file_paths: List[str] = Field(
        description="List of file paths to get context for"
    )


class GetContextForSymbolArgs(BaseModel):
    """Arguments for getContextForSymbol tool."""
    symbol_name: str = Field(
        description="Name of the symbol (class, function, variable) to find"
    )
    symbol_type: Optional[str] = Field(
        default=None,
        description="Optional type hint: 'class', 'function', 'method', etc."
    )


class BuildPlanForChangeArgs(BaseModel):
    """Arguments for buildPlanForChange tool."""
    change_request: str = Field(
        description="Description of the change to be implemented"
    )


class BlarifyMCPServer:
    """MCP Server for Blarify graph queries."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("mcp-cue")
        self.driver = None
        self.context_tools = None
        self.planning_tools = None
        self.container_manager = None
        self.container_info = None
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="getContextForFiles",
                    description="Retrieve comprehensive context for specified files including classes, functions, dependencies, and documentation",
                    inputSchema=GetContextForFilesArgs.model_json_schema()
                ),
                Tool(
                    name="getContextForSymbol",
                    description="Get detailed context for a specific symbol (class, function, variable) including definition, usage, and relationships",
                    inputSchema=GetContextForSymbolArgs.model_json_schema()
                ),
                Tool(
                    name="buildPlanForChange",
                    description="Analyze the codebase and create a detailed implementation plan for a change request",
                    inputSchema=BuildPlanForChangeArgs.model_json_schema()
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                # Ensure connection is established
                if not self.driver:
                    await self._connect_to_neo4j()
                
                if name == "getContextForFiles":
                    args = GetContextForFilesArgs(**arguments)
                    result = await self.context_tools.get_context_for_files(args.file_paths)
                    
                elif name == "getContextForSymbol":
                    args = GetContextForSymbolArgs(**arguments)
                    result = await self.context_tools.get_context_for_symbol(
                        args.symbol_name,
                        args.symbol_type
                    )
                    
                elif name == "buildPlanForChange":
                    args = BuildPlanForChangeArgs(**arguments)
                    result = await self.planning_tools.build_plan_for_change(args.change_request)
                    
                else:
                    result = f"Unknown tool: {name}"
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                error_msg = f"Error executing {name}: {str(e)}"
                return [TextContent(type="text", text=error_msg)]
    
    async def _connect_to_neo4j(self):
        """Establish connection to Neo4j."""
        try:
            # Check if we should manage the container
            if Config.MANAGE_NEO4J_CONTAINER:
                logger.info("Starting managed Neo4j container")
                self.container_manager = Neo4jContainerManager(
                    data_dir=Config.NEO4J_DATA_DIR,
                    debug=Config.DEBUG
                )
                
                # Start container
                self.container_info = self.container_manager.start({
                    "environment": Config.ENVIRONMENT,
                    "password": Config.NEO4J_PASSWORD,
                    "username": Config.NEO4J_USERNAME,
                    "plugins": ["apoc"],
                    "memory": "2G"
                })
                
                # Use the dynamically allocated URI
                neo4j_uri = self.container_info["uri"]
            else:
                # Use configured URI
                neo4j_uri = Config.NEO4J_URI
            
            logger.info(f"Connecting to Neo4j at {neo4j_uri}")
            self.driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD)
            )
            
            # Verify connection
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
            
            # Initialize tools
            self.context_tools = ContextTools(self.driver)
            self.planning_tools = PlanningTools(self.driver)
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def run(self):
        """Run the MCP server."""
        try:
            # Connect to Neo4j
            await self._connect_to_neo4j()
            
            # Run the server
            async with self.server.run(
                transport="stdio",
                initialization_options=InitializationOptions(
                    server_name="Blarify MCP Server",
                    server_version="0.1.0"
                )
            ) as running_server:
                logger.info("Blarify MCP Server started")
                await running_server.wait_closed()
                
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            # Cleanup
            if self.driver:
                self.driver.close()
                logger.info("Closed Neo4j connection")
            
            # Stop container if managed
            if self.container_manager and Config.MANAGE_NEO4J_CONTAINER:
                try:
                    self.container_manager.stop()
                    logger.info("Stopped managed Neo4j container")
                except Exception as e:
                    logger.error(f"Error stopping container: {e}")


async def main():
    """Main entry point."""
    server = BlarifyMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())