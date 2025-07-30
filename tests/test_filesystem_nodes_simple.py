import unittest
from blarify.graph.node.types.node_labels import NodeLabels
from blarify.graph.relationship.relationship_type import RelationshipType


class TestFilesystemNodeTypes(unittest.TestCase):
    """Test that filesystem node and relationship types exist."""
    
    def test_filesystem_node_types_exist(self):
        """Test that FILESYSTEM node types exist in NodeLabels."""
        # These tests should fail initially since these types don't exist yet
        with self.assertRaises(AttributeError):
            _ = NodeLabels.FILESYSTEM
        
        with self.assertRaises(AttributeError):
            _ = NodeLabels.FILESYSTEM_FILE
            
        with self.assertRaises(AttributeError):
            _ = NodeLabels.FILESYSTEM_DIRECTORY
    
    def test_filesystem_relationship_types_exist(self):
        """Test that filesystem relationship types exist."""
        # These tests should fail initially since these types don't exist yet
        with self.assertRaises(AttributeError):
            _ = RelationshipType.IMPLEMENTS
            
        with self.assertRaises(AttributeError):
            _ = RelationshipType.DEPENDS_ON
            
        with self.assertRaises(AttributeError):
            _ = RelationshipType.FILESYSTEM_CONTAINS
            
        with self.assertRaises(AttributeError):
            _ = RelationshipType.REFERENCED_BY_DESCRIPTION


if __name__ == '__main__':
    unittest.main()