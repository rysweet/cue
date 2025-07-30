"""
Comprehensive tests for graph operations.
"""
import unittest
from unittest.mock import Mock, patch
from blarify.graph.graph import Graph
from blarify.graph.node.file_node import FileNode
from blarify.graph.node.class_node import ClassNode
from blarify.graph.node.function_node import FunctionNode
from blarify.graph.relationship.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType
from blarify.graph.node.types.node_labels import NodeLabels
from tests.fixtures.graph_fixtures import create_test_graph
from tests.fixtures.node_factories import (
    create_file_node, create_class_node, create_function_node
)


class TestGraphOperations(unittest.TestCase):
    """Test suite for core graph operations."""
    
    def setUp(self):
        """Set up test graph instance."""
        self.graph = Graph()
        
    def test_add_node_success(self):
        """Test adding a node to the graph."""
        node = create_file_node("main.py")
        
        self.graph.add_node(node)
        
        # Verify node was added
        self.assertIn(node.id, self.graph.nodes)
        self.assertEqual(self.graph.nodes[node.id], node)
        
    def test_add_duplicate_node(self):
        """Test that duplicate nodes are handled correctly."""
        node1 = create_file_node("main.py", "file:///test/main.py")
        node2 = create_file_node("main.py", "file:///test/main.py")
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        # Should only have one node
        self.assertEqual(len(self.graph.nodes), 1)
        
    def test_get_node_by_id(self):
        """Test retrieving a node by ID."""
        node = create_class_node("TestClass")
        self.graph.add_node(node)
        
        retrieved = self.graph.get_node_by_id(node.id)
        
        self.assertEqual(retrieved, node)
        self.assertEqual(retrieved.name, "TestClass")
        
    def test_get_node_by_id_not_found(self):
        """Test retrieving non-existent node returns None."""
        result = self.graph.get_node_by_id("non_existent_id")
        self.assertIsNone(result)
        
    def test_get_nodes_by_label(self):
        """Test retrieving nodes by label."""
        file1 = create_file_node("main.py")
        file2 = create_file_node("utils.py")
        class1 = create_class_node("TestClass")
        
        self.graph.add_node(file1)
        self.graph.add_node(file2)
        self.graph.add_node(class1)
        
        file_nodes = self.graph.get_nodes_by_label(NodeLabels.FILE)
        class_nodes = self.graph.get_nodes_by_label(NodeLabels.CLASS)
        
        self.assertEqual(len(file_nodes), 2)
        self.assertEqual(len(class_nodes), 1)
        self.assertIn(file1, file_nodes)
        self.assertIn(file2, file_nodes)
        self.assertIn(class1, class_nodes)
        
    def test_add_relationship_success(self):
        """Test adding a relationship between nodes."""
        file_node = create_file_node("main.py")
        class_node = create_class_node("TestClass", file_node.path)
        
        self.graph.add_node(file_node)
        self.graph.add_node(class_node)
        
        rel = Relationship(
            source_id=file_node.id,
            target_id=class_node.id,
            type=RelationshipType.CONTAINS
        )
        self.graph.add_relationship(rel)
        
        # Verify relationship was added
        relationships = self.graph.get_relationships_as_objects()
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]['sourceId'], file_node.id)
        self.assertEqual(relationships[0]['targetId'], class_node.id)
        self.assertEqual(relationships[0]['type'], RelationshipType.CONTAINS.value)
        
    def test_add_relationship_missing_nodes(self):
        """Test adding relationship with missing nodes raises error."""
        rel = Relationship(
            source_id="missing_source",
            target_id="missing_target",
            type=RelationshipType.CONTAINS
        )
        
        with self.assertRaises(ValueError):
            self.graph.add_relationship(rel)
            
    def test_get_relationships_by_node(self):
        """Test retrieving relationships for a specific node."""
        file_node = create_file_node("main.py")
        class1 = create_class_node("Class1", file_node.path)
        class2 = create_class_node("Class2", file_node.path)
        func1 = create_function_node("func1", file_node.path)
        
        self.graph.add_node(file_node)
        self.graph.add_node(class1)
        self.graph.add_node(class2)
        self.graph.add_node(func1)
        
        # Add relationships
        self.graph.add_relationship(Relationship(
            source_id=file_node.id,
            target_id=class1.id,
            type=RelationshipType.CONTAINS
        ))
        self.graph.add_relationship(Relationship(
            source_id=file_node.id,
            target_id=class2.id,
            type=RelationshipType.CONTAINS
        ))
        self.graph.add_relationship(Relationship(
            source_id=file_node.id,
            target_id=func1.id,
            type=RelationshipType.CONTAINS
        ))
        
        # Get outgoing relationships from file node
        outgoing = self.graph.get_relationships_by_node(file_node.id, direction="outgoing")
        self.assertEqual(len(outgoing), 3)
        
        # Get incoming relationships to class1
        incoming = self.graph.get_relationships_by_node(class1.id, direction="incoming")
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0].source_id, file_node.id)
        
    def test_get_nodes_as_objects(self):
        """Test serializing nodes to dictionary objects."""
        file_node = create_file_node("main.py")
        class_node = create_class_node("TestClass")
        
        self.graph.add_node(file_node)
        self.graph.add_node(class_node)
        
        objects = self.graph.get_nodes_as_objects()
        
        self.assertEqual(len(objects), 2)
        
        # Check file node object
        file_obj = next(obj for obj in objects if obj['type'] == NodeLabels.FILE.value)
        self.assertEqual(file_obj['attributes']['name'], "main.py")
        self.assertEqual(file_obj['attributes']['path'], file_node.path)
        
        # Check class node object
        class_obj = next(obj for obj in objects if obj['type'] == NodeLabels.CLASS.value)
        self.assertEqual(class_obj['attributes']['name'], "TestClass")
        
    def test_clear_graph(self):
        """Test clearing all nodes and relationships from graph."""
        # Add some nodes and relationships
        graph = create_test_graph()
        
        # Verify graph has content
        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.get_relationships_as_objects()), 0)
        
        # Clear the graph
        graph.clear()
        
        # Verify graph is empty
        self.assertEqual(len(graph.nodes), 0)
        self.assertEqual(len(graph.get_relationships_as_objects()), 0)
        
    def test_node_exists(self):
        """Test checking if a node exists in the graph."""
        node = create_function_node("test_func")
        
        self.assertFalse(self.graph.node_exists(node.id))
        
        self.graph.add_node(node)
        
        self.assertTrue(self.graph.node_exists(node.id))
        
    def test_remove_node(self):
        """Test removing a node from the graph."""
        node = create_file_node("temp.py")
        class_node = create_class_node("TempClass", node.path)
        
        self.graph.add_node(node)
        self.graph.add_node(class_node)
        self.graph.add_relationship(Relationship(
            source_id=node.id,
            target_id=class_node.id,
            type=RelationshipType.CONTAINS
        ))
        
        # Remove the file node
        self.graph.remove_node(node.id)
        
        # Verify node is removed
        self.assertFalse(self.graph.node_exists(node.id))
        self.assertTrue(self.graph.node_exists(class_node.id))
        
        # Verify relationships involving the node are also removed
        relationships = self.graph.get_relationships_as_objects()
        self.assertEqual(len(relationships), 0)
        
    def test_get_connected_nodes(self):
        """Test getting nodes connected to a specific node."""
        # Create a small graph
        file1 = create_file_node("main.py")
        file2 = create_file_node("utils.py")
        class1 = create_class_node("MainClass", file1.path)
        func1 = create_function_node("helper", file2.path)
        
        self.graph.add_node(file1)
        self.graph.add_node(file2)
        self.graph.add_node(class1)
        self.graph.add_node(func1)
        
        # file1 contains class1
        self.graph.add_relationship(Relationship(
            source_id=file1.id,
            target_id=class1.id,
            type=RelationshipType.CONTAINS
        ))
        
        # file2 contains func1
        self.graph.add_relationship(Relationship(
            source_id=file2.id,
            target_id=func1.id,
            type=RelationshipType.CONTAINS
        ))
        
        # class1 uses func1
        self.graph.add_relationship(Relationship(
            source_id=class1.id,
            target_id=func1.id,
            type=RelationshipType.USES
        ))
        
        # Get nodes connected to class1
        connected = self.graph.get_connected_nodes(class1.id)
        
        # Should include file1 (incoming) and func1 (outgoing)
        connected_ids = [n.id for n in connected]
        self.assertIn(file1.id, connected_ids)
        self.assertIn(func1.id, connected_ids)
        self.assertNotIn(file2.id, connected_ids)
        
    def test_get_subgraph(self):
        """Test extracting a subgraph around specific nodes."""
        # Use the test graph fixture
        graph = create_test_graph()
        
        # Get a specific node
        nodes = graph.get_nodes_by_label(NodeLabels.CLASS)
        self.assertGreater(len(nodes), 0)
        class_node = nodes[0]
        
        # Extract subgraph around the class node
        subgraph = graph.get_subgraph([class_node.id], max_depth=1)
        
        # Verify subgraph contains the class node
        self.assertTrue(subgraph.node_exists(class_node.id))
        
        # Verify subgraph has fewer nodes than original
        self.assertLess(len(subgraph.nodes), len(graph.nodes))
        
    def test_merge_graphs(self):
        """Test merging two graphs together."""
        graph1 = Graph()
        graph2 = Graph()
        
        # Add nodes to graph1
        file1 = create_file_node("file1.py")
        class1 = create_class_node("Class1", file1.path)
        graph1.add_node(file1)
        graph1.add_node(class1)
        
        # Add nodes to graph2
        file2 = create_file_node("file2.py")
        func2 = create_function_node("func2", file2.path)
        graph2.add_node(file2)
        graph2.add_node(func2)
        
        # Merge graph2 into graph1
        graph1.merge(graph2)
        
        # Verify all nodes are in graph1
        self.assertEqual(len(graph1.nodes), 4)
        self.assertTrue(graph1.node_exists(file1.id))
        self.assertTrue(graph1.node_exists(class1.id))
        self.assertTrue(graph1.node_exists(file2.id))
        self.assertTrue(graph1.node_exists(func2.id))


if __name__ == '__main__':
    unittest.main()