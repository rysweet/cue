"""Tests for LLM processor."""

import pytest
from unittest.mock import Mock, patch
from src.processors.llm_processor import LLMProcessor


class TestLLMProcessor:
    """Test LLM processor functionality."""
    
    @pytest.fixture
    def llm_processor_disabled(self):
        """Create an LLM processor with LLM disabled."""
        with patch.dict('os.environ', {'AZURE_OPENAI_API_KEY': ''}):
            return LLMProcessor()
    
    @pytest.fixture
    def llm_processor_enabled(self):
        """Create an LLM processor with mocked LLM."""
        with patch.dict('os.environ', {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }):
            with patch('src.processors.llm_processor.AzureOpenAI'):
                return LLMProcessor()
    
    def test_llm_disabled(self, llm_processor_disabled):
        """Test LLM processor when disabled."""
        assert not llm_processor_disabled.enabled
        assert llm_processor_disabled.client is None
    
    def test_organize_file_context_without_llm(self, llm_processor_disabled):
        """Test organizing file context without LLM."""
        context = {
            "file": {"path": "/src/main.py"},
            "contents": [{"name": "main", "_labels": ["FUNCTION"]}]
        }
        
        result = llm_processor_disabled.organize_file_context(context)
        assert "Context for File: /src/main.py" in result
        assert "FUNCTION: main" in result
    
    def test_organize_symbol_context_without_llm(self, llm_processor_disabled):
        """Test organizing symbol context without LLM."""
        context = {
            "symbol": {"name": "UserService", "_labels": ["CLASS"]},
            "file": {"path": "/src/services/user.py"}
        }
        
        result = llm_processor_disabled.organize_symbol_context(context)
        assert "Context for Symbol: UserService" in result
        assert "Type**: CLASS" in result
    
    def test_extract_entities_basic(self, llm_processor_disabled):
        """Test basic entity extraction without LLM."""
        change_request = "Update the UserService class and AuthController to add email verification"
        
        entities = llm_processor_disabled.extract_entities_from_request(change_request)
        assert "UserService" in entities
        assert "AuthController" in entities
    
    def test_create_implementation_plan_without_llm(self, llm_processor_disabled):
        """Test creating implementation plan without LLM."""
        change_request = "Add email verification"
        impact_analysis = {
            "UserService": {
                "target": {"name": "UserService"},
                "dependents": [{"name": "UserController"}],
                "containing_files": [{"path": "/src/services/user.py"}]
            }
        }
        
        plan = llm_processor_disabled.create_implementation_plan(change_request, impact_analysis)
        assert "Implementation Plan" in plan
        assert "Add email verification" in plan
        assert "Entities Affected: 1" in plan
    
    @patch('src.processors.llm_processor.AzureOpenAI')
    def test_organize_file_context_with_llm(self, mock_azure, llm_processor_enabled):
        """Test organizing file context with LLM."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Organized Context\nFile details..."))]
        llm_processor_enabled.client.chat.completions.create.return_value = mock_response
        
        context = {
            "file": {"path": "/src/main.py"},
            "contents": []
        }
        
        result = llm_processor_enabled.organize_file_context(context)
        assert "Organized Context" in result
    
    def test_extract_entities_from_camelcase(self, llm_processor_disabled):
        """Test entity extraction from CamelCase."""
        change_request = "The UserService and PaymentProcessor need updates"
        entities = llm_processor_disabled._extract_entities_basic(change_request)
        
        assert "UserService" in entities
        assert "PaymentProcessor" in entities
    
    def test_extract_entities_from_quotes(self, llm_processor_disabled):
        """Test entity extraction from quoted strings."""
        change_request = 'Update "user_service.py" and `auth_controller.js`'
        entities = llm_processor_disabled._extract_entities_basic(change_request)
        
        assert "user_service.py" in entities
        assert "auth_controller.js" in entities