"""Simple integration tests for MCP server that work with existing Neo4j."""

import pytest
import pytest_asyncio
import os
from unittest.mock import Mock, AsyncMock

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import BlarifyMCPServer


class TestIntegrationSimple:
    """Simple integration tests that don't require Neo4j setup."""
    
    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create MCP server instance with mocked driver."""
        server = BlarifyMCPServer()
        # Mock the Neo4j driver to avoid connection issues
        server.driver = Mock()
        server.driver.verify_connectivity = Mock()
        server.driver.close = Mock()
        
        # Mock the session
        mock_session = AsyncMock()
        server.driver.session = Mock(return_value=mock_session)
        
        yield server
        
    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_server):
        """Test that server initializes correctly."""
        assert mcp_server is not None
        assert mcp_server.driver is not None
        
    @pytest.mark.asyncio
    async def test_context_tools_exist(self, mcp_server):
        """Test that context tools are available."""
        assert hasattr(mcp_server, 'context_tools')
        assert mcp_server.context_tools is not None
        
    @pytest.mark.asyncio
    async def test_planning_tools_exist(self, mcp_server):
        """Test that planning tools are available."""
        assert hasattr(mcp_server, 'planning_tools')
        assert mcp_server.planning_tools is not None
        
    @pytest.mark.asyncio 
    async def test_get_context_with_mock(self, mcp_server):
        """Test get context with mocked data."""
        # Mock the query result
        mock_result = [
            {
                "fileName": "test.py",
                "filePath": "/test/test.py",
                "classes": ["TestClass"],
                "functions": ["test_func"]
            }
        ]
        
        # Setup mock session
        mock_session = AsyncMock()
        mock_run = AsyncMock()
        mock_run.data.return_value = mock_result
        mock_session.run = AsyncMock(return_value=mock_run)
        mcp_server.driver.session.return_value = mock_session
        
        # Test the method
        result = await mcp_server.context_tools.get_context_for_files(["test.py"])
        
        assert result is not None
        assert "Context for Files" in result
        
    @pytest.mark.asyncio
    async def test_build_plan_with_mock(self, mcp_server):
        """Test build plan with mocked data."""
        # Mock the query result
        mock_result = [
            {
                "fileName": "test.py",
                "complexity": 5,
                "dependencies": []
            }
        ]
        
        # Setup mock session
        mock_session = AsyncMock()
        mock_run = AsyncMock()
        mock_run.data.return_value = mock_result
        mock_session.run = AsyncMock(return_value=mock_run)
        mcp_server.driver.session.return_value = mock_session
        
        # Test the method
        result = await mcp_server.planning_tools.build_plan_for_change(
            "Add new feature",
            ["test.py"]
        )
        
        assert result is not None
        assert "Implementation Plan" in result