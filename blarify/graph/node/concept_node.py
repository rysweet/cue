from typing import TYPE_CHECKING, Optional, Dict, Any
from blarify.graph.node.types.node import Node
from blarify.graph.node.types.node_labels import NodeLabels

if TYPE_CHECKING:
    from blarify.graph.graph_environment import GraphEnvironment


class ConceptNode(Node):
    """Node representing a concept extracted from documentation."""
    
    description: str
    source_file: str  # Path to the documentation file this concept came from
    
    def __init__(
        self,
        name: str,
        description: str,
        source_file: str,
        level: int = 0,
        parent: Optional["Node"] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ):
        # For concepts, use a file-like path format
        # Sanitize the name to create a valid path
        sanitized_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Use the source file as the base path
        path = f"file://{source_file}#concept:{sanitized_name}"
        
        super().__init__(
            label=NodeLabels.CONCEPT,
            path=path,
            name=name,
            level=level,
            parent=parent,
            graph_environment=graph_environment,
        )
        self.description = description
        self.source_file = source_file
    
    @property
    def node_repr_for_identifier(self) -> str:
        return f"/CONCEPT[{self.name}]"
    
    def as_object(self) -> Dict[str, Any]:
        obj = super().as_object()
        obj["attributes"].update({
            "description": self.description,
            "source_file": self.source_file,
            "type": "concept",
        })
        return obj