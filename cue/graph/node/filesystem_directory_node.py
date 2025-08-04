from typing import TYPE_CHECKING, Optional, List, Dict, Any
from cue.graph.node.types.node import Node
from cue.graph.node.types.node_labels import NodeLabels
from cue.graph.relationship import Relationship

if TYPE_CHECKING:
    from cue.graph.graph_environment import GraphEnvironment


class FilesystemDirectoryNode(Node):
    """Node representing a directory in the filesystem."""
    
    relative_path: str
    permissions: Optional[str]
    _contains: List[Node]
    
    def __init__(
        self,
        path: str,
        name: str,
        level: int,
        relative_path: str,
        permissions: Optional[str] = None,
        parent: Optional["Node"] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ):
        super().__init__(
            label=NodeLabels.FILESYSTEM_DIRECTORY,
            path=path,
            name=name,
            level=level,
            parent=parent,
            graph_environment=graph_environment,
        )
        self.relative_path = relative_path
        self.permissions = permissions
        self._contains: List[Node] = []
    
    @property
    def node_repr_for_identifier(self) -> str:
        return f"/FILESYSTEM_DIR[{self.relative_path}]"
    
    def as_object(self) -> Dict[str, Any]:
        obj = super().as_object()
        obj["attributes"].update({
            "relative_path": self.relative_path,
            "type": "directory",
        })
        if self.permissions:
            obj["attributes"]["permissions"] = self.permissions
        return obj
    
    def add_child(self, node: "Node") -> None:
        """Add a child file or directory to this directory."""
        from cue.graph.node.filesystem_file_node import FilesystemFileNode
        
        if isinstance(node, (FilesystemFileNode, FilesystemDirectoryNode)):
            self._contains.append(node)
        else:
            raise TypeError(f"FilesystemDirectoryNode can only contain FilesystemFileNode or FilesystemDirectoryNode, not {type(node).__name__}")
    
    def get_relationships(self) -> List["Relationship"]:
        """Get FILESYSTEM_CONTAINS relationships for children."""
        from cue.graph.relationship.relationship_type import RelationshipType
        
        relationships: List["Relationship"] = []
        for child in self._contains:
            rel = Relationship(
                start_node=self,
                end_node=child,
                rel_type=RelationshipType.FILESYSTEM_CONTAINS
            )
            relationships.append(rel)
        return relationships