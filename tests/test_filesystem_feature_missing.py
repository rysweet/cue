"""Test that filesystem nodes feature exists and works correctly."""
import unittest
from cue.graph.node.filesystem_file_node import FilesystemFileNode
from cue.graph.node.filesystem_directory_node import FilesystemDirectoryNode
from cue.filesystem.filesystem_graph_generator import FilesystemGraphGenerator


class TestFilesystemFeatureExists(unittest.TestCase):
    """Verify that filesystem feature components exist and can be imported."""
    
    def test_filesystem_module_exists(self):
        """Test that filesystem module exists."""
        import cue.filesystem
        self.assertIsNotNone(cue.filesystem)
    
    def test_filesystem_node_classes_exist(self):
        """Test that filesystem node classes exist."""
        # These imports would have raised ImportError if they didn't exist
        self.assertIsNotNone(FilesystemFileNode)
        self.assertIsNotNone(FilesystemDirectoryNode)
    
    def test_filesystem_generator_exists(self):
        """Test that filesystem graph generator exists."""
        # This import would have raised ImportError if it didn't exist
        self.assertIsNotNone(FilesystemGraphGenerator)


if __name__ == '__main__':
    unittest.main()