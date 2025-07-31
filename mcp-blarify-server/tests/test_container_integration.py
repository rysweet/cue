"""Test Neo4j container integration."""

import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_container import Neo4jContainerManager


class TestNeo4jContainerManager:
    """Test Neo4j container manager wrapper."""
    
    def test_init(self):
        """Test initialization."""
        manager = Neo4jContainerManager(data_dir="/tmp/test", debug=True)
        assert manager.data_dir == "/tmp/test"
        assert manager.debug is True
        assert manager.container_info is None
    
    @patch('subprocess.run')
    def test_start_container(self, mock_run):
        """Test starting a container."""
        # Mock successful Node.js execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '''
        {
            "containerId": "test-container-123",
            "uri": "bolt://localhost:7688",
            "boltPort": 7688,
            "httpPort": 7475,
            "httpsPort": 7474
        }
        '''
        mock_run.return_value = mock_result
        
        manager = Neo4jContainerManager()
        result = manager.start({
            "environment": "test",
            "password": "testpass",
            "username": "neo4j"
        })
        
        assert result["containerId"] == "test-container-123"
        assert result["uri"] == "bolt://localhost:7688"
        assert result["boltPort"] == 7688
        assert manager.container_info == result
    
    @patch('subprocess.run')
    def test_stop_container(self, mock_run):
        """Test stopping a container."""
        # First set up container info
        manager = Neo4jContainerManager()
        manager.container_info = {
            "containerId": "test-container-123",
            "uri": "bolt://localhost:7688"
        }
        
        # Mock successful stop
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true}'
        mock_run.return_value = mock_result
        
        manager.stop()
        assert manager.container_info is None
    
    @patch('subprocess.run')
    def test_is_running(self, mock_run):
        """Test checking if container is running."""
        manager = Neo4jContainerManager()
        manager.container_info = {
            "containerId": "test-container-123",
            "uri": "bolt://localhost:7688"
        }
        
        # Mock running check
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"running": true}'
        mock_run.return_value = mock_result
        
        assert manager.is_running() is True
    
    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test error handling."""
        # Mock Node.js error
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"error": "Docker not running"}'
        mock_run.return_value = mock_result
        
        manager = Neo4jContainerManager()
        with pytest.raises(RuntimeError) as exc_info:
            manager.start({"password": "test"})
        
        assert "Failed to start Neo4j" in str(exc_info.value)
        assert "Docker not running" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])