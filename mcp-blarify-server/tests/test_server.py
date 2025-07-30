"""Tests for MCP server."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.server import BlarifyMCPServer, GetContextForFilesArgs, GetContextForSymbolArgs, BuildPlanForChangeArgs


class TestBlarifyMCPServer:
    """Test MCP server functionality."""
    
    @pytest.fixture
    def mock_neo4j_driver(self):
        """Create a mock Neo4j driver."""
        driver = Mock()
        driver.verify_connectivity = Mock()
        driver.close = Mock()
        driver.session = Mock()
        return driver
    
    @pytest.fixture
    async def server(self, mock_neo4j_driver):
        """Create a server instance with mocked dependencies."""
        with patch('src.server.GraphDatabase') as mock_gdb:
            mock_gdb.driver.return_value = mock_neo4j_driver
            with patch.dict('os.environ', {
                'NEO4J_URI': 'bolt://test:7687',
                'NEO4J_USERNAME': 'test',
                'NEO4J_PASSWORD': 'test'
            }):
                server = BlarifyMCPServer()
                await server._connect_to_neo4j()
                return server
    
    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test listing available tools."""
        tools = await server.server.list_tools()
        
        assert len(tools) == 3
        tool_names = [tool.name for tool in tools]
        assert "getContextForFiles" in tool_names
        assert "getContextForSymbol" in tool_names
        assert "buildPlanForChange" in tool_names
    
    @pytest.mark.asyncio
    async def test_get_context_for_files_args(self):
        """Test getContextForFiles argument validation."""
        args = GetContextForFilesArgs(file_paths=["src/main.py", "tests/test_main.py"])
        assert args.file_paths == ["src/main.py", "tests/test_main.py"]
        
        # Test validation
        with pytest.raises(ValueError):
            GetContextForFilesArgs()
    
    @pytest.mark.asyncio
    async def test_get_context_for_symbol_args(self):
        """Test getContextForSymbol argument validation."""
        args = GetContextForSymbolArgs(symbol_name="UserService", symbol_type="class")
        assert args.symbol_name == "UserService"
        assert args.symbol_type == "class"
        
        # Test without type
        args2 = GetContextForSymbolArgs(symbol_name="process_data")
        assert args2.symbol_name == "process_data"
        assert args2.symbol_type is None
    
    @pytest.mark.asyncio
    async def test_build_plan_for_change_args(self):
        """Test buildPlanForChange argument validation."""
        args = BuildPlanForChangeArgs(change_request="Add email verification to registration")
        assert args.change_request == "Add email verification to registration"
    
    @pytest.mark.asyncio
    async def test_call_tool_get_context_for_files(self, server):
        """Test calling getContextForFiles tool."""
        # Mock the context tools
        server.context_tools.get_context_for_files = AsyncMock(
            return_value="# Context for Files\n\nFile information..."
        )
        
        result = await server.server.call_tool(
            "getContextForFiles",
            {"file_paths": ["src/main.py"]}
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Context for Files" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_error_handling(self, server):
        """Test error handling in tool calls."""
        # Mock to raise an error
        server.context_tools.get_context_for_files = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        result = await server.server.call_tool(
            "getContextForFiles",
            {"file_paths": ["src/main.py"]}
        )
        
        assert len(result) == 1
        assert "Error executing getContextForFiles" in result[0].text
        assert "Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_unknown_tool(self, server):
        """Test calling an unknown tool."""
        result = await server.server.call_tool(
            "unknownTool",
            {"arg": "value"}
        )
        
        assert len(result) == 1
        assert "Unknown tool: unknownTool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_neo4j_connection_error(self):
        """Test handling Neo4j connection errors."""
        with patch('src.server.GraphDatabase') as mock_gdb:
            mock_driver = Mock()
            mock_driver.verify_connectivity.side_effect = Exception("Connection failed")
            mock_gdb.driver.return_value = mock_driver
            
            server = BlarifyMCPServer()
            
            with pytest.raises(Exception) as exc_info:
                await server._connect_to_neo4j()
            
            assert "Connection failed" in str(exc_info.value)