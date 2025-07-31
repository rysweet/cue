import unittest
from unittest.mock import MagicMock, patch
from blarify.graph.graph import Graph
from blarify.graph.node import Node, NodeLabels, FileNode
from blarify.graph.relationship import Relationship, RelationshipType


class TestGraphComprehensive(unittest.TestCase):
    """Comprehensive test cases for Graph class to improve coverage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = Graph()
        
    def test_has_folder_node_with_path(self):
        """Test checking if folder node exists with path."""
        # Initially no folder nodes
        self.assertFalse(self.graph.has_folder_node_with_path("/test/folder"))
        
        # Add a folder node
        mock_folder = MagicMock(spec=Node)
        mock_folder.id = "folder1"
        mock_folder.path = "/test/folder"
        mock_folder.label = NodeLabels.FOLDER
        mock_folder.relative_id = "folder1"
        
        self.graph.add_node(mock_folder)
        
        self.assertTrue(self.graph.has_folder_node_with_path("/test/folder"))
        self.assertFalse(self.graph.has_folder_node_with_path("/other/folder"))
        
    def test_add_nodes(self):
        """Test adding multiple nodes at once."""
        nodes = []
        for i in range(3):
            mock_node = MagicMock(spec=Node)
            mock_node.id = f"node{i}"
            mock_node.path = f"/test/file{i}.py"
            mock_node.label = NodeLabels.CLASS
            mock_node.relative_id = f"node{i}"
            nodes.append(mock_node)
            
        self.graph.add_nodes(nodes)
        
        # Verify all nodes were added
        for i in range(3):
            self.assertIsNotNone(self.graph.get_node_by_id(f"node{i}"))
            
    def test_get_file_node_by_path_none(self):
        """Test getting file node when it doesn't exist."""
        result = self.graph.get_file_node_by_path("/nonexistent/file.py")
        self.assertIsNone(result)
        
    def test_get_file_node_by_path_exists(self):
        """Test getting file node when it exists."""
        mock_file = MagicMock(spec=FileNode)
        mock_file.id = "file1"
        mock_file.path = "/test/file.py"
        mock_file.label = NodeLabels.FILE
        mock_file.relative_id = "file1"
        
        self.graph.add_node(mock_file)
        
        result = self.graph.get_file_node_by_path("/test/file.py")
        self.assertEqual(result, mock_file)
        
    def test_get_folder_node_by_path(self):
        """Test getting folder node by path."""
        mock_folder = MagicMock(spec=Node)
        mock_folder.id = "folder1"
        mock_folder.path = "/test/folder"
        mock_folder.label = NodeLabels.FOLDER
        mock_folder.relative_id = "folder1"
        
        self.graph.add_node(mock_folder)
        
        result = self.graph.get_folder_node_by_path("/test/folder")
        self.assertEqual(result, mock_folder)
        
    def test_get_node_by_relative_id_none(self):
        """Test getting node by relative ID when it doesn't exist."""
        result = self.graph.get_node_by_relative_id("nonexistent")
        self.assertIsNone(result)
        
    def test_get_node_by_relative_id_exists(self):
        """Test getting node by relative ID when it exists."""
        mock_node = MagicMock(spec=Node)
        mock_node.id = "node1"
        mock_node.path = "/test/file.py"
        mock_node.label = NodeLabels.CLASS
        mock_node.relative_id = "MyClass"
        
        self.graph.add_node(mock_node)
        
        result = self.graph.get_node_by_relative_id("MyClass")
        self.assertEqual(result, mock_node)
        
    def test_get_relationships_as_objects(self):
        """Test getting relationships as objects."""
        # Add nodes with relationships
        mock_node1 = MagicMock(spec=Node)
        mock_node1.id = "node1"
        mock_node1.path = "/test/file1.py"
        mock_node1.label = NodeLabels.CLASS
        mock_node1.relative_id = "node1"
        
        mock_node2 = MagicMock(spec=Node)
        mock_node2.id = "node2"
        mock_node2.path = "/test/file2.py"
        mock_node2.label = NodeLabels.CLASS
        mock_node2.relative_id = "node2"
        
        # Mock internal relationship
        mock_rel1 = MagicMock(spec=Relationship)
        mock_rel1.as_object.return_value = {"type": "DEFINES", "start": "node1", "end": "node2"}
        mock_node1.get_relationships.return_value = [mock_rel1]
        mock_node2.get_relationships.return_value = []
        
        self.graph.add_node(mock_node1)
        self.graph.add_node(mock_node2)
        
        # Add reference relationship
        mock_ref_rel = MagicMock(spec=Relationship)
        mock_ref_rel.as_object.return_value = {"type": "USES", "start": "node2", "end": "node1"}
        self.graph.add_references_relationships([mock_ref_rel])
        
        relationships = self.graph.get_relationships_as_objects()
        
        self.assertEqual(len(relationships), 2)
        self.assertIn({"type": "DEFINES", "start": "node1", "end": "node2"}, relationships)
        self.assertIn({"type": "USES", "start": "node2", "end": "node1"}, relationships)
        
    def test_get_relationships_from_nodes(self):
        """Test getting relationships from nodes."""
        mock_node1 = MagicMock(spec=Node)
        mock_node1.id = "node1"
        mock_node1.path = "/test/file.py"
        mock_node1.label = NodeLabels.CLASS
        mock_node1.relative_id = "node1"
        
        mock_rel1 = MagicMock(spec=Relationship)
        mock_rel2 = MagicMock(spec=Relationship)
        mock_node1.get_relationships.return_value = [mock_rel1, mock_rel2]
        
        self.graph.add_node(mock_node1)
        
        relationships = self.graph.get_relationships_from_nodes()
        
        self.assertEqual(len(relationships), 2)
        self.assertIn(mock_rel1, relationships)
        self.assertIn(mock_rel2, relationships)
        
    def test_get_all_relationships(self):
        """Test getting all relationships (nodes + references)."""
        # Add node with relationship
        mock_node = MagicMock(spec=Node)
        mock_node.id = "node1"
        mock_node.path = "/test/file.py"
        mock_node.label = NodeLabels.CLASS
        mock_node.relative_id = "node1"
        
        mock_node_rel = MagicMock(spec=Relationship)
        mock_node.get_relationships.return_value = [mock_node_rel]
        
        self.graph.add_node(mock_node)
        
        # Add reference relationship
        mock_ref_rel = MagicMock(spec=Relationship)
        self.graph.add_references_relationships([mock_ref_rel])
        
        all_relationships = self.graph.get_all_relationships()
        
        self.assertEqual(len(all_relationships), 2)
        self.assertIn(mock_node_rel, all_relationships)
        self.assertIn(mock_ref_rel, all_relationships)
        
    def test_get_nodes_as_objects(self):
        """Test getting nodes as objects."""
        mock_node1 = MagicMock(spec=Node)
        mock_node1.id = "node1"
        mock_node1.path = "/test/file1.py"
        mock_node1.label = NodeLabels.CLASS
        mock_node1.relative_id = "node1"
        mock_node1.as_object.return_value = {"id": "node1", "type": "CLASS"}
        
        mock_node2 = MagicMock(spec=Node)
        mock_node2.id = "node2"
        mock_node2.path = "/test/file2.py"
        mock_node2.label = NodeLabels.FUNCTION
        mock_node2.relative_id = "node2"
        mock_node2.as_object.return_value = {"id": "node2", "type": "FUNCTION"}
        
        self.graph.add_node(mock_node1)
        self.graph.add_node(mock_node2)
        
        objects = self.graph.get_nodes_as_objects()
        
        self.assertEqual(len(objects), 2)
        self.assertIn({"id": "node1", "type": "CLASS"}, objects)
        self.assertIn({"id": "node2", "type": "FUNCTION"}, objects)
        
    def test_filtered_graph_by_paths(self):
        """Test filtering graph by paths."""
        # Create nodes
        nodes = []
        for i in range(4):
            mock_node = MagicMock(spec=Node)
            mock_node.id = f"node{i}"
            mock_node.path = f"/test/file{i}.py"
            mock_node.label = NodeLabels.CLASS
            mock_node.relative_id = f"node{i}"
            mock_node.filter_children_by_path = MagicMock()
            nodes.append(mock_node)
            self.graph.add_node(mock_node)
            
        # Create relationships
        mock_rel1 = MagicMock(spec=Relationship)
        mock_rel1.start_node = nodes[0]
        mock_rel1.end_node = nodes[1]
        
        mock_rel2 = MagicMock(spec=Relationship)
        mock_rel2.start_node = nodes[2]
        mock_rel2.end_node = nodes[3]
        
        self.graph.add_references_relationships([mock_rel1, mock_rel2])
        
        # Filter by paths
        paths_to_keep = ["/test/file0.py", "/test/file1.py"]
        filtered_graph = self.graph.filtered_graph_by_paths(paths_to_keep)
        
        # Verify filtered graph
        self.assertIsNotNone(filtered_graph.get_node_by_id("node0"))
        self.assertIsNotNone(filtered_graph.get_node_by_id("node1"))
        self.assertIsNone(filtered_graph.get_node_by_id("node2"))
        self.assertIsNone(filtered_graph.get_node_by_id("node3"))
        
        # Verify filter_children_by_path was called
        nodes[0].filter_children_by_path.assert_called_once_with(paths_to_keep)
        nodes[1].filter_children_by_path.assert_called_once_with(paths_to_keep)
        
        # Verify only relevant relationships are kept
        filtered_relationships = filtered_graph.get_all_relationships()
        self.assertEqual(len(filtered_relationships), 1)
        
    def test_filtered_graph_by_paths_with_cross_references(self):
        """Test filtering graph with cross-file references."""
        # Create nodes
        node1 = MagicMock(spec=Node)
        node1.id = "node1"
        node1.path = "/keep/file1.py"
        node1.label = NodeLabels.CLASS
        node1.relative_id = "node1"
        node1.filter_children_by_path = MagicMock()
        
        node2 = MagicMock(spec=Node)
        node2.id = "node2"
        node2.path = "/remove/file2.py"
        node2.label = NodeLabels.CLASS
        node2.relative_id = "node2"
        node2.filter_children_by_path = MagicMock()
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        # Create relationship from removed node to kept node
        mock_rel = MagicMock(spec=Relationship)
        mock_rel.start_node = node2  # This node will be filtered out
        mock_rel.end_node = node1    # This node will be kept
        
        self.graph.add_references_relationships([mock_rel])
        
        # Filter by paths
        paths_to_keep = ["/keep/file1.py"]
        filtered_graph = self.graph.filtered_graph_by_paths(paths_to_keep)
        
        # Verify the relationship is still kept because end_node is in paths_to_keep
        filtered_relationships = filtered_graph.get_all_relationships()
        self.assertEqual(len(filtered_relationships), 1)
        
    def test_str_representation(self):
        """Test string representation of graph."""
        # Add nodes
        mock_node1 = MagicMock(spec=Node)
        mock_node1.id = "node1"
        mock_node1.path = "/test/file1.py"
        mock_node1.label = NodeLabels.CLASS
        mock_node1.relative_id = "node1"
        mock_node1.__str__.return_value = "Node1: Class"
        
        mock_node2 = MagicMock(spec=Node)
        mock_node2.id = "node2"
        mock_node2.path = "/test/file2.py"
        mock_node2.label = NodeLabels.FUNCTION
        mock_node2.relative_id = "node2"
        mock_node2.__str__.return_value = "Node2: Function"
        
        self.graph.add_node(mock_node1)
        self.graph.add_node(mock_node2)
        
        # Add reference relationship
        mock_rel = MagicMock(spec=Relationship)
        mock_rel.__str__.return_value = "Relationship: Node1 -> Node2"
        self.graph.add_references_relationships([mock_rel])
        
        graph_str = str(self.graph)
        
        self.assertIn("Node1: Class", graph_str)
        self.assertIn("Node2: Function", graph_str)
        self.assertIn("Relationship: Node1 -> Node2", graph_str)
        
    def test_empty_graph_operations(self):
        """Test operations on empty graph."""
        # Test getting from empty graph
        self.assertEqual(len(self.graph.get_nodes_by_path("/any/path")), 0)
        self.assertEqual(len(self.graph.get_nodes_by_label(NodeLabels.CLASS)), 0)
        self.assertIsNone(self.graph.get_node_by_id("any_id"))
        self.assertIsNone(self.graph.get_node_by_relative_id("any_relative_id"))
        self.assertIsNone(self.graph.get_file_node_by_path("/any/file.py"))
        
        # Test getting relationships from empty graph
        self.assertEqual(len(self.graph.get_relationships_from_nodes()), 0)
        self.assertEqual(len(self.graph.get_all_relationships()), 0)
        self.assertEqual(len(self.graph.get_relationships_as_objects()), 0)
        
        # Test string representation of empty graph
        self.assertEqual(str(self.graph), "")
        
    def test_get_all_nodes(self):
        """Test getting all nodes from graph."""
        nodes = []
        for i in range(3):
            mock_node = MagicMock(spec=Node)
            mock_node.id = f"node{i}"
            mock_node.path = f"/test/file{i}.py"
            mock_node.label = NodeLabels.CLASS
            mock_node.relative_id = f"node{i}"
            nodes.append(mock_node)
            self.graph.add_node(mock_node)
            
        all_nodes = self.graph.get_all_nodes()
        
        self.assertEqual(len(all_nodes), 3)
        for node in nodes:
            self.assertIn(node, all_nodes)


if __name__ == '__main__':
    unittest.main()