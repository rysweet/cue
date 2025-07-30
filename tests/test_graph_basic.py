"""
Basic tests for graph functionality that work with current codebase structure.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from blarify.graph.graph import Graph
from blarify.graph.relationship.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType
from blarify.graph.node.types.node_labels import NodeLabels


class TestGraphBasic(unittest.TestCase):
    """Basic tests for Graph class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = Graph()
        
    def test_graph_initialization(self):
        """Test graph is initialized empty."""
        self.assertEqual(len(self.graph.nodes), 0)
        self.assertIsInstance(self.graph.nodes, dict)
        
    def test_node_exists(self):
        """Test checking if node exists."""
        # Mock node with required properties
        mock_node = Mock()
        mock_node.id = "test_node_123"
        mock_node.label = NodeLabels.DESCRIPTION
        mock_node.name = "Test Node"
        
        # Initially should not exist
        self.assertFalse(self.graph.node_exists("test_node_123"))
        
        # Add node
        self.graph.nodes["test_node_123"] = mock_node
        
        # Now should exist
        self.assertTrue(self.graph.node_exists("test_node_123"))
        
    def test_get_node_by_id(self):
        """Test retrieving node by ID."""
        mock_node = Mock()
        mock_node.id = "test_node_456"
        mock_node.label = NodeLabels.DESCRIPTION
        
        # Add to graph
        self.graph.nodes["test_node_456"] = mock_node
        
        # Retrieve
        retrieved = self.graph.get_node_by_id("test_node_456")
        self.assertEqual(retrieved, mock_node)
        
        # Non-existent node
        self.assertIsNone(self.graph.get_node_by_id("non_existent"))
        
    def test_get_nodes_by_label(self):
        """Test filtering nodes by label."""
        # Create mock nodes with different labels
        desc_node1 = Mock()
        desc_node1.id = "desc1"
        desc_node1.label = NodeLabels.DESCRIPTION
        
        desc_node2 = Mock()
        desc_node2.id = "desc2"
        desc_node2.label = NodeLabels.DESCRIPTION
        
        concept_node = Mock()
        concept_node.id = "concept1"
        concept_node.label = NodeLabels.CONCEPT
        
        # Add to graph
        self.graph.nodes = {
            "desc1": desc_node1,
            "desc2": desc_node2,
            "concept1": concept_node
        }
        
        # Filter by label
        desc_nodes = self.graph.get_nodes_by_label(NodeLabels.DESCRIPTION)
        self.assertEqual(len(desc_nodes), 2)
        self.assertIn(desc_node1, desc_nodes)
        self.assertIn(desc_node2, desc_nodes)
        
        concept_nodes = self.graph.get_nodes_by_label(NodeLabels.CONCEPT)
        self.assertEqual(len(concept_nodes), 1)
        self.assertIn(concept_node, concept_nodes)
        
    def test_add_relationship_validation(self):
        """Test relationship validation."""
        # Create mock nodes
        node1 = Mock()
        node1.id = "node1"
        node2 = Mock()
        node2.id = "node2"
        
        self.graph.nodes = {"node1": node1, "node2": node2}
        
        # Valid relationship
        rel = Relationship(
            source_id="node1",
            target_id="node2",
            type=RelationshipType.CONTAINS
        )
        
        # Should not raise exception
        self.graph.add_relationship(rel)
        
        # Invalid relationship (missing target)
        bad_rel = Relationship(
            source_id="node1",
            target_id="missing_node",
            type=RelationshipType.CONTAINS
        )
        
        with self.assertRaises(ValueError):
            self.graph.add_relationship(bad_rel)
            
    def test_get_relationships_as_objects(self):
        """Test serializing relationships."""
        # Create nodes
        node1 = Mock()
        node1.id = "src"
        node2 = Mock()
        node2.id = "tgt"
        
        self.graph.nodes = {"src": node1, "tgt": node2}
        
        # Add relationships
        self.graph._add_relationship_to_indexes(
            "src", "tgt", RelationshipType.CONTAINS
        )
        
        # Get as objects
        rels = self.graph.get_relationships_as_objects()
        
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0]['sourceId'], "src")
        self.assertEqual(rels[0]['targetId'], "tgt")
        self.assertEqual(rels[0]['type'], RelationshipType.CONTAINS.value)


class TestNodeLabelsAndRelationships(unittest.TestCase):
    """Test node labels and relationship types exist."""
    
    def test_essential_node_labels(self):
        """Test essential node labels are defined."""
        # Core labels
        self.assertEqual(NodeLabels.FILE.value, "FILE")
        self.assertEqual(NodeLabels.FOLDER.value, "FOLDER") 
        self.assertEqual(NodeLabels.CLASS.value, "CLASS")
        self.assertEqual(NodeLabels.FUNCTION.value, "FUNCTION")
        
        # Extended labels
        self.assertEqual(NodeLabels.DESCRIPTION.value, "DESCRIPTION")
        self.assertEqual(NodeLabels.FILESYSTEM_FILE.value, "FILESYSTEM_FILE")
        self.assertEqual(NodeLabels.FILESYSTEM_DIRECTORY.value, "FILESYSTEM_DIRECTORY")
        self.assertEqual(NodeLabels.DOCUMENTATION_FILE.value, "DOCUMENTATION_FILE")
        self.assertEqual(NodeLabels.CONCEPT.value, "CONCEPT")
        self.assertEqual(NodeLabels.DOCUMENTED_ENTITY.value, "DOCUMENTED_ENTITY")
        
    def test_essential_relationship_types(self):
        """Test essential relationship types are defined."""
        # Core relationships
        self.assertEqual(RelationshipType.CONTAINS.value, "CONTAINS")
        self.assertEqual(RelationshipType.IMPORTS.value, "IMPORTS")
        self.assertEqual(RelationshipType.USES.value, "USES")
        self.assertEqual(RelationshipType.DEFINES.value, "DEFINES")
        
        # Extended relationships
        # Note: DESCRIBES doesn't exist, using DESCRIBES_ENTITY instead
        # self.assertEqual(RelationshipType.DESCRIBES.value, "DESCRIBES")
        self.assertEqual(RelationshipType.FILESYSTEM_CONTAINS.value, "FILESYSTEM_CONTAINS")
        self.assertEqual(RelationshipType.IMPLEMENTS.value, "IMPLEMENTS")
        self.assertEqual(RelationshipType.CONTAINS_CONCEPT.value, "CONTAINS_CONCEPT")
        self.assertEqual(RelationshipType.DESCRIBES_ENTITY.value, "DESCRIBES_ENTITY")
        self.assertEqual(RelationshipType.REFERENCED_BY_DESCRIPTION.value, "REFERENCED_BY_DESCRIPTION")


class TestDescriptionNode(unittest.TestCase):
    """Test DescriptionNode functionality."""
    
    def test_description_node_creation(self):
        """Test creating a description node."""
        from blarify.graph.node.description_node import DescriptionNode
        
        target_id = "function_123"
        desc_text = "This function calculates the sum"
        model = "gpt-4"
        
        node = DescriptionNode(
            target_node_id=target_id,
            description=desc_text,
            model=model
        )
        
        self.assertEqual(node.target_node_id, target_id)
        self.assertEqual(node.description, desc_text)
        self.assertEqual(node.model, model)
        self.assertEqual(node.label, NodeLabels.DESCRIPTION)
        
        # Check ID includes target
        self.assertIn(target_id, node.id)
        self.assertIn("description", node.id)
        
    def test_description_node_as_object(self):
        """Test serializing description node."""
        from blarify.graph.node.description_node import DescriptionNode
        
        node = DescriptionNode(
            target_node_id="class_456",
            description="Handles user authentication",
            model="gpt-3.5-turbo"
        )
        
        # Mock graph environment to avoid AttributeError
        node.graph_environment = Mock()
        node.graph_environment.diff_identifier = "test_diff"
        
        obj = node.as_object()
        
        self.assertEqual(obj['type'], 'DESCRIPTION')
        self.assertEqual(obj['attributes']['description'], "Handles user authentication")
        self.assertEqual(obj['attributes']['model'], "gpt-3.5-turbo")
        self.assertEqual(obj['attributes']['target_node_id'], "class_456")


class TestFilesystemNodes(unittest.TestCase):
    """Test filesystem node types."""
    
    def test_filesystem_file_node(self):
        """Test FilesystemFileNode creation."""
        from blarify.graph.node.filesystem_file_node import FilesystemFileNode
        
        node = FilesystemFileNode(
            path="file:///project/src/main.py",
            name="main.py",
            level=2,
            relative_path="src/main.py",
            size=1024,
            extension=".py",
            last_modified=1234567890.0
        )
        
        self.assertEqual(node.label, NodeLabels.FILESYSTEM_FILE)
        self.assertEqual(node.name, "main.py")
        self.assertEqual(node.relative_path, "src/main.py")
        self.assertEqual(node.size, 1024)
        self.assertEqual(node.extension, ".py")
        
    def test_filesystem_directory_node(self):
        """Test FilesystemDirectoryNode creation."""
        from blarify.graph.node.filesystem_directory_node import FilesystemDirectoryNode
        
        node = FilesystemDirectoryNode(
            path="file:///project/src",
            name="src",
            level=1,
            relative_path="src"
        )
        
        self.assertEqual(node.label, NodeLabels.FILESYSTEM_DIRECTORY)
        self.assertEqual(node.name, "src")
        self.assertEqual(node.relative_path, "src")


class TestDocumentationNodes(unittest.TestCase):
    """Test documentation node types."""
    
    def test_concept_node(self):
        """Test ConceptNode creation."""
        from blarify.graph.node.concept_node import ConceptNode
        
        node = ConceptNode(
            name="Repository Pattern",
            description="A design pattern for data access",
            source_file="README.md"
        )
        
        self.assertEqual(node.label, NodeLabels.CONCEPT)
        self.assertEqual(node.name, "Repository Pattern")
        self.assertEqual(node.description, "A design pattern for data access")
        self.assertEqual(node.source_file, "README.md")
        
    def test_documented_entity_node(self):
        """Test DocumentedEntityNode creation."""
        from blarify.graph.node.documented_entity_node import DocumentedEntityNode
        
        node = DocumentedEntityNode(
            name="UserService",
            entity_type="service",
            description="Manages user operations",
            source_file="docs/api.md"
        )
        
        self.assertEqual(node.label, NodeLabels.DOCUMENTED_ENTITY)
        self.assertEqual(node.name, "UserService")
        self.assertEqual(node.entity_type, "service")
        self.assertEqual(node.description, "Manages user operations")


if __name__ == '__main__':
    unittest.main()