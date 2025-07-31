"""
Tests for LLM service and description generation.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import json
import pytest

from blarify.llm_descriptions.llm_service import LLMService
from blarify.llm_descriptions.description_generator import DescriptionGenerator
from blarify.graph.graph import Graph
from blarify.graph.node.class_node import ClassNode
from blarify.graph.node.function_node import FunctionNode
from blarify.graph.node.file_node import FileNode
from blarify.graph.node.description_node import DescriptionNode
from blarify.graph.node.types.node_labels import NodeLabels
from tests.fixtures.node_factories import (
    create_class_node, create_function_node, create_file_node, create_folder_node
)


class TestLLMService(unittest.TestCase):
    """Test LLM service functionality."""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_MODEL_CHAT': 'gpt-4'
    })
    @patch('openai.AzureOpenAI')
    def setUp(self, mock_openai_class):
        """Set up test fixtures."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test description"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        self.service = LLMService()
        self.service.client = mock_client  # Ensure the service uses the mocked client
        self.mock_client = mock_client
        
    @patch('openai.AzureOpenAI')
    def test_initialization_with_env_vars(self, mock_openai_class):
        """Test LLM service initialization with environment variables."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        service = LLMService()
        self.assertIsNotNone(service.client)
        self.assertEqual(service.deployment_name, 'gpt-4')
        
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_missing_config(self):
        """Test initialization fails with missing configuration."""
        with self.assertRaises(ValueError) as context:
            LLMService()
            
        self.assertIn("Azure OpenAI configuration is incomplete", str(context.exception))
        
    @pytest.mark.skipif(
        not os.getenv('AZURE_OPENAI_KEY'),
        reason="AZURE_OPENAI_KEY not set in environment"
    )
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
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_MODEL_CHAT': 'gpt-4'
        }):
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
        
    @pytest.mark.skipif(
        not os.getenv('AZURE_OPENAI_KEY'),
        reason="AZURE_OPENAI_KEY not set in environment"
    )
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
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_MODEL_CHAT': 'gpt-4'
        }):
            service = LLMService()
        
        description = service.generate_description("Generate a description for this code")
        
        self.assertEqual(description, "Success")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        
    @pytest.mark.skipif(
        not os.getenv('AZURE_OPENAI_KEY'),
        reason="AZURE_OPENAI_KEY not set in environment"
    )
    @patch('openai.AzureOpenAI')
    def test_generate_description_all_retries_fail(self, mock_openai_class):
        """Test description generation when all retries fail."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # All calls fail
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_MODEL_CHAT': 'gpt-4'
        }):
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
        
        # Mock the LLMService client attribute
        self.service.client = self.mock_client
        
        # Mock the responses
        self.mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content="Description for foo"))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Description for Bar"))])
        ]
        
        results = self.service.generate_batch_descriptions(prompts)
        
        self.assertIsInstance(results, dict)
        self.assertIn("node1", results)
        self.assertIn("node2", results)
        self.assertEqual(results["node1"], "Description for foo")
        self.assertEqual(results["node2"], "Description for Bar")
        
    @patch('openai.AzureOpenAI')
    def test_is_enabled(self, mock_openai_class):
        """Test checking if LLM service is enabled."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        service = LLMService()
        self.assertTrue(service.is_enabled())


class TestDescriptionGenerator(unittest.TestCase):
    """Test description generation for graph nodes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.generate_description.return_value = "Test description"
        self.mock_llm.is_enabled.return_value = True
        self.mock_llm.deployment_name = "gpt-4"
        self.mock_llm.generate_batch_descriptions.return_value = {}
        self.generator = DescriptionGenerator(llm_service=self.mock_llm)
        self.graph = Graph()
        
    def test_get_eligible_nodes(self):
        """Test getting eligible nodes for description generation."""
        # Create various node types
        file_node = create_file_node("test.py")
        class_node = create_class_node("TestClass")
        func_node = create_function_node("test_func")
        folder_node = create_folder_node("src")
        
        self.graph.add_node(file_node)
        self.graph.add_node(class_node)
        self.graph.add_node(func_node)
        self.graph.add_node(folder_node)
        
        # Get eligible nodes
        eligible_nodes = self.generator._get_eligible_nodes(self.graph)
        
        # File, class, and function should be eligible
        self.assertEqual(len(eligible_nodes), 3)
        node_labels = {node.label for node in eligible_nodes}
        self.assertIn(NodeLabels.FILE, node_labels)
        self.assertIn(NodeLabels.CLASS, node_labels)
        self.assertIn(NodeLabels.FUNCTION, node_labels)
        
        # Folder should not be eligible
        self.assertNotIn(NodeLabels.FOLDER, node_labels)
        
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_extract_node_context(self, mock_exists, mock_open):
        """Test extracting context information for nodes."""
        # Test for function node
        func_node = create_function_node("test_func")
        func_node.text = "def test_func(): pass"
        context = self.generator._extract_node_context(func_node, self.graph)
        
        self.assertIsNotNone(context)
        self.assertEqual(context["function_name"], "test_func")
        self.assertEqual(context["code_snippet"], "def test_func(): pass")
        
        # Test for class node
        class_node = create_class_node("TestClass")
        class_node.text = "class TestClass: pass"
        context = self.generator._extract_node_context(class_node, self.graph)
        
        self.assertIsNotNone(context)
        self.assertEqual(context["class_name"], "TestClass")
        self.assertEqual(context["code_snippet"], "class TestClass: pass")
        
    def test_detect_language(self):
        """Test language detection from file extensions."""
        # Test common extensions
        self.assertEqual(self.generator._detect_language(".py"), "Python")
        self.assertEqual(self.generator._detect_language(".js"), "JavaScript")
        self.assertEqual(self.generator._detect_language(".ts"), "TypeScript")
        self.assertEqual(self.generator._detect_language(".java"), "Java")
        self.assertEqual(self.generator._detect_language(".go"), "Go")
        self.assertEqual(self.generator._detect_language(".rb"), "Ruby")
        self.assertEqual(self.generator._detect_language(".php"), "PHP")
        self.assertEqual(self.generator._detect_language(".cs"), "C#")
        
        # Test unknown extension
        self.assertEqual(self.generator._detect_language(".xyz"), "Unknown")
        
    def test_generate_description_for_node(self):
        """Test generating description for a specific node."""
        class_node = create_class_node("UserManager")
        class_node.text = "class UserManager:\n    def create_user(self, name):\n        pass"
        self.graph.add_node(class_node)
        
        # Create prompt and generate description
        prompt_data = self.generator._create_prompt_for_node(class_node, self.graph)
        self.assertIsNotNone(prompt_data)
        self.assertEqual(prompt_data["id"], class_node.hashed_id)
        
        # Test description node creation
        desc_node, rel = self.generator._create_description_node_and_relationship(
            class_node, "Test description", self.graph
        )
        
        self.assertIsInstance(desc_node, DescriptionNode)
        self.assertEqual(desc_node.description_text, "Test description")
        self.assertEqual(desc_node.target_node_id, class_node.hashed_id)
        
    def test_generate_descriptions_for_graph(self):
        """Test generating descriptions for all eligible nodes in graph."""
        # Create graph with multiple nodes
        file_node = create_file_node("main.py")
        class_node = create_class_node("MainClass", file_node.path)
        func_node = create_function_node("main_func", file_node.path)
        
        self.graph.add_node(file_node)
        self.graph.add_node(class_node)
        self.graph.add_node(func_node)
        
        # Add text content to nodes
        class_node.text = "class MainClass:\n    pass"
        func_node.text = "def main_func():\n    pass"
        
        # Mock the batch descriptions to return descriptions for eligible nodes
        self.mock_llm.generate_batch_descriptions.return_value = {
            class_node.hashed_id: "This class handles main application logic",
            func_node.hashed_id: "This function is the entry point",
            file_node.hashed_id: "This file contains the main application"
        }
        
        # Generate descriptions
        description_nodes = self.generator.generate_descriptions_for_graph(self.graph)
            
        # Check description nodes were created
        desc_nodes = self.graph.get_nodes_by_label(NodeLabels.DESCRIPTION)
        self.assertEqual(len(desc_nodes), 3)  # One for file, one for class, one for function
        
        # Verify relationships were created
        relationships = self.graph.get_relationships_as_objects()
        desc_relationships = [r for r in relationships 
                            if r['type'] == 'HAS_DESCRIPTION']
        self.assertEqual(len(desc_relationships), 3)
        
    def test_generate_descriptions_with_limit(self):
        """Test respecting description generation limit."""
        # Create many nodes
        for i in range(10):
            node = create_function_node(f"func_{i}")
            self.graph.add_node(node)
            
        # Add text content to nodes and create mock descriptions
        mock_descriptions = {}
        for i, node in enumerate(self.graph.get_nodes_by_label(NodeLabels.FUNCTION)):
            node.text = "def func(): pass"
            if i < 3:  # Only first 3 should get descriptions
                mock_descriptions[node.hashed_id] = f"Description for function {i}"
        
        self.mock_llm.generate_batch_descriptions.return_value = mock_descriptions
        
        # Generate with limit
        description_nodes = self.generator.generate_descriptions_for_graph(self.graph, node_limit=3)
            
        # Should only create 3 descriptions
        desc_nodes = self.graph.get_nodes_by_label(NodeLabels.DESCRIPTION)
        self.assertEqual(len(desc_nodes), 3)
        
    def test_extract_referenced_nodes(self):
        """Test extracting node references from description text."""
        # Add some nodes to the graph
        class_node = create_class_node("UserManager")
        func_node = create_function_node("create_user")
        self.graph.add_node(class_node)
        self.graph.add_node(func_node)
        
        # Test description with references
        description = "This class uses `UserManager` to create users via 'create_user' function."
        
        referenced_nodes = self.generator._extract_referenced_nodes(description, self.graph)
        
        # Should find both referenced nodes
        self.assertEqual(len(referenced_nodes), 2)
        node_names = [node.name for node in referenced_nodes]
        self.assertIn("UserManager", node_names)
        self.assertIn("create_user", node_names)


class TestDescriptionNodeIntegration(unittest.TestCase):
    """Test description node creation and relationships."""
    
    def test_description_node_creation(self):
        """Test creating description nodes with proper attributes."""
        target_id = "class_123"
        description_text = "This class handles user authentication"
        llm_model = "gpt-4"
        
        desc_node = DescriptionNode(
            path="file:///test/auth.py",
            name="Description of AuthClass",
            level=2,
            description_text=description_text,
            target_node_id=target_id,
            llm_model=llm_model
        )
        
        self.assertEqual(desc_node.target_node_id, target_id)
        self.assertEqual(desc_node.description_text, description_text)
        self.assertEqual(desc_node.llm_model, llm_model)
        self.assertEqual(desc_node.label, NodeLabels.DESCRIPTION)
        
    def test_description_node_serialization(self):
        """Test serializing description node to object."""
        from blarify.graph.graph_environment import GraphEnvironment
        
        desc_node = DescriptionNode(
            path="file:///test/math.py",
            name="Description of sum_func",
            level=3,
            description_text="Calculates the sum of two numbers",
            target_node_id="func_456",
            llm_model="gpt-3.5-turbo",
            graph_environment=GraphEnvironment(environment="test", diff_identifier="test_diff", root_path="/test")
        )
        
        obj = desc_node.as_object()
        
        self.assertEqual(obj['type'], NodeLabels.DESCRIPTION.value)
        self.assertEqual(obj['attributes']['description_text'], "Calculates the sum of two numbers")
        self.assertEqual(obj['attributes']['llm_model'], "gpt-3.5-turbo")
        self.assertEqual(obj['attributes']['target_node_id'], "func_456")


if __name__ == '__main__':
    unittest.main()