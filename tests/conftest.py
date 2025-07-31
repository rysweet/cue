"""
Pytest configuration and shared fixtures for the test suite.
"""
import os
import tempfile
import shutil
from unittest.mock import Mock, MagicMock
import pytest
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_project_dir(temp_dir):
    """Create a test project structure."""
    # Create directories
    src_dir = Path(temp_dir) / "src"
    src_dir.mkdir()
    
    tests_dir = Path(temp_dir) / "tests"
    tests_dir.mkdir()
    
    docs_dir = Path(temp_dir) / "docs"
    docs_dir.mkdir()
    
    # Create test files
    (src_dir / "main.py").write_text("""
def main():
    print("Hello World")

class Application:
    def run(self):
        pass
""")
    
    (src_dir / "utils.py").write_text("""
def format_string(s):
    return s.strip()
    
def calculate_sum(a, b):
    return a + b
""")
    
    (tests_dir / "test_main.py").write_text("""
from src.main import main

def test_main():
    main()
""")
    
    (Path(temp_dir) / "README.md").write_text("""
# Test Project

This is a test project for unit testing.

## Features
- Main application
- Utility functions
""")
    
    (docs_dir / "api.md").write_text("""
# API Documentation

## Application Class
The main application class.

## Utility Functions
- format_string: Formats input strings
- calculate_sum: Adds two numbers
""")
    
    return temp_dir


@pytest.fixture
def mock_graph():
    """Create a mock graph for testing."""
    from blarify.graph.graph import Graph
    graph = Graph()
    return graph


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver."""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    driver.session.return_value.__exit__.return_value = None
    return driver


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    llm_service = Mock()
    llm_service.generate_description.return_value = "Test description"
    llm_service.extract_concepts.return_value = {
        "concepts": [
            {"name": "Test Concept", "description": "A test concept"}
        ],
        "entities": [
            {"name": "TestEntity", "type": "class"}
        ],
        "relationships": [],
        "code_references": []
    }
    return llm_service


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    # Mock Azure OpenAI configuration to prevent errors
    monkeypatch.setenv("AZURE_OPENAI_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_MODEL_CHAT", "gpt-4")
    
    # Set test database configuration
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")
    monkeypatch.setenv("NEO4J_DATABASE", "test")


@pytest.fixture
def sample_file_node():
    """Create a sample file node for testing."""
    from blarify.graph.node.file_node import FileNode
    return FileNode(
        path="file:///test/main.py",
        name="main.py",
        level=1
    )


@pytest.fixture
def sample_class_node():
    """Create a sample class node for testing."""
    from blarify.graph.node.class_node import ClassNode
    return ClassNode(
        id="test_class_123",
        name="TestClass",
        path="file:///test/main.py",
        level=2,
        start_line=10,
        end_line=20
    )


@pytest.fixture
def sample_function_node():
    """Create a sample function node for testing."""
    from blarify.graph.node.function_node import FunctionNode
    return FunctionNode(
        id="test_func_456",
        name="test_function",
        path="file:///test/main.py",
        level=2,
        start_line=25,
        end_line=30
    )