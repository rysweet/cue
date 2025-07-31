"""
Tests for LLM service and description generation.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import json

from blarify.llm_descriptions.llm_service import LLMService
from blarify.llm_descriptions.description_generator import DescriptionGenerator
from blarify.graph.graph import Graph
from blarify.graph.node.class_node import ClassNode
from blarify.graph.node.function_node import FunctionNode
from blarify.graph.node.file_node import FileNode
from blarify.graph.node.description_node import DescriptionNode
from blarify.graph.node.types.node_labels import NodeLabels
from tests.fixtures.node_factories import (
    create_class_node, create_function_node, create_file_node
)


class TestLLMService(unittest.TestCase):
    """Test LLM service functionality."""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_MODEL_CHAT': 'gpt-4'
    })
    def setUp(self):
        """Set up test fixtures."""
        self.service = LLMService()
        
    def test_initialization_with_env_vars(self):
        """Test LLM service initialization with environment variables."""
        self.assertIsNotNone(self.service.client)
        self.assertEqual(self.service.deployment_name, 'gpt-4')
        
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_missing_config(self):
        """Test initialization fails with missing configuration."""
        with self.assertRaises(ValueError) as context:
            LLMService()
            
        self.assertIn("Azure OpenAI configuration is incomplete", str(context.exception))
        
    @patch('openai.AzureOpenAI')
    def test_generate_description_success(self, mock_openai_class):
        """Test successful description generation."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="This class manages users"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        
        code = """
        class UserManager:
            def create_user(self, name, email):
                pass
        """
        
        prompt = f"Generate a description for the following class named UserManager:\n\n{code}"
        description = service.generate_description(prompt)
        
        self.assertEqual(description, "This class manages users")
        mock_client.chat.completions.create.assert_called_once()
        
    @patch('openai.AzureOpenAI')
    def test_generate_description_with_retry(self, mock_openai_class):
        """Test description generation with retry on failure."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # First call fails, second succeeds
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Success"))]
        
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_response
        ]
        
        service = LLMService()
        
        description = service.generate_description("Generate a description for this code")
        
        self.assertEqual(description, "Success")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        
    @patch('openai.AzureOpenAI')
    def test_generate_description_all_retries_fail(self, mock_openai_class):
        """Test description generation when all retries fail."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # All calls fail
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        service = LLMService()
        
        description = service.generate_description("Generate a description for this code")
        
        self.assertEqual(description, "Failed to generate description")
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)  # Initial + 2 retries
        
    def test_batch_description_generation(self):
        """Test batch description generation."""
        prompts = [
            {"id": "node1", "prompt": "Describe function foo"},
            {"id": "node2", "prompt": "Describe class Bar"}
        ]
        
        results = self.service.generate_batch_descriptions(prompts)
        
        self.assertIsInstance(results, dict)
        self.assertIn("node1", results)
        self.assertIn("node2", results)
        
    def test_is_enabled(self):
        """Test checking if LLM service is enabled."""
        self.assertTrue(self.service.is_enabled())


class TestDescriptionGenerator(unittest.TestCase):
    """Test description generation for graph nodes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.generate_description.return_value = "Test description"
        self.generator = DescriptionGenerator(llm_service=self.mock_llm)
        self.graph = Graph()
        
    def test_should_generate_description(self):
        """Test determining which nodes should get descriptions."""
        # Should generate for classes and functions
        class_node = create_class_node("TestClass")
        func_node = create_function_node("test_func")
        
        self.assertTrue(self.generator.should_generate_description(class_node))
        self.assertTrue(self.generator.should_generate_description(func_node))
        
        # Should not generate for files
        file_node = create_file_node("test.py")
        self.assertFalse(self.generator.should_generate_description(file_node))
        
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_get_file_content(self, mock_exists, mock_open):
        """Test reading file content for context."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "file content"
        
        content = self.generator.get_file_content("/test/file.py")
        
        self.assertEqual(content, "file content")
        mock_open.assert_called_once_with("/test/file.py", 'r', encoding='utf-8')
        
    def test_get_file_content_not_found(self):
        """Test handling missing files."""
        content = self.generator.get_file_content("/nonexistent/file.py")
        
        self.assertIsNone(content)
        
    def test_extract_code_snippet(self):
        """Test extracting code snippets for nodes."""
        file_content = """line 1
line 2
class TestClass:
    def method(self):
        pass
line 6
line 7"""
        
        # Test class extraction
        class_node = create_class_node("TestClass", start_line=3, end_line=5)
        snippet = self.generator.extract_code_snippet(class_node, file_content)
        
        self.assertIn("class TestClass:", snippet)
        self.assertIn("def method", snippet)
        
        # Test with context lines
        snippet_with_context = self.generator.extract_code_snippet(
            class_node, file_content, context_lines=1
        )
        
        self.assertIn("line 2", snippet_with_context)
        self.assertIn("line 6", snippet_with_context)
        
    def test_generate_description_for_node(self):
        """Test generating description for a specific node."""
        class_node = create_class_node("UserManager")
        self.graph.add_node(class_node)
        
        # Mock file reading
        with patch.object(self.generator, 'get_file_content') as mock_get_content:
            mock_get_content.return_value = """
class UserManager:
    def create_user(self, name):
        pass
"""
            
            desc_node = self.generator.generate_description_for_node(
                class_node, self.graph
            )
            
        self.assertIsInstance(desc_node, DescriptionNode)
        self.assertEqual(desc_node.description, "Test description")
        self.assertEqual(desc_node.target_node_id, class_node.id)
        
    def test_generate_descriptions_for_graph(self):
        """Test generating descriptions for all eligible nodes in graph."""
        # Create graph with multiple nodes
        file_node = create_file_node("main.py")
        class_node = create_class_node("MainClass", file_node.path)
        func_node = create_function_node("main_func", file_node.path)
        
        self.graph.add_node(file_node)
        self.graph.add_node(class_node)
        self.graph.add_node(func_node)
        
        # Mock file content
        with patch.object(self.generator, 'get_file_content') as mock_get_content:
            mock_get_content.return_value = """
class MainClass:
    pass

def main_func():
    pass
"""
            
            # Generate descriptions
            self.generator.generate_descriptions(self.graph)
            
        # Check description nodes were created
        desc_nodes = self.graph.get_nodes_by_label(NodeLabels.DESCRIPTION)
        self.assertEqual(len(desc_nodes), 2)  # One for class, one for function
        
        # Verify relationships were created
        relationships = self.graph.get_relationships_as_objects()
        desc_relationships = [r for r in relationships 
                            if r['type'] == 'HAS_DESCRIPTION']
        self.assertEqual(len(desc_relationships), 2)
        
    def test_generate_descriptions_with_limit(self):
        """Test respecting description generation limit."""
        # Create many nodes
        for i in range(10):
            node = create_function_node(f"func_{i}")
            self.graph.add_node(node)
            
        with patch.object(self.generator, 'get_file_content') as mock_get_content:
            mock_get_content.return_value = "def func(): pass"
            
            # Generate with limit
            self.generator.generate_descriptions(self.graph, max_descriptions=3)
            
        # Should only create 3 descriptions
        desc_nodes = self.graph.get_nodes_by_label(NodeLabels.DESCRIPTION)
        self.assertEqual(len(desc_nodes), 3)
        
    def test_handle_special_characters_in_code(self):
        """Test handling code with special characters."""
        code_with_special = '''
def process_data(text: str) -> dict[str, Any]:
    """Process text with regex patterns."""
    pattern = r'\\d{3}-\\d{3}-\\d{4}'  # Phone pattern
    return {"processed": True}
'''
        
        class_node = create_function_node("process_data", start_line=2, end_line=5)
        snippet = self.generator.extract_code_snippet(class_node, code_with_special)
        
        self.assertIn("def process_data", snippet)
        self.assertIn("regex patterns", snippet)


class TestDescriptionNodeIntegration(unittest.TestCase):
    """Test description node creation and relationships."""
    
    def test_description_node_creation(self):
        """Test creating description nodes with proper attributes."""
        target_id = "class_123"
        description = "This class handles user authentication"
        model = "gpt-4"
        
        desc_node = DescriptionNode(
            target_node_id=target_id,
            description=description,
            model=model
        )
        
        self.assertEqual(desc_node.target_node_id, target_id)
        self.assertEqual(desc_node.description, description)
        self.assertEqual(desc_node.model, model)
        self.assertEqual(desc_node.label, NodeLabels.DESCRIPTION)
        
        # Check ID generation
        self.assertIn(target_id, desc_node.id)
        self.assertIn("description", desc_node.id)
        
    def test_description_node_serialization(self):
        """Test serializing description node to object."""
        desc_node = DescriptionNode(
            target_node_id="func_456",
            description="Calculates the sum of two numbers",
            model="gpt-3.5-turbo"
        )
        
        obj = desc_node.as_object()
        
        self.assertEqual(obj['type'], NodeLabels.DESCRIPTION.value)
        self.assertEqual(obj['attributes']['description'], "Calculates the sum of two numbers")
        self.assertEqual(obj['attributes']['model'], "gpt-3.5-turbo")
        self.assertEqual(obj['attributes']['target_node_id'], "func_456")


if __name__ == '__main__':
    unittest.main()