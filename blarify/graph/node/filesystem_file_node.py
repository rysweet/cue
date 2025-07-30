from typing import TYPE_CHECKING, Optional
from blarify.graph.node.types.node import Node
from blarify.graph.node.types.node_labels import NodeLabels

if TYPE_CHECKING:
    from blarify.graph.graph_environment import GraphEnvironment


class FilesystemFileNode(Node):
    """Node representing a file in the filesystem."""
    
    relative_path: str
    size: int
    file_extension: str
    last_modified: float
    permissions: Optional[str]
    
    def __init__(
        self,
        path: str,
        name: str,
        level: int,
        relative_path: str,
        size: int,
        extension: str,
        last_modified: float,
        permissions: Optional[str] = None,
        parent: "Node" = None,
        graph_environment: "GraphEnvironment" = None,
    ):
        super().__init__(
            label=NodeLabels.FILESYSTEM_FILE,
            path=path,
            name=name,
            level=level,
            parent=parent,
            graph_environment=graph_environment,
        )
        self.relative_path = relative_path
        self.size = size
        self.file_extension = extension
        self.last_modified = last_modified
        self.permissions = permissions
    
    @property
    def node_repr_for_identifier(self) -> str:
        return f"/FILESYSTEM_FILE[{self.relative_path}]"
    
    def as_object(self) -> dict:
        obj = super().as_object()
        obj["attributes"].update({
            "relative_path": self.relative_path,
            "size": self.size,
            "extension": self.file_extension,
            "last_modified": self.last_modified,
            "type": "file",
        })
        if self.permissions:
            obj["attributes"]["permissions"] = self.permissions
        return obj