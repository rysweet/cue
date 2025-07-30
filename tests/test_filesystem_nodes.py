import unittest
import tempfile
import os
import shutil
from unittest.mock import MagicMock, patch
from blarify.graph.graph import Graph
from blarify.graph.node.types.node_labels import NodeLabels
from blarify.graph.relationship.relationship_type import RelationshipType


class TestFilesystemNodes(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create test file structure
        os.makedirs(os.path.join(self.test_dir, "src", "utils"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        
        # Create test files
        self.create_file("src/main.py", """
def main():
    print("Hello World")

class Application:
    def run(self):
        pass
""")
        
        self.create_file("src/utils/helpers.py", """
def format_string(s):
    return s.strip()
""")
        
        self.create_file("tests/test_main.py", """
from src.main import main

def test_main():
    main()
""")
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def create_file(self, path, content):
        full_path = os.path.join(self.test_dir, path)
        with open(full_path, 'w') as f:
            f.write(content)
    
    def test_filesystem_node_types_exist(self):
        """Test that FILESYSTEM node type exists in NodeLabels."""
        # This should fail initially
        self.assertTrue(hasattr(NodeLabels, 'FILESYSTEM'))
        self.assertTrue(hasattr(NodeLabels, 'FILESYSTEM_FILE'))
        self.assertTrue(hasattr(NodeLabels, 'FILESYSTEM_DIRECTORY'))
    
    def test_filesystem_relationship_types_exist(self):
        """Test that filesystem relationship types exist."""
        # This should fail initially
        self.assertTrue(hasattr(RelationshipType, 'IMPLEMENTS'))
        self.assertTrue(hasattr(RelationshipType, 'DEPENDS_ON'))
        self.assertTrue(hasattr(RelationshipType, 'FILESYSTEM_CONTAINS'))
        self.assertTrue(hasattr(RelationshipType, 'REFERENCED_BY_DESCRIPTION'))
    
    def test_filesystem_node_creation(self):
        """Test that filesystem nodes can be created."""
        # This should fail initially - FilesystemFileNode doesn't exist yet
        from blarify.graph.node.filesystem_file_node import FilesystemFileNode
        
        node = FilesystemFileNode(
            path="file:///test/main.py",
            name="main.py",
            level=2,
            relative_path="src/main.py",
            size=1024,
            extension=".py",
            last_modified=1234567890
        )
        
        self.assertEqual(node.label, NodeLabels.FILESYSTEM_FILE)
        self.assertEqual(node.relative_path, "src/main.py")
        self.assertEqual(node.size, 1024)
    
    def test_filesystem_directory_node_creation(self):
        """Test that filesystem directory nodes can be created."""
        # This should fail initially - FilesystemDirectoryNode doesn't exist yet
        from blarify.graph.node.filesystem_directory_node import FilesystemDirectoryNode
        
        node = FilesystemDirectoryNode(
            path="file:///test/src",
            name="src",
            level=1,
            relative_path="src"
        )
        
        self.assertEqual(node.label, NodeLabels.FILESYSTEM_DIRECTORY)
        self.assertEqual(node.relative_path, "src")
    
    def test_filesystem_graph_generator(self):
        """Test that FilesystemGraphGenerator creates filesystem nodes."""
        # This should fail initially - FilesystemGraphGenerator doesn't exist yet
        from blarify.filesystem.filesystem_graph_generator import FilesystemGraphGenerator
        
        graph = Graph()
        generator = FilesystemGraphGenerator(root_path=self.test_dir)
        generator.generate_filesystem_nodes(graph)
        
        # Check that filesystem nodes were created
        fs_file_nodes = graph.get_nodes_by_label(NodeLabels.FILESYSTEM_FILE)
        fs_dir_nodes = graph.get_nodes_by_label(NodeLabels.FILESYSTEM_DIRECTORY)
        
        self.assertGreater(len(fs_file_nodes), 0)
        self.assertGreater(len(fs_dir_nodes), 0)
        
        # Check for specific files
        file_names = [node.name for node in fs_file_nodes]
        self.assertIn("main.py", file_names)
        self.assertIn("helpers.py", file_names)
        self.assertIn("test_main.py", file_names)
    
    def test_implements_relationships(self):
        """Test that IMPLEMENTS relationships connect filesystem to code nodes."""
        # This test will fail initially as the integration doesn't exist
        from blarify.prebuilt.graph_builder import GraphBuilder
        
        # Mock the graph builder to enable filesystem nodes
        with patch.dict(os.environ, {'ENABLE_FILESYSTEM_NODES': 'true'}):
            builder = GraphBuilder(
                root_path=self.test_dir,
                extensions_to_skip=[".pyc"],
                names_to_skip=["__pycache__"],
                enable_filesystem_nodes=True  # This parameter doesn't exist yet
            )
            
            graph = builder.build()
            
            # Get relationships
            relationships = graph.get_relationships_as_objects()
            implements_rels = [r for r in relationships if r['type'] == 'IMPLEMENTS']
            
            # Should have IMPLEMENTS relationships from filesystem files to code
            self.assertGreater(len(implements_rels), 0)
            
            # Check specific relationship exists
            # main.py should implement the main function and Application class
            main_py_nodes = [n for n in graph.get_nodes_as_objects() 
                           if n.get('attributes', {}).get('name') == 'main.py' 
                           and n['type'] == 'FILESYSTEM_FILE']
            self.assertEqual(len(main_py_nodes), 1)
    
    def test_filesystem_contains_relationships(self):
        """Test that FILESYSTEM_CONTAINS relationships connect directories to files."""
        from blarify.filesystem.filesystem_graph_generator import FilesystemGraphGenerator
        
        graph = Graph()
        generator = FilesystemGraphGenerator(root_path=self.test_dir)
        generator.generate_filesystem_nodes(graph)
        
        relationships = graph.get_relationships_as_objects()
        contains_rels = [r for r in relationships if r['type'] == 'FILESYSTEM_CONTAINS']
        
        # Should have contains relationships
        self.assertGreater(len(contains_rels), 0)
        
        # src directory should contain main.py
        src_contains_main = any(
            r for r in contains_rels 
            if 'src' in str(r.get('sourceId', '')) and 'main.py' in str(r.get('targetId', ''))
        )
        self.assertTrue(src_contains_main)
    
    def test_filesystem_node_properties(self):
        """Test that filesystem nodes have expected properties."""
        from blarify.graph.node.filesystem_file_node import FilesystemFileNode
        
        test_file = os.path.join(self.test_dir, "src/main.py")
        file_stat = os.stat(test_file)
        
        node = FilesystemFileNode(
            path=f"file://{test_file}",
            name="main.py",
            level=2,
            relative_path="src/main.py",
            size=file_stat.st_size,
            extension=".py",
            last_modified=file_stat.st_mtime
        )
        
        obj = node.as_object()
        attrs = obj['attributes']
        
        self.assertEqual(attrs['relative_path'], "src/main.py")
        self.assertEqual(attrs['extension'], ".py")
        self.assertEqual(attrs['size'], file_stat.st_size)
        self.assertIn('last_modified', attrs)
        self.assertEqual(obj['type'], 'FILESYSTEM_FILE')


if __name__ == '__main__':
    unittest.main()