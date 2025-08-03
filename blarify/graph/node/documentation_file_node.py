from typing import TYPE_CHECKING, Optional, Dict, Any
from blarify.graph.node.types.node import Node
from blarify.graph.node.types.node_labels import NodeLabels

if TYPE_CHECKING:
    from blarify.graph.graph_environment import GraphEnvironment


class DocumentationFileNode(Node):
    """Node representing a documentation file."""
    
    relative_path: str
    doc_type: str  # markdown, rst, txt, etc.
    
    def __init__(
        self,
        path: str,
        name: str,
        level: int,
        relative_path: str,
        doc_type: str,
        parent: Optional["Node"] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ):
        super().__init__(
            label=NodeLabels.DOCUMENTATION_FILE,
            path=path,
            name=name,
            level=level,
            parent=parent,
            graph_environment=graph_environment,
        )
        self.relative_path = relative_path
        self.doc_type = doc_type
    
    @property
    def node_repr_for_identifier(self) -> str:
        return f"/DOCUMENTATION_FILE[{self.relative_path}]"
    
    def as_object(self) -> Dict[str, Any]:
        obj = super().as_object()
        obj["attributes"].update({
            "relative_path": self.relative_path,
            "doc_type": self.doc_type,
            "type": "documentation_file",
        })
        return obj