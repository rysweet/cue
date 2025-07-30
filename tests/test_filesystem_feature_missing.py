"""Test that filesystem nodes feature doesn't exist yet."""
import unittest


class TestFilesystemFeatureMissing(unittest.TestCase):
    """Verify that filesystem feature components don't exist yet."""
    
    def test_filesystem_module_missing(self):
        """Test that filesystem module doesn't exist."""
        with self.assertRaises(ImportError):
            import blarify.filesystem
    
    def test_filesystem_node_classes_missing(self):
        """Test that filesystem node classes don't exist."""
        with self.assertRaises(ImportError):
            from blarify.graph.node.filesystem_file_node import FilesystemFileNode
            
        with self.assertRaises(ImportError):
            from blarify.graph.node.filesystem_directory_node import FilesystemDirectoryNode
    
    def test_filesystem_generator_missing(self):
        """Test that filesystem graph generator doesn't exist."""
        with self.assertRaises(ImportError):
            from blarify.filesystem.filesystem_graph_generator import FilesystemGraphGenerator


if __name__ == '__main__':
    unittest.main()