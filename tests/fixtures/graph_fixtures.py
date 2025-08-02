"""
Graph fixtures for testing graph operations.
"""
from blarify.graph.graph import Graph
# Removed unused imports - FileNode, ClassNode, FunctionNode
from blarify.graph.node.filesystem_file_node import FilesystemFileNode
from blarify.graph.node.filesystem_directory_node import FilesystemDirectoryNode
from blarify.graph.relationship.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType


def create_test_graph():
    """Create a test graph with sample nodes and relationships."""
    graph = Graph()
    
    # Add filesystem file nodes instead of code nodes
    main_file = FilesystemFileNode(
        path="file:///test/src/main.py",
        name="main.py",
        level=2,
        relative_path="src/main.py",
        size=1500,
        extension=".py",
        last_modified=1234567890.0
    )
    utils_file = FilesystemFileNode(
        path="file:///test/src/utils.py",
        name="utils.py",
        level=2,
        relative_path="src/utils.py",
        size=1000,
        extension=".py",
        last_modified=1234567890.0
    )
    test_file = FilesystemFileNode(
        path="file:///test/tests/test_main.py",
        name="test_main.py",
        level=2,
        relative_path="tests/test_main.py",
        size=2000,
        extension=".py",
        last_modified=1234567890.0
    )
    
    graph.add_node(main_file)
    graph.add_node(utils_file)
    graph.add_node(test_file)
    
    # Add documentation nodes
    from blarify.graph.node.concept_node import ConceptNode
    from blarify.graph.node.documented_entity_node import DocumentedEntityNode
    
    app_concept = ConceptNode(
        name="Application Architecture",
        description="Main application structure and design",
        source_file="src/main.py"
    )
    graph.add_node(app_concept)
    
    # Add documented entities
    main_entity = DocumentedEntityNode(
        name="main",
        entity_type="function",
        description="Entry point of the application",
        source_file="src/main.py"
    )
    format_entity = DocumentedEntityNode(
        name="format_string",
        entity_type="function",
        description="Utility function for string formatting",
        source_file="src/utils.py"
    )
    
    graph.add_node(main_entity)
    graph.add_node(format_entity)
    
    # Add relationships
    graph.add_references_relationships([
        Relationship(
            start_node=main_file,
            end_node=app_concept,
            rel_type=RelationshipType.CONTAINS_CONCEPT
        ),
        Relationship(
            start_node=main_file,
            end_node=main_entity,
            rel_type=RelationshipType.DESCRIBES_ENTITY
        ),
        Relationship(
            start_node=utils_file,
            end_node=format_entity,
            rel_type=RelationshipType.DESCRIBES_ENTITY
        ),
        Relationship(
            start_node=test_file,
            end_node=main_file,
            rel_type=RelationshipType.DEPENDS_ON
        )
    ])
    
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
    graph.add_references_relationships([
        Relationship(
            start_node=root_dir,
            end_node=src_dir,
            rel_type=RelationshipType.FILESYSTEM_CONTAINS
        ),
        Relationship(
            start_node=root_dir,
            end_node=tests_dir,
            rel_type=RelationshipType.FILESYSTEM_CONTAINS
        ),
        Relationship(
            start_node=src_dir,
            end_node=main_fs_file,
            rel_type=RelationshipType.FILESYSTEM_CONTAINS
        ),
        Relationship(
            start_node=src_dir,
            end_node=utils_fs_file,
            rel_type=RelationshipType.FILESYSTEM_CONTAINS
        )
    ])
    
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
    graph.add_references_relationships([
        Relationship(
            start_node=readme,
            end_node=architecture_concept,
            rel_type=RelationshipType.CONTAINS_CONCEPT
        ),
        Relationship(
            start_node=readme,
            end_node=user_service,
            rel_type=RelationshipType.DESCRIBES_ENTITY
        )
    ])
    
    return graph


def create_complex_graph():
    """Create a complex test graph with all node types and relationships."""
    # Start with basic code graph
    graph = create_test_graph()
    
    # Add filesystem nodes
    fs_graph = create_filesystem_graph()
    for node in fs_graph.get_all_nodes():
        graph.add_node(node)
    
    # Add documentation nodes
    doc_graph = create_documentation_graph()
    for node in doc_graph.get_all_nodes():
        graph.add_node(node)
    
    # Add all relationships
    for rel in fs_graph.get_all_relationships():
        graph.add_references_relationships([rel])
    for rel in doc_graph.get_all_relationships():
        graph.add_references_relationships([rel])
    
    # Connect filesystem to code nodes
    # This would normally be done by the graph builder
    # but we'll simulate it here for testing
    
    return graph