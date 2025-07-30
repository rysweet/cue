"""
Graph fixtures for testing graph operations.
"""
from blarify.graph.graph import Graph
from blarify.graph.node.file_node import FileNode
from blarify.graph.node.class_node import ClassNode
from blarify.graph.node.function_node import FunctionNode
from blarify.graph.node.filesystem_file_node import FilesystemFileNode
from blarify.graph.node.filesystem_directory_node import FilesystemDirectoryNode
from blarify.graph.relationship.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType


def create_test_graph():
    """Create a test graph with sample nodes and relationships."""
    graph = Graph()
    
    # Add file nodes
    main_file = FileNode(
        path="file:///test/src/main.py",
        name="main.py",
        level=2
    )
    utils_file = FileNode(
        path="file:///test/src/utils.py",
        name="utils.py",
        level=2
    )
    test_file = FileNode(
        path="file:///test/tests/test_main.py",
        name="test_main.py",
        level=2
    )
    
    graph.add_node(main_file)
    graph.add_node(utils_file)
    graph.add_node(test_file)
    
    # Add class nodes
    app_class = ClassNode(
        id="class_app_123",
        name="Application",
        path="file:///test/src/main.py",
        level=3,
        start_line=5,
        end_line=8
    )
    graph.add_node(app_class)
    
    # Add function nodes
    main_func = FunctionNode(
        id="func_main_456",
        name="main",
        path="file:///test/src/main.py",
        level=3,
        start_line=1,
        end_line=3
    )
    format_func = FunctionNode(
        id="func_format_789",
        name="format_string",
        path="file:///test/src/utils.py",
        level=3,
        start_line=1,
        end_line=3
    )
    
    graph.add_node(main_func)
    graph.add_node(format_func)
    
    # Add relationships
    graph.add_relationship(Relationship(
        source_id=main_file.id,
        target_id=app_class.id,
        type=RelationshipType.CONTAINS
    ))
    graph.add_relationship(Relationship(
        source_id=main_file.id,
        target_id=main_func.id,
        type=RelationshipType.CONTAINS
    ))
    graph.add_relationship(Relationship(
        source_id=utils_file.id,
        target_id=format_func.id,
        type=RelationshipType.CONTAINS
    ))
    graph.add_relationship(Relationship(
        source_id=test_file.id,
        target_id=main_file.id,
        type=RelationshipType.IMPORTS
    ))
    
    return graph


def create_filesystem_graph():
    """Create a test graph with filesystem nodes."""
    graph = Graph()
    
    # Add filesystem directory nodes
    root_dir = FilesystemDirectoryNode(
        path="file:///test",
        name="test",
        level=0,
        relative_path=""
    )
    src_dir = FilesystemDirectoryNode(
        path="file:///test/src",
        name="src",
        level=1,
        relative_path="src"
    )
    tests_dir = FilesystemDirectoryNode(
        path="file:///test/tests",
        name="tests",
        level=1,
        relative_path="tests"
    )
    
    graph.add_node(root_dir)
    graph.add_node(src_dir)
    graph.add_node(tests_dir)
    
    # Add filesystem file nodes
    main_fs_file = FilesystemFileNode(
        path="file:///test/src/main.py",
        name="main.py",
        level=2,
        relative_path="src/main.py",
        size=150,
        extension=".py",
        last_modified=1234567890
    )
    utils_fs_file = FilesystemFileNode(
        path="file:///test/src/utils.py",
        name="utils.py",
        level=2,
        relative_path="src/utils.py",
        size=100,
        extension=".py",
        last_modified=1234567890
    )
    
    graph.add_node(main_fs_file)
    graph.add_node(utils_fs_file)
    
    # Add filesystem relationships
    graph.add_relationship(Relationship(
        source_id=root_dir.id,
        target_id=src_dir.id,
        type=RelationshipType.FILESYSTEM_CONTAINS
    ))
    graph.add_relationship(Relationship(
        source_id=root_dir.id,
        target_id=tests_dir.id,
        type=RelationshipType.FILESYSTEM_CONTAINS
    ))
    graph.add_relationship(Relationship(
        source_id=src_dir.id,
        target_id=main_fs_file.id,
        type=RelationshipType.FILESYSTEM_CONTAINS
    ))
    graph.add_relationship(Relationship(
        source_id=src_dir.id,
        target_id=utils_fs_file.id,
        type=RelationshipType.FILESYSTEM_CONTAINS
    ))
    
    return graph


def create_documentation_graph():
    """Create a test graph with documentation nodes."""
    from blarify.graph.node.documentation_file_node import DocumentationFileNode
    from blarify.graph.node.concept_node import ConceptNode
    from blarify.graph.node.documented_entity_node import DocumentedEntityNode
    
    graph = Graph()
    
    # Add documentation file node
    readme = DocumentationFileNode(
        path="file:///test/README.md",
        name="README.md",
        level=1,
        relative_path="README.md",
        format="markdown"
    )
    graph.add_node(readme)
    
    # Add concept nodes
    architecture_concept = ConceptNode(
        name="Microservices Architecture",
        description="The application uses microservices pattern",
        source_file="README.md"
    )
    pattern_concept = ConceptNode(
        name="Repository Pattern",
        description="Data access is implemented using repository pattern",
        source_file="docs/patterns.md"
    )
    
    graph.add_node(architecture_concept)
    graph.add_node(pattern_concept)
    
    # Add documented entity
    user_service = DocumentedEntityNode(
        name="UserService",
        entity_type="service",
        description="Handles user management operations",
        source_file="README.md"
    )
    graph.add_node(user_service)
    
    # Add relationships
    graph.add_relationship(Relationship(
        source_id=readme.id,
        target_id=architecture_concept.id,
        type=RelationshipType.CONTAINS_CONCEPT
    ))
    graph.add_relationship(Relationship(
        source_id=readme.id,
        target_id=user_service.id,
        type=RelationshipType.DESCRIBES_ENTITY
    ))
    
    return graph


def create_complex_graph():
    """Create a complex test graph with all node types and relationships."""
    # Start with basic code graph
    graph = create_test_graph()
    
    # Add filesystem nodes
    fs_graph = create_filesystem_graph()
    for node in fs_graph.get_nodes_as_objects():
        graph.add_node_from_dict(node)
    
    # Add documentation nodes
    doc_graph = create_documentation_graph()
    for node in doc_graph.get_nodes_as_objects():
        graph.add_node_from_dict(node)
    
    # Connect filesystem to code nodes
    # This would normally be done by the graph builder
    # but we'll simulate it here for testing
    
    return graph