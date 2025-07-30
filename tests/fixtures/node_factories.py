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


def create_file_node(name="test.py", path=None, level=1):
    """Create a file node with default values."""
    if path is None:
        path = f"file:///test/{name}"
    return FileNode(path=path, name=name, level=level)


def create_folder_node(name="src", path=None, level=0):
    """Create a folder node with default values."""
    if path is None:
        path = f"file:///test/{name}"
    return FolderNode(path=path, name=name, level=level)


def create_class_node(name="TestClass", path="file:///test/main.py", 
                     start_line=10, end_line=50):
    """Create a class node with default values."""
    return ClassNode(
        id=f"class_{name.lower()}_{start_line}",
        name=name,
        path=path,
        level=2,
        start_line=start_line,
        end_line=end_line
    )


def create_function_node(name="test_function", path="file:///test/main.py",
                        start_line=5, end_line=8):
    """Create a function node with default values."""
    return FunctionNode(
        id=f"func_{name.lower()}_{start_line}",
        name=name,
        path=path,
        level=2,
        start_line=start_line,
        end_line=end_line
    )


def create_filesystem_file_node(name="test.py", relative_path=None,
                               size=1024, extension=".py"):
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
        last_modified=time.time()
    )


def create_filesystem_directory_node(name="src", relative_path=None):
    """Create a filesystem directory node with default values."""
    if relative_path is None:
        relative_path = name
    return FilesystemDirectoryNode(
        path=f"file:///test/{relative_path}",
        name=name,
        level=relative_path.count('/'),
        relative_path=relative_path
    )


def create_documentation_file_node(name="README.md", relative_path=None,
                                  format="markdown"):
    """Create a documentation file node with default values."""
    if relative_path is None:
        relative_path = name
    return DocumentationFileNode(
        path=f"file:///test/{relative_path}",
        name=name,
        level=relative_path.count('/'),
        relative_path=relative_path,
        format=format
    )


def create_concept_node(name="Design Pattern", description=None,
                       source_file="README.md"):
    """Create a concept node with default values."""
    if description is None:
        description = f"Description of {name}"
    return ConceptNode(
        name=name,
        description=description,
        source_file=source_file
    )


def create_documented_entity_node(name="UserService", entity_type="class",
                                 description=None, source_file="README.md"):
    """Create a documented entity node with default values."""
    if description is None:
        description = f"Description of {name}"
    return DocumentedEntityNode(
        name=name,
        entity_type=entity_type,
        description=description,
        source_file=source_file
    )


def create_description_node(target_node_id, description="Test description",
                           model="gpt-4"):
    """Create a description node with default values."""
    return DescriptionNode(
        target_node_id=target_node_id,
        description=description,
        model=model
    )


def create_sample_project_nodes():
    """Create a set of nodes representing a sample project structure."""
    nodes = []
    
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