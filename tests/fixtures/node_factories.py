from typing import Optional, List
"""
Factory functions for creating test nodes.
"""
import time
from blarify.graph.node.file_node import FileNode
from blarify.graph.node.folder_node import FolderNode
from blarify.graph.node.class_node import ClassNode
from blarify.graph.node.function_node import FunctionNode
from blarify.graph.node.filesystem_file_node import FilesystemFileNode
from blarify.graph.node.filesystem_directory_node import FilesystemDirectoryNode
from blarify.graph.node.documentation_file_node import DocumentationFileNode
from blarify.graph.node.concept_node import ConceptNode
from blarify.graph.node.documented_entity_node import DocumentedEntityNode
from blarify.graph.node.description_node import DescriptionNode
from blarify.graph.graph_environment import GraphEnvironment


def get_test_graph_environment():
    """Get a default graph environment for testing."""
    return GraphEnvironment(
        environment="test",
        diff_identifier="test_diff",
        root_path="/test"
    )


def create_file_node(name: str = "test.py", path: Optional[str] = None, level: int = 1):
    """Create a file node with default values."""
    from unittest.mock import Mock
    
    if path is None:
        path = f"file:///test/{name}"
    
    # Create mock tree-sitter objects
    mock_definition_range = Mock()
    mock_node_range = Mock()
    mock_node_range.range = Mock()
    mock_node_range.range.start = Mock(line=1)
    mock_node_range.range.end = Mock(line=100)
    mock_body_node = Mock()
    mock_tree_sitter_node = Mock()
    mock_tree_sitter_node.text = b"# File content"
    mock_tree_sitter_node.start_byte = 0
    
    return FileNode(
        definition_range=mock_definition_range,
        node_range=mock_node_range,
        code_text="# File content",
        body_node=mock_body_node,
        tree_sitter_node=mock_tree_sitter_node,
        path=path,
        name=name,
        level=level,
        graph_environment=get_test_graph_environment()
    )


def create_folder_node(name: str = "src", path: Optional[str] = None, level: int = 0):
    """Create a folder node with default values."""
    if path is None:
        path = f"file:///test/{name}"
    return FolderNode(path=path, name=name, level=level)


def create_class_node(name: str = "TestClass", path: Optional[str] = "file:///test/main.py", 
                     start_line: int = 10, end_line: int = 50):
    """Create a class node with default values."""
    from unittest.mock import Mock
    
    # Create mock tree-sitter objects
    mock_definition_range = Mock()
    mock_node_range = Mock()
    mock_node_range.range = Mock()
    mock_node_range.range.start = Mock(line=start_line)
    mock_node_range.range.end = Mock(line=end_line)
    mock_body_node = Mock()
    mock_tree_sitter_node = Mock()
    mock_tree_sitter_node.text = f"class {name}: pass".encode()
    mock_tree_sitter_node.start_byte = 0
    
    return ClassNode(
        definition_range=mock_definition_range,
        node_range=mock_node_range,
        code_text=f"class {name}: pass",
        body_node=mock_body_node,
        tree_sitter_node=mock_tree_sitter_node,
        name=name,
        path=path,
        level=2,
        graph_environment=get_test_graph_environment()
    )


def create_function_node(name: str = "test_function", path: Optional[str] = "file:///test/main.py",
                        start_line: int = 5, end_line: int = 8):
    """Create a function node with default values."""
    from unittest.mock import Mock
    
    # Create mock tree-sitter objects
    mock_definition_range = Mock()
    mock_node_range = Mock()
    mock_node_range.range = Mock()
    mock_node_range.range.start = Mock(line=start_line)
    mock_node_range.range.end = Mock(line=end_line)
    mock_body_node = Mock()
    mock_tree_sitter_node = Mock()
    mock_tree_sitter_node.text = f"def {name}(): pass".encode()
    mock_tree_sitter_node.start_byte = 0
    
    return FunctionNode(
        definition_range=mock_definition_range,
        node_range=mock_node_range,
        code_text=f"def {name}(): pass",
        body_node=mock_body_node,
        tree_sitter_node=mock_tree_sitter_node,
        name=name,
        path=path,
        level=2,
        graph_environment=get_test_graph_environment()
    )


def create_filesystem_file_node(name: str = "test.py", relative_path: Optional[str] = None,
                               size: int = 1024, extension: str = ".py"):
    """Create a filesystem file node with default values."""
    if relative_path is None:
        relative_path = f"src/{name}"
    return FilesystemFileNode(
        path=f"file:///test/{relative_path}",
        name=name,
        level=relative_path.count('/') + 1,
        relative_path=relative_path,
        size=size,
        extension=extension,
        last_modified=time.time(),
        graph_environment=get_test_graph_environment()
    )


def create_filesystem_directory_node(name: str = "src", relative_path: Optional[str] = None):
    """Create a filesystem directory node with default values."""
    if relative_path is None:
        relative_path = name
    return FilesystemDirectoryNode(
        path=f"file:///test/{relative_path}",
        name=name,
        level=relative_path.count('/'),
        relative_path=relative_path,
        graph_environment=get_test_graph_environment()
    )


def create_documentation_file_node(name: str = "README.md", relative_path: Optional[str] = None,
                                  format: str = "markdown"):
    """Create a documentation file node with default values."""
    if relative_path is None:
        relative_path = name
    return DocumentationFileNode(
        path=f"file:///test/{relative_path}",
        name=name,
        level=relative_path.count('/'),
        relative_path=relative_path,
        format=format,
        graph_environment=get_test_graph_environment()
    )


def create_concept_node(name: str = "Design Pattern", description: Optional[str] = None,
                       source_file: str = "README.md"):
    """Create a concept node with default values."""
    if description is None:
        description = f"Description of {name}"
    return ConceptNode(
        name=name,
        description=description,
        source_file=source_file,
        graph_environment=get_test_graph_environment()
    )


def create_documented_entity_node(name: str = "UserService", entity_type: str = "class",
                                 description: Optional[str] = None, source_file: str = "README.md"):
    """Create a documented entity node with default values."""
    if description is None:
        description = f"Description of {name}"
    return DocumentedEntityNode(
        name=name,
        entity_type=entity_type,
        description=description,
        source_file=source_file,
        graph_environment=get_test_graph_environment()
    )


def create_description_node(target_node_id: str, description: str = "Test description",
                           model: str = "gpt-4", path: Optional[str] = None):
    """Create a description node with default values."""
    if path is None:
        path = f"file:///test/description_{target_node_id}"
    return DescriptionNode(
        path=path,
        name=f"description_for_{target_node_id}",
        level=1,
        description_text=description,
        target_node_id=target_node_id,
        llm_model=model,
        graph_environment=get_test_graph_environment()
    )


def create_sample_project_nodes() -> List:
    """Create a set of nodes representing a sample project structure."""
    nodes: List = []
    
    # Root folder
    root = create_folder_node("project", "file:///test/project", 0)
    nodes.append(root)
    
    # Source folder
    src = create_folder_node("src", "file:///test/project/src", 1)
    nodes.append(src)
    
    # Main file
    main_file = create_file_node("main.py", "file:///test/project/src/main.py", 2)
    nodes.append(main_file)
    
    # Classes in main file
    app_class = create_class_node("Application", main_file.path, 10, 50)
    config_class = create_class_node("Config", main_file.path, 52, 70)
    nodes.extend([app_class, config_class])
    
    # Functions in main file
    main_func = create_function_node("main", main_file.path, 72, 80)
    init_func = create_function_node("initialize", main_file.path, 82, 90)
    nodes.extend([main_func, init_func])
    
    # Utils file
    utils_file = create_file_node("utils.py", "file:///test/project/src/utils.py", 2)
    nodes.append(utils_file)
    
    # Functions in utils file
    format_func = create_function_node("format_string", utils_file.path, 1, 5)
    validate_func = create_function_node("validate_input", utils_file.path, 7, 15)
    nodes.extend([format_func, validate_func])
    
    # Test folder
    tests = create_folder_node("tests", "file:///test/project/tests", 1)
    nodes.append(tests)
    
    # Test file
    test_file = create_file_node("test_main.py", "file:///test/project/tests/test_main.py", 2)
    nodes.append(test_file)
    
    # Documentation
    readme = create_documentation_file_node("README.md", "README.md")
    nodes.append(readme)
    
    return nodes