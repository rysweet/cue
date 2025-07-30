"""
Simple tests for graph operations that work with current structure.
"""
import unittest
from unittest.mock import Mock, MagicMock
from blarify.graph.graph import Graph
from blarify.graph.node.types.node import Node
from blarify.graph.node.types.node_labels import NodeLabels
from blarify.graph.relationship.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType


class TestGraphSimple(unittest.TestCase):
    """Simple test suite for graph operations."""
    
    def setUp(self):
        """Set up test graph instance."""
        self.graph = Graph()
        
    def test_graph_creation(self):
        """Test creating an empty graph."""
        self.assertIsInstance(self.graph, Graph)
        self.assertEqual(len(self.graph.nodes), 0)
        
    def test_add_simple_node(self):
        """Test adding a simple node to graph."""
        # Create a basic node
        node = Node(
            label=NodeLabels.FILE,
            path="file:///test/main.py",
            name="main.py",
            level=1
        )
        
        # Add to graph
        self.graph.add_node(node)
        
        # Verify it was added
        self.assertIn(node.id, self.graph.nodes)
        self.assertEqual(self.graph.nodes[node.id], node)
        
    def test_get_node_by_id(self):
        """Test retrieving node by ID."""
        node = Node(
            label=NodeLabels.FOLDER,
            path="file:///test/src",
            name="src",
            level=0
        )
        self.graph.add_node(node)
        
        retrieved = self.graph.get_node_by_id(node.id)
        
        self.assertEqual(retrieved, node)
        self.assertEqual(retrieved.name, "src")
        
    def test_get_nodes_by_label(self):
        """Test retrieving nodes by label."""
        # Add different types of nodes
        file_node = Node(
            label=NodeLabels.FILE,
            path="file:///test/main.py",
            name="main.py",
            level=1
        )
        folder_node = Node(
            label=NodeLabels.FOLDER,
            path="file:///test/src",
            name="src",
            level=0
        )
        
        self.graph.add_node(file_node)
        self.graph.add_node(folder_node)
        
        # Get nodes by label
        file_nodes = self.graph.get_nodes_by_label(NodeLabels.FILE)
        folder_nodes = self.graph.get_nodes_by_label(NodeLabels.FOLDER)
        
        self.assertEqual(len(file_nodes), 1)
        self.assertEqual(len(folder_nodes), 1)
        self.assertIn(file_node, file_nodes)
        self.assertIn(folder_node, folder_nodes)
        
    def test_add_relationship(self):
        """Test adding relationships between nodes."""
        # Create two nodes
        parent = Node(
            label=NodeLabels.FOLDER,
            path="file:///test/src",
            name="src",
            level=0
        )
        child = Node(
            label=NodeLabels.FILE,
            path="file:///test/src/main.py",
            name="main.py",
            level=1
        )
        
        self.graph.add_node(parent)
        self.graph.add_node(child)
        
        # Add relationship
        rel = Relationship(
            source_id=parent.id,
            target_id=child.id,
            type=RelationshipType.CONTAINS
        )
        self.graph.add_relationship(rel)
        
        # Verify relationship exists
        relationships = self.graph.get_relationships_as_objects()
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]['sourceId'], parent.id)
        self.assertEqual(relationships[0]['targetId'], child.id)
        
    def test_get_nodes_as_objects(self):
        """Test serializing nodes to dictionaries."""
        node = Node(
            label=NodeLabels.FILE,
            path="file:///test/utils.py",
            name="utils.py",
            level=1
        )
        self.graph.add_node(node)
        
        objects = self.graph.get_nodes_as_objects()
        
        self.assertEqual(len(objects), 1)
        obj = objects[0]
        
        self.assertIn('id', obj)
        self.assertIn('type', obj)
        self.assertIn('attributes', obj)
        self.assertEqual(obj['type'], NodeLabels.FILE.value)
        self.assertEqual(obj['attributes']['name'], 'utils.py')


class TestNodeLabels(unittest.TestCase):
    """Test node label types."""
    
    def test_node_labels_exist(self):
        """Test that expected node labels exist."""
        # Basic labels
        self.assertTrue(hasattr(NodeLabels, 'FILE'))
        self.assertTrue(hasattr(NodeLabels, 'FOLDER'))
        self.assertTrue(hasattr(NodeLabels, 'CLASS'))
        self.assertTrue(hasattr(NodeLabels, 'FUNCTION'))
        
        # Filesystem labels
        self.assertTrue(hasattr(NodeLabels, 'FILESYSTEM'))
        self.assertTrue(hasattr(NodeLabels, 'FILESYSTEM_FILE'))
        self.assertTrue(hasattr(NodeLabels, 'FILESYSTEM_DIRECTORY'))
        
        # Documentation labels
        self.assertTrue(hasattr(NodeLabels, 'DOCUMENTATION_FILE'))
        self.assertTrue(hasattr(NodeLabels, 'CONCEPT'))
        self.assertTrue(hasattr(NodeLabels, 'DOCUMENTED_ENTITY'))
        
        # Description label
        self.assertTrue(hasattr(NodeLabels, 'DESCRIPTION'))


class TestRelationshipTypes(unittest.TestCase):
    """Test relationship types."""
    
    def test_relationship_types_exist(self):
        """Test that expected relationship types exist."""
        # Basic relationships
        self.assertTrue(hasattr(RelationshipType, 'CONTAINS'))
        self.assertTrue(hasattr(RelationshipType, 'IMPORTS'))
        self.assertTrue(hasattr(RelationshipType, 'USES'))
        
        # Filesystem relationships
        self.assertTrue(hasattr(RelationshipType, 'FILESYSTEM_CONTAINS'))
        self.assertTrue(hasattr(RelationshipType, 'IMPLEMENTS'))
        
        # Documentation relationships
        self.assertTrue(hasattr(RelationshipType, 'CONTAINS_CONCEPT'))
        self.assertTrue(hasattr(RelationshipType, 'DESCRIBES_ENTITY'))
        self.assertTrue(hasattr(RelationshipType, 'DOCUMENTS'))
        
        # Description relationships
        self.assertTrue(hasattr(RelationshipType, 'DESCRIBES'))
        self.assertTrue(hasattr(RelationshipType, 'REFERENCED_BY_DESCRIPTION'))


if __name__ == '__main__':
    unittest.main()