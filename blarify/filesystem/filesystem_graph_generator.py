import os
import logging
from typing import TYPE_CHECKING, Dict, Optional, List
from blarify.graph.node import (
    FilesystemFileNode, FilesystemDirectoryNode, NodeLabels
)
from blarify.graph.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType

if TYPE_CHECKING:
    from blarify.graph.graph import Graph
    from blarify.graph.graph_environment import GraphEnvironment

logger = logging.getLogger(__name__)


class FilesystemGraphGenerator:
    """Generates filesystem nodes and relationships for a codebase."""
    
    def __init__(
        self, 
        root_path: str,
        graph_environment: Optional["GraphEnvironment"] = None,
        include_metadata: bool = True,
        max_depth: int = 10,
        extensions_to_skip: Optional[List[str]] = None,
        names_to_skip: Optional[List[str]] = None
    ):
        self.root_path = os.path.abspath(root_path)
        self.graph_environment = graph_environment
        self.include_metadata = include_metadata
        self.max_depth = max_depth
        self.extensions_to_skip = extensions_to_skip or []
        self.names_to_skip = names_to_skip or []
        self._directory_nodes: Dict[str, FilesystemDirectoryNode] = {}
        self._file_nodes: Dict[str, FilesystemFileNode] = {}
    
    def generate_filesystem_nodes(self, graph: "Graph") -> None:
        """Generate filesystem nodes and add them to the graph."""
        logger.info(f"Generating filesystem nodes for: {self.root_path}")
        
        # Create root directory node
        root_node = self._create_directory_node(self.root_path, level=0)
        graph.add_node(root_node)
        
        # Traverse filesystem
        self._traverse_directory(self.root_path, root_node, graph, level=1)
        
        # Add all relationships
        for dir_node in self._directory_nodes.values():
            relationships = dir_node.get_relationships()
            for rel in relationships:
                graph.add_references_relationships([rel])
        
        logger.info(f"Created {len(self._file_nodes)} file nodes and {len(self._directory_nodes)} directory nodes")
    
    def _traverse_directory(
        self, 
        dir_path: str, 
        parent_node: FilesystemDirectoryNode, 
        graph: "Graph",
        level: int
    ) -> None:
        """Recursively traverse directory and create nodes."""
        if level > self.max_depth:
            logger.warning(f"Max depth {self.max_depth} reached at {dir_path}")
            return
        
        try:
            entries = os.listdir(dir_path)
        except PermissionError:
            logger.warning(f"Permission denied: {dir_path}")
            return
        
        for entry in sorted(entries):
            # Skip specified names
            if entry in self.names_to_skip:
                continue
            
            entry_path = os.path.join(dir_path, entry)
            
            if os.path.isdir(entry_path):
                # Create directory node
                dir_node = self._create_directory_node(entry_path, level, parent_node)
                graph.add_node(dir_node)
                parent_node.add_child(dir_node)
                
                # Recurse into subdirectory
                self._traverse_directory(entry_path, dir_node, graph, level + 1)
                
            elif os.path.isfile(entry_path):
                # Skip specified extensions
                _, ext = os.path.splitext(entry)
                if ext in self.extensions_to_skip:
                    continue
                
                # Create file node
                file_node = self._create_file_node(entry_path, level, parent_node)
                graph.add_node(file_node)
                parent_node.add_child(file_node)
    
    def _create_directory_node(
        self, 
        dir_path: str, 
        level: int,
        parent: Optional[FilesystemDirectoryNode] = None
    ) -> FilesystemDirectoryNode:
        """Create a filesystem directory node."""
        abs_path = os.path.abspath(dir_path)
        relative_path = os.path.relpath(abs_path, self.root_path)
        if relative_path == ".":
            relative_path = ""
        
        name = os.path.basename(abs_path) or os.path.basename(self.root_path)
        
        permissions = None
        if self.include_metadata:
            try:
                stat = os.stat(abs_path)
                permissions = oct(stat.st_mode)[-3:]
            except OSError:
                pass
        
        node = FilesystemDirectoryNode(
            path=f"file://{abs_path}",
            name=name,
            level=level,
            relative_path=relative_path,
            permissions=permissions,
            parent=parent,
            graph_environment=self.graph_environment
        )
        
        self._directory_nodes[abs_path] = node
        return node
    
    def _create_file_node(
        self,
        file_path: str,
        level: int,
        parent: FilesystemDirectoryNode
    ) -> FilesystemFileNode:
        """Create a filesystem file node."""
        abs_path = os.path.abspath(file_path)
        relative_path = os.path.relpath(abs_path, self.root_path)
        name = os.path.basename(abs_path)
        _, extension = os.path.splitext(name)
        
        # Get file metadata
        size = 0
        last_modified = 0.0
        permissions = None
        
        if self.include_metadata:
            try:
                stat = os.stat(abs_path)
                size = stat.st_size
                last_modified = stat.st_mtime
                permissions = oct(stat.st_mode)[-3:]
            except OSError:
                logger.warning(f"Could not stat file: {abs_path}")
        
        node = FilesystemFileNode(
            path=f"file://{abs_path}",
            name=name,
            level=level,
            relative_path=relative_path,
            size=size,
            extension=extension,
            last_modified=last_modified,
            permissions=permissions,
            parent=parent,
            graph_environment=self.graph_environment
        )
        
        self._file_nodes[abs_path] = node
        return node
    
    def create_implements_relationships(
        self, 
        graph: "Graph"
    ) -> List[Relationship]:
        """Create IMPLEMENTS relationships between filesystem files and code nodes."""
        implements_relationships = []
        
        # For each file node, find corresponding code nodes
        for file_path, fs_file_node in self._file_nodes.items():
            # Convert to file URI to match code nodes
            file_uri = f"file://{file_path}"
            
            # Get all code nodes at this path
            code_nodes = graph.get_nodes_by_path(file_uri)
            
            for code_node in code_nodes:
                # Skip if it's a filesystem node or folder node
                if code_node.label in [NodeLabels.FILESYSTEM_FILE, NodeLabels.FILESYSTEM_DIRECTORY, NodeLabels.FOLDER]:
                    continue
                
                # Create IMPLEMENTS relationship from filesystem file to code node
                rel = Relationship(
                    start_node=fs_file_node,
                    end_node=code_node,
                    rel_type=RelationshipType.IMPLEMENTS
                )
                implements_relationships.append(rel)
                
        logger.info(f"Created {len(implements_relationships)} IMPLEMENTS relationships")
        return implements_relationships
    
    def create_description_references(
        self,
        graph: "Graph"
    ) -> List[Relationship]:
        """Create REFERENCED_BY_DESCRIPTION relationships for file paths mentioned in descriptions."""
        referenced_relationships = []
        
        # Get all description nodes
        description_nodes = graph.get_nodes_by_label(NodeLabels.DESCRIPTION)
        
        for desc_node in description_nodes:
            if hasattr(desc_node, 'description_text'):
                # Look for file paths in the description
                for file_path, fs_node in self._file_nodes.items():
                    relative_path = os.path.relpath(file_path, self.root_path)
                    
                    # Check if relative path is mentioned in description
                    if relative_path in desc_node.description_text:
                        rel = Relationship(
                            start_node=desc_node,
                            end_node=fs_node,
                            rel_type=RelationshipType.REFERENCED_BY_DESCRIPTION
                        )
                        referenced_relationships.append(rel)
        
        logger.info(f"Created {len(referenced_relationships)} REFERENCED_BY_DESCRIPTION relationships")
        return referenced_relationships