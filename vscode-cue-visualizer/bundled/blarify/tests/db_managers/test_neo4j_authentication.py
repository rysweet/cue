"""
Comprehensive tests for Neo4j authentication compatibility.
Tests Neo4j 4.x and 5.x authentication formats, error handling, and fallback mechanisms.
"""
import pytest
import os
import logging
from unittest.mock import Mock, patch, MagicMock, call
from neo4j import Driver, exceptions, basic_auth

# Import the module under test
from blarify.db_managers.neo4j_manager import Neo4jManager


class TestNeo4jAuthentication:
    """Test suite for Neo4j authentication compatibility and error handling."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock environment variables
        self.test_uri = "bolt://localhost:7687"
        self.test_user = "neo4j"
        self.test_password = "test_password"
        
        # Set up environment variables
        os.environ["NEO4J_URI"] = self.test_uri
        os.environ["NEO4J_USERNAME"] = self.test_user
        os.environ["NEO4J_PASSWORD"] = self.test_password

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up environment variables
        for key in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]:
            if key in os.environ:
                del os.environ[key]

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_neo4j_5x_authentication_success(self, mock_graph_database):
        """Test successful authentication using Neo4j 5.x format."""
        # Mock driver and session
        mock_driver = Mock(spec=Driver)
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.__getitem__ = Mock(return_value=1)
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        
        mock_graph_database.driver.return_value = mock_driver
        
        # Create Neo4jManager instance
        manager = Neo4jManager()
        
        # Verify that basic_auth was used
        mock_graph_database.driver.assert_called_with(
            self.test_uri, 
            auth=basic_auth(self.test_user, self.test_password),
            max_connection_pool_size=50
        )
        
        # Verify authentication was verified
        mock_session.run.assert_called_with("RETURN 1 as test")
        
        assert manager.driver == mock_driver
        assert manager.repo_id == "default_repo"
        assert manager.entity_id == "default_user"

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_missing_key_principal_error_fallback(self, mock_graph_database):
        """Test fallback to Neo4j 4.x format when 'missing key principal' error occurs."""
        # Mock driver for successful fallback
        mock_driver_fallback = Mock(spec=Driver)
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.__getitem__ = Mock(return_value=1)
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver_fallback.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver_fallback.session.return_value.__exit__ = Mock(return_value=None)
        
        # First call (5.x format) raises AuthError with "missing key principal"
        # Second call (4.x format) succeeds
        mock_graph_database.driver.side_effect = [
            exceptions.AuthError("missing key `principal` in auth token"),
            mock_driver_fallback
        ]
        
        with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
            # Create Neo4jManager instance
            manager = Neo4jManager()
            
            # Verify both authentication attempts were made
            calls = mock_graph_database.driver.call_args_list
            assert len(calls) == 2
            
            # First call should use basic_auth (Neo4j 5.x format)
            first_call = calls[0]
            assert first_call[1]['auth'] == basic_auth(self.test_user, self.test_password)
            
            # Second call should use tuple format (Neo4j 4.x format)
            second_call = calls[1]
            assert second_call[1]['auth'] == (self.test_user, self.test_password)
            
            # Verify logging occurred
            mock_logger.error.assert_any_call(
                "Neo4j authentication failed with 'missing key principal' error. "
                "This indicates a compatibility issue with Neo4j 5.x authentication format."
            )
            mock_logger.info.assert_any_call("Attempting fallback authentication method...")
            mock_logger.info.assert_any_call("Fallback authentication successful - using Neo4j 4.x compatible format")
            
            assert manager.driver == mock_driver_fallback

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_authentication_error_no_fallback(self, mock_graph_database):
        """Test authentication error handling when not a 'missing key principal' error."""
        # Mock AuthError that is not "missing key principal"
        auth_error = exceptions.AuthError("Invalid username or password")
        mock_graph_database.driver.side_effect = auth_error
        
        with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
            with pytest.raises(exceptions.AuthError):
                Neo4jManager()
            
            # Verify error was logged
            mock_logger.error.assert_called_with(f"Neo4j authentication error: {auth_error}")
            
            # Verify only one attempt was made (no fallback)
            assert mock_graph_database.driver.call_count == 1

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_fallback_authentication_also_fails(self, mock_graph_database):
        """Test behavior when both 5.x and 4.x authentication methods fail."""
        original_error = exceptions.AuthError("missing key `principal` in auth token")
        fallback_error = exceptions.AuthError("Connection refused")
        
        # First call raises "missing key principal", second call raises different error
        mock_graph_database.driver.side_effect = [original_error, fallback_error]
        
        with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
            with pytest.raises(Exception) as exc_info:
                Neo4jManager()
            
            # Verify both errors are included in the final exception
            assert "Neo4j authentication failed with both 5.x and 4.x formats" in str(exc_info.value)
            assert str(original_error) in str(exc_info.value)
            assert str(fallback_error) in str(exc_info.value)
            
            # Verify appropriate logging
            mock_logger.error.assert_any_call("Fallback authentication also failed: Connection refused")

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_service_unavailable_retry_mechanism(self, mock_graph_database):
        """Test retry mechanism for ServiceUnavailable errors."""
        # Mock driver for successful connection on third attempt
        mock_driver = Mock(spec=Driver)
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.__getitem__ = Mock(return_value=1)
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        
        # First two attempts fail, third succeeds
        service_error = exceptions.ServiceUnavailable("Neo4j service unavailable")
        mock_graph_database.driver.side_effect = [service_error, service_error, mock_driver]
        
        with patch('blarify.db_managers.neo4j_manager.time.sleep') as mock_sleep:
            with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
                manager = Neo4jManager()
                
                # Verify 3 attempts were made
                assert mock_graph_database.driver.call_count == 3
                
                # Verify exponential backoff sleep calls
                expected_calls = [call(1), call(2)]  # 2^0=1, 2^1=2
                mock_sleep.assert_has_calls(expected_calls)
                
                # Verify warning logs for retry attempts
                mock_logger.warning.assert_any_call(
                    f"Neo4j connection attempt 1 failed: {service_error}. Retrying in 1 seconds..."
                )
                mock_logger.warning.assert_any_call(
                    f"Neo4j connection attempt 2 failed: {service_error}. Retrying in 2 seconds..."
                )
                mock_logger.info.assert_called_with("Neo4j connection established successfully on attempt 3")
                
                assert manager.driver == mock_driver

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_service_unavailable_max_retries_exceeded(self, mock_graph_database):
        """Test behavior when ServiceUnavailable persists beyond max retries."""
        service_error = exceptions.ServiceUnavailable("Neo4j service unavailable")
        mock_graph_database.driver.side_effect = service_error
        
        with patch('blarify.db_managers.neo4j_manager.time.sleep'):
            with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
                with pytest.raises(exceptions.ServiceUnavailable):
                    Neo4jManager()
                
                # Verify 3 attempts were made
                assert mock_graph_database.driver.call_count == 3
                
                # Verify final error log
                mock_logger.error.assert_called_with(
                    f"Neo4j connection failed after 3 attempts: {service_error}"
                )

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_authentication_verification_failure(self, mock_graph_database):
        """Test behavior when authentication verification fails."""
        mock_driver = Mock(spec=Driver)
        mock_session = Mock()
        
        # Mock verification query to fail
        verification_error = Exception("Verification failed")
        mock_session.run.side_effect = verification_error
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        
        mock_graph_database.driver.return_value = mock_driver
        
        with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
            with pytest.raises(Exception):
                Neo4jManager()
            
            # Verify verification was attempted
            mock_session.run.assert_called_with("RETURN 1 as test")
            
            # The error gets caught in the general exception handler in the retry loop
            # So we check for the general error log instead
            mock_logger.error.assert_any_call(f"Unexpected error during Neo4j connection attempt 3: {verification_error}")

    def test_custom_parameters(self):
        """Test Neo4jManager with custom parameters instead of environment variables."""
        custom_uri = "bolt://custom:7687"
        custom_user = "custom_user"
        custom_password = "custom_password"
        custom_connections = 100
        custom_repo = "custom_repo"
        custom_entity = "custom_entity"
        
        with patch('blarify.db_managers.neo4j_manager.GraphDatabase') as mock_graph_database:
            mock_driver = Mock(spec=Driver)
            mock_session = Mock()
            mock_result = Mock()
            mock_record = Mock()
            mock_record.__getitem__ = Mock(return_value=1)
            mock_result.single.return_value = mock_record
            mock_session.run.return_value = mock_result
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=None)
            
            mock_graph_database.driver.return_value = mock_driver
            
            manager = Neo4jManager(
                uri=custom_uri,
                user=custom_user,
                password=custom_password,
                max_connections=custom_connections,
                repo_id=custom_repo,
                entity_id=custom_entity
            )
            
            # Verify custom parameters were used
            mock_graph_database.driver.assert_called_with(
                custom_uri,
                auth=basic_auth(custom_user, custom_password),
                max_connection_pool_size=custom_connections
            )
            
            assert manager.repo_id == custom_repo
            assert manager.entity_id == custom_entity


class TestNeo4jHealthCheck:
    """Test suite for Neo4j health check and diagnostic functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_uri = "bolt://localhost:7687"
        self.test_user = "neo4j"
        self.test_password = "test_password"
        
        os.environ["NEO4J_URI"] = self.test_uri
        os.environ["NEO4J_USERNAME"] = self.test_user
        os.environ["NEO4J_PASSWORD"] = self.test_password

    def teardown_method(self):
        """Clean up after each test."""
        for key in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]:
            if key in os.environ:
                del os.environ[key]

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_health_check_success(self, mock_graph_database):
        """Test successful health check."""
        mock_driver = Mock(spec=Driver)
        mock_session = Mock()
        
        # Mock verification query result
        mock_verification_result = Mock()
        mock_verification_record = Mock()
        mock_verification_record.__getitem__ = Mock(return_value=1)
        mock_verification_result.single.return_value = mock_verification_record
        
        # Mock server info query result
        mock_server_result = Mock()
        mock_server_record = Mock()
        mock_server_record.__getitem__ = Mock(side_effect=lambda key: {
            "name": "Neo4j Kernel",
            "versions": ["5.0.0"],
            "edition": "community"
        }[key])
        mock_server_result.__iter__ = Mock(return_value=iter([mock_server_record]))
        
        # Mock health check write query
        mock_health_result = Mock()
        
        # Configure session.run to return different results based on query
        def run_side_effect(query, **kwargs):
            if "RETURN 1 as test" in query:
                return mock_verification_result
            elif "CALL dbms.components()" in query:
                return mock_server_result
            elif "CREATE (test:HealthCheck" in query:
                return mock_health_result
            return Mock()
        
        mock_session.run.side_effect = run_side_effect
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        
        mock_graph_database.driver.return_value = mock_driver
        
        manager = Neo4jManager()
        health_result = manager.health_check()
        
        assert health_result["status"] == "healthy"
        assert "server_info" in health_result
        assert "timestamp" in health_result
        assert len(health_result["server_info"]) == 1
        assert health_result["server_info"][0]["name"] == "Neo4j Kernel"

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_health_check_failure(self, mock_graph_database):
        """Test health check failure."""
        mock_driver = Mock(spec=Driver)
        mock_session_init = Mock()
        mock_session_health = Mock()
        
        # Mock successful initialization
        mock_verification_result = Mock()
        mock_verification_record = Mock()
        mock_verification_record.__getitem__ = Mock(return_value=1)
        mock_verification_result.single.return_value = mock_verification_record
        mock_session_init.run.return_value = mock_verification_result
        
        # Mock health check failure
        mock_session_health.run.side_effect = Exception("Connection failed")
        
        # Configure driver to return different sessions for init and health check
        session_count = 0
        def session_context_manager():
            nonlocal session_count
            session_count += 1
            if session_count == 1:
                return MockContextManager(mock_session_init)
            else:
                return MockContextManager(mock_session_health)
        
        mock_driver.session.side_effect = session_context_manager
        mock_graph_database.driver.return_value = mock_driver
        
        with patch('blarify.db_managers.neo4j_manager.logger'):
            manager = Neo4jManager()
            health_result = manager.health_check()
        
        assert health_result["status"] == "unhealthy"
        assert "error" in health_result
        assert "Connection failed" in health_result["error"]
        assert "timestamp" in health_result


class MockContextManager:
    """Helper class for mocking context managers."""
    def __init__(self, mock_obj):
        self.mock_obj = mock_obj
    
    def __enter__(self):
        return self.mock_obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_get_server_info_success(self, mock_graph_database):
        """Test successful server info retrieval."""
        mock_driver = Mock(spec=Driver)
        mock_session = Mock()
        
        # Mock verification query
        mock_verification_result = Mock()
        mock_verification_record = Mock()
        mock_verification_record.__getitem__ = Mock(return_value=1)
        mock_verification_result.single.return_value = mock_verification_record
        
        # Mock server info query with simpler approach
        mock_server_result = Mock()
        
        # Create mock records
        record1 = Mock()
        record1.__getitem__ = Mock(side_effect=lambda key: {
            "name": "Neo4j Kernel", "versions": ["5.0.0"], "edition": "community"
        }[key])
        
        record2 = Mock()
        record2.__getitem__ = Mock(side_effect=lambda key: {
            "name": "APOC", "versions": ["5.0.0"], "edition": "community"
        }[key])
        
        mock_server_result.__iter__ = Mock(return_value=iter([record1, record2]))
        
        def run_side_effect(query, **kwargs):
            if "RETURN 1 as test" in query:
                return mock_verification_result
            elif "CALL dbms.components()" in query:
                return mock_server_result
            return Mock()
        
        mock_session.run.side_effect = run_side_effect
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        
        mock_graph_database.driver.return_value = mock_driver
        
        manager = Neo4jManager()
        server_info = manager.get_server_info()
        
        assert len(server_info) == 2
        assert server_info[0]["name"] == "Neo4j Kernel"
        assert server_info[1]["name"] == "APOC"

    @patch('blarify.db_managers.neo4j_manager.GraphDatabase')
    def test_get_server_info_failure(self, mock_graph_database):
        """Test server info retrieval failure."""
        mock_driver = Mock(spec=Driver)
        mock_session = Mock()
        
        # Mock verification query success, server info query failure
        mock_verification_result = Mock()
        mock_verification_record = Mock()
        mock_verification_record.__getitem__ = Mock(return_value=1)
        mock_verification_result.single.return_value = mock_verification_record
        
        def run_side_effect(query, **kwargs):
            if "RETURN 1 as test" in query:
                return mock_verification_result
            elif "CALL dbms.components()" in query:
                raise Exception("Permission denied")
            return Mock()
        
        mock_session.run.side_effect = run_side_effect
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        
        mock_graph_database.driver.return_value = mock_driver
        
        with patch('blarify.db_managers.neo4j_manager.logger') as mock_logger:
            manager = Neo4jManager()
            server_info = manager.get_server_info()
        
        assert server_info == []
        mock_logger.warning.assert_called_with("Could not retrieve Neo4j server info: Permission denied")


if __name__ == "__main__":
    # Configure logging for test runs
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v"])