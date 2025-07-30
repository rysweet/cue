"""
Tests for documentation extraction and processing.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from blarify.documentation.documentation_parser import DocumentationParser
from blarify.documentation.concept_extractor import ConceptExtractor
from blarify.documentation.documentation_linker import DocumentationLinker
from blarify.documentation.documentation_graph_generator import DocumentationGraphGenerator
from blarify.graph.graph import Graph
from blarify.graph.node.types.node_labels import NodeLabels
from tests.fixtures.graph_fixtures import create_test_graph


class TestDocumentationParser(unittest.TestCase):
    """Test documentation file parsing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DocumentationParser()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_is_documentation_file_markdown(self):
        """Test identifying markdown files as documentation."""
        test_files = [
            "README.md",
            "CHANGELOG.md",
            "docs/api.md",
            "documentation.markdown"
        ]
        
        for filename in test_files:
            with self.subTest(filename=filename):
                self.assertTrue(self.parser.is_documentation_file(filename))
                
    def test_is_documentation_file_other_formats(self):
        """Test identifying other documentation formats."""
        test_files = [
            "README.rst",
            "LICENSE.txt",
            "CONTRIBUTING.adoc",
            "docs/guide.rst"
        ]
        
        for filename in test_files:
            with self.subTest(filename=filename):
                self.assertTrue(self.parser.is_documentation_file(filename))
                
    def test_is_not_documentation_file(self):
        """Test rejecting non-documentation files."""
        test_files = [
            "main.py",
            "config.json",
            "package-lock.json",
            "test.cpp"
        ]
        
        for filename in test_files:
            with self.subTest(filename=filename):
                self.assertFalse(self.parser.is_documentation_file(filename))
                
    def test_parse_markdown_content(self):
        """Test parsing markdown content."""
        content = """# Project Title

## Overview
This is a test project.

## Features
- Feature 1
- Feature 2

### API Reference
The main API is located in `src/api.py`.
"""
        
        result = self.parser.parse_content(content, "markdown")
        
        self.assertIn("sections", result)
        self.assertIn("headers", result)
        self.assertIn("code_references", result)
        
        # Check headers were extracted
        self.assertIn("Project Title", result["headers"])
        self.assertIn("Overview", result["headers"])
        self.assertIn("Features", result["headers"])
        
        # Check code reference was found
        self.assertIn("src/api.py", result["code_references"])
        
    def test_parse_restructuredtext_content(self):
        """Test parsing reStructuredText content."""
        content = """Project Title
=============

Overview
--------
This is a test project.

.. code-block:: python

   from src.main import Application
"""
        
        result = self.parser.parse_content(content, "rst")
        
        self.assertIn("sections", result)
        self.assertIn("code_blocks", result)
        
    def test_extract_code_references(self):
        """Test extracting code references from text."""
        text = """
        The main class is defined in src/main.py.
        Helper functions are in utils/helpers.py.
        See also: tests/test_main.py for examples.
        The Application class handles requests.
        UserService manages user data.
        """
        
        refs = self.parser.extract_code_references(text)
        
        self.assertIn("src/main.py", refs)
        self.assertIn("utils/helpers.py", refs)
        self.assertIn("tests/test_main.py", refs)
        self.assertIn("Application", refs)
        self.assertIn("UserService", refs)


class TestConceptExtractor(unittest.TestCase):
    """Test concept extraction from documentation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.extractor = ConceptExtractor(llm_service=self.mock_llm)
        
    def test_extract_concepts_success(self):
        """Test successful concept extraction."""
        # Mock LLM response
        self.mock_llm.extract_concepts.return_value = {
            "concepts": [
                {
                    "name": "Microservices Architecture",
                    "description": "The system uses microservices pattern"
                },
                {
                    "name": "Repository Pattern",
                    "description": "Data access uses repository pattern"
                }
            ],
            "entities": [
                {
                    "name": "UserService",
                    "type": "service",
                    "description": "Manages user operations"
                }
            ],
            "relationships": [
                {
                    "source": "UserService",
                    "target": "Repository Pattern",
                    "type": "implements"
                }
            ],
            "code_references": [
                "src/services/user_service.py",
                "UserRepository"
            ]
        }
        
        content = "Documentation about microservices and user management..."
        result = self.extractor.extract_concepts(content, "README.md")
        
        self.assertEqual(len(result["concepts"]), 2)
        self.assertEqual(len(result["entities"]), 1)
        self.assertEqual(len(result["relationships"]), 1)
        self.assertEqual(result["concepts"][0]["name"], "Microservices Architecture")
        
    def test_extract_concepts_empty_content(self):
        """Test extraction with empty content."""
        result = self.extractor.extract_concepts("", "empty.md")
        
        self.assertEqual(result["concepts"], [])
        self.assertEqual(result["entities"], [])
        
    def test_extract_concepts_llm_error(self):
        """Test handling of LLM errors."""
        self.mock_llm.extract_concepts.side_effect = Exception("LLM Error")
        
        result = self.extractor.extract_concepts("Some content", "doc.md")
        
        # Should return empty results on error
        self.assertEqual(result["concepts"], [])
        self.assertEqual(result["entities"], [])
        
    def test_format_prompt(self):
        """Test prompt formatting for concept extraction."""
        content = "This project uses the MVC pattern..."
        
        prompt = self.extractor._format_extraction_prompt(content)
        
        self.assertIn("concepts", prompt.lower())
        self.assertIn("entities", prompt.lower())
        self.assertIn(content, prompt)


class TestDocumentationLinker(unittest.TestCase):
    """Test linking documentation to code nodes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = create_test_graph()
        self.linker = DocumentationLinker(self.graph)
        
    def test_find_code_node_by_name(self):
        """Test finding code nodes by name."""
        # The test graph has an "Application" class
        node = self.linker.find_code_node("Application")
        
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "Application")
        self.assertEqual(node.label, NodeLabels.CLASS)
        
    def test_find_code_node_by_path(self):
        """Test finding code nodes by file path."""
        # Find by relative path
        node = self.linker.find_code_node("src/main.py")
        
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "main.py")
        self.assertEqual(node.label, NodeLabels.FILE)
        
    def test_find_code_node_case_insensitive(self):
        """Test case-insensitive node matching."""
        node = self.linker.find_code_node("application")  # lowercase
        
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "Application")
        
    def test_link_documentation_to_code(self):
        """Test creating links between documentation and code."""
        from blarify.graph.node.documentation_file_node import DocumentationFileNode
        from blarify.graph.node.concept_node import ConceptNode
        
        # Add documentation nodes
        doc_node = DocumentationFileNode(
            path="file:///test/README.md",
            name="README.md",
            level=1,
            relative_path="README.md",
            format="markdown"
        )
        self.graph.add_node(doc_node)
        
        concept_node = ConceptNode(
            name="Application Architecture",
            description="Describes the Application class",
            source_file="README.md"
        )
        self.graph.add_node(concept_node)
        
        # Create links
        links_created = self.linker.link_documentation_to_code(
            doc_node,
            ["Application", "main.py"],
            [concept_node]
        )
        
        # Verify links were created
        self.assertGreater(links_created, 0)
        
        # Check relationships exist
        relationships = self.graph.get_relationships_as_objects()
        doc_relationships = [r for r in relationships 
                           if r['sourceId'] == doc_node.id or r['targetId'] == doc_node.id]
        self.assertGreater(len(doc_relationships), 0)


class TestDocumentationGraphGenerator(unittest.TestCase):
    """Test documentation graph generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_llm = Mock()
        self.generator = DocumentationGraphGenerator(
            root_path=self.temp_dir,
            llm_service=self.mock_llm
        )
        
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def create_test_docs(self):
        """Create test documentation files."""
        # Create README
        readme_path = Path(self.temp_dir) / "README.md"
        readme_path.write_text("""# Test Project

## Overview
This project implements a UserService using the Repository Pattern.

## Architecture
The application uses a microservices architecture with the following services:
- UserService: Manages user data
- AuthService: Handles authentication

See `src/services/` for implementation details.
""")
        
        # Create docs directory
        docs_dir = Path(self.temp_dir) / "docs"
        docs_dir.mkdir()
        
        # Create API docs
        api_docs = docs_dir / "api.md"
        api_docs.write_text("""# API Documentation

## UserService API
The UserService class is located in `src/services/user_service.py`.

### Methods
- `create_user()`: Creates a new user
- `get_user()`: Retrieves user by ID
""")
        
    def test_find_documentation_files(self):
        """Test finding documentation files in project."""
        self.create_test_docs()
        
        doc_files = self.generator.find_documentation_files()
        
        self.assertEqual(len(doc_files), 2)
        
        # Check file paths
        file_names = [f.name for f in doc_files]
        self.assertIn("README.md", file_names)
        self.assertIn("api.md", file_names)
        
    def test_process_documentation_file(self):
        """Test processing a single documentation file."""
        self.create_test_docs()
        
        # Mock LLM response
        self.mock_llm.extract_concepts.return_value = {
            "concepts": [
                {"name": "Repository Pattern", "description": "Data access pattern"}
            ],
            "entities": [
                {"name": "UserService", "type": "service", "description": "User management"}
            ],
            "relationships": [],
            "code_references": ["src/services/user_service.py"]
        }
        
        readme_path = Path(self.temp_dir) / "README.md"
        graph = Graph()
        
        nodes_created = self.generator.process_documentation_file(
            readme_path, graph
        )
        
        # Should create documentation file node + concepts + entities
        self.assertGreater(nodes_created, 0)
        
        # Check nodes were added
        doc_nodes = graph.get_nodes_by_label(NodeLabels.DOCUMENTATION_FILE)
        self.assertEqual(len(doc_nodes), 1)
        
        concept_nodes = graph.get_nodes_by_label(NodeLabels.CONCEPT)
        self.assertGreater(len(concept_nodes), 0)
        
    @patch('blarify.documentation.documentation_graph_generator.ProjectFilesIterator')
    def test_generate_documentation_nodes(self, mock_iterator):
        """Test generating documentation nodes for entire project."""
        self.create_test_docs()
        
        # Mock file iterator
        mock_file = Mock()
        mock_file.path = str(Path(self.temp_dir) / "README.md")
        mock_file.extension = ".md"
        mock_iterator.return_value = [mock_file]
        
        # Mock LLM
        self.mock_llm.extract_concepts.return_value = {
            "concepts": [],
            "entities": [],
            "relationships": [],
            "code_references": []
        }
        
        graph = Graph()
        self.generator.generate_documentation_nodes(graph)
        
        # Should have created documentation nodes
        doc_nodes = graph.get_nodes_by_label(NodeLabels.DOCUMENTATION_FILE)
        self.assertGreater(len(doc_nodes), 0)


if __name__ == '__main__':
    unittest.main()