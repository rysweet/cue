"""Integration tests for MCP server with real Neo4j."""

import pytest
import pytest_asyncio
import asyncio
import os
from neo4j import GraphDatabase
import subprocess
import time

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import BlarifyMCPServer
from src.tools.context_tools import ContextTools
from src.tools.planning_tools import PlanningTools


class TestIntegration:
    """Integration tests with real Neo4j database."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        # Check if Neo4j is running
        try:
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "testpassword")
            )
            driver.verify_connectivity()
            driver.close()
            print("Neo4j is already running")
        except Exception:
            print("Starting Neo4j with docker-compose...")
            subprocess.run(["docker-compose", "up", "-d"], 
                         cwd=os.path.dirname(os.path.dirname(__file__)))
            time.sleep(10)  # Wait for Neo4j to start
        
        # Set up test graph
        print("Setting up test graph...")
        subprocess.run([sys.executable, "tests/setup_test_graph.py"],
                      cwd=os.path.dirname(os.path.dirname(__file__)))
    
    @pytest_asyncio.fixture
    def neo4j_driver(self):
        """Create Neo4j driver."""
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        yield driver
        driver.close()
    
    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create MCP server instance."""
        os.environ.update({
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "testpassword",
            "NEO4J_DATABASE": "neo4j"
        })
        
        server = BlarifyMCPServer()
        await server._connect_to_neo4j()
        yield server
        if server.driver:
            server.driver.close()
    
    @pytest.mark.asyncio
    async def test_get_context_for_files_real(self, mcp_server):
        """Test getting context for real files in the graph."""
        result = await mcp_server.context_tools.get_context_for_files([
            "user_service.py",
            "auth_service.py"
        ])
        
        assert "Context for Files" in result
        assert "user_service.py" in result
        assert "UserService" in result
        assert "create_user" in result
        assert "auth_service.py" in result
        assert "AuthService" in result
        
        # Check for relationships
        assert "Imports" in result or "Dependencies" in result
        assert "user.py" in result  # UserService imports User model
    
    @pytest.mark.asyncio
    async def test_get_context_for_symbol_real(self, mcp_server):
        """Test getting context for a real symbol in the graph."""
        result = await mcp_server.context_tools.get_context_for_symbol(
            "UserService",
            "class"
        )
        
        assert "UserService" in result
        assert "CLASS" in result
        assert "/src/services/user_service.py" in result
        
        # Check for methods
        assert "create_user" in result
        assert "get_user" in result
        assert "update_user" in result
        
        # Check for inheritance
        assert "BaseService" in result
        
        # Check for usage
        assert "UserController" in result or "AuthService" in result
    
    @pytest.mark.asyncio
    async def test_build_plan_for_change_real(self, mcp_server):
        """Test building a change plan with real graph data."""
        result = await mcp_server.planning_tools.build_plan_for_change(
            "Add email verification to the UserService"
        )
        
        assert "Implementation Plan" in result
        assert "UserService" in result
        
        # Should identify affected files
        assert "user_service.py" in result
        
        # Should identify test files
        assert "test_user_service.py" in result
        
        # Should have implementation steps
        assert "Modify" in result or "Update" in result
    
    @pytest.mark.asyncio
    async def test_complex_traversal(self, neo4j_driver):
        """Test complex graph traversal queries."""
        context_tools = ContextTools(neo4j_driver)
        
        # Get context for UserController - should show full dependency chain
        result = await context_tools.get_context_for_symbol("UserController")
        
        # Should show that UserController uses UserService
        assert "UserService" in result
        
        # Should show methods
        assert "handle_create" in result or "handle_get" in result
    
    @pytest.mark.asyncio
    async def test_documentation_integration(self, mcp_server):
        """Test documentation node integration."""
        # Get context for a file that has documentation
        result = await mcp_server.context_tools.get_context_for_symbol("AuthService")
        
        # Should include concept if documentation nodes are linked
        if "JWT Authentication" in result:
            assert "Authentication" in result
    
    @pytest.mark.asyncio
    async def test_mcp_tool_calls(self, mcp_server):
        """Test MCP tool calls through the server interface."""
        # Test listing tools
        tools = await mcp_server.server.list_tools()
        assert len(tools) == 3
        assert any(t.name == "getContextForFiles" for t in tools)
        
        # Test calling getContextForFiles
        result = await mcp_server.server.call_tool(
            "getContextForFiles",
            {"file_paths": ["user_service.py"]}
        )
        assert len(result) == 1
        assert "UserService" in result[0].text
        
        # Test calling getContextForSymbol
        result = await mcp_server.server.call_tool(
            "getContextForSymbol",
            {"symbol_name": "UserService", "symbol_type": "class"}
        )
        assert len(result) == 1
        assert "UserService" in result[0].text
        
        # Test calling buildPlanForChange
        result = await mcp_server.server.call_tool(
            "buildPlanForChange",
            {"change_request": "Add password reset functionality"}
        )
        assert len(result) == 1
        assert "Implementation Plan" in result[0].text
    
    def test_verify_test_data(self, neo4j_driver):
        """Verify test data was loaded correctly."""
        with neo4j_driver.session() as session:
            # Check UserService exists
            result = session.run(
                "MATCH (n:CLASS {name: 'UserService'}) RETURN n"
            ).single()
            assert result is not None
            
            # Check relationships exist
            result = session.run("""
                MATCH (us:CLASS {name: 'UserService'})-[:HAS_METHOD]->(m)
                RETURN count(m) as method_count
            """).single()
            assert result["method_count"] >= 3
            
            # Check file nodes exist
            result = session.run("""
                MATCH (f:FILE)
                RETURN count(f) as file_count
            """).single()
            assert result["file_count"] >= 4


@pytest.mark.asyncio
async def test_server_lifecycle():
    """Test server startup and shutdown."""
    server = BlarifyMCPServer()
    
    # Test connection
    await server._connect_to_neo4j()
    assert server.driver is not None
    assert server.context_tools is not None
    assert server.planning_tools is not None
    
    # Test tool availability
    tools = await server.server.list_tools()
    assert len(tools) == 3
    
    # Cleanup
    server.driver.close()