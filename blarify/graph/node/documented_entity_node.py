from typing import TYPE_CHECKING, Optional
from blarify.graph.node.types.node import Node
from blarify.graph.node.types.node_labels import NodeLabels

if TYPE_CHECKING:
    from blarify.graph.graph_environment import GraphEnvironment


class DocumentedEntityNode(Node):
    """Node representing an entity (class, service, module) mentioned in documentation."""
    
    entity_type: str  # class, service, module, api, etc.
    description: str
    source_file: str  # Path to the documentation file this entity came from
    
    def __init__(
        self,
        name: str,
        entity_type: str,
        description: str,
        source_file: str,
        level: int = 0,
        parent: Optional["Node"] = None,
        graph_environment: Optional["GraphEnvironment"] = None,
    ):
        # For documented entities, use a file-like path format
        # Sanitize the name and type to create a valid path
        sanitized_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        sanitized_type = entity_type.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Use the source file as the base path
        path = f"file://{source_file}#entity:{sanitized_type}:{sanitized_name}"
        
        super().__init__(
            label=NodeLabels.DOCUMENTED_ENTITY,
            path=path,
            name=name,
            level=level,
            parent=parent,
            graph_environment=graph_environment,
        )
        self.entity_type = entity_type
        self.description = description
        self.source_file = source_file
    
    @property
    def node_repr_for_identifier(self) -> str:
        return f"/DOCUMENTED_ENTITY[{self.entity_type}:{self.name}]"
    
    def as_object(self) -> dict:
        obj = super().as_object()
        obj["attributes"].update({
            "entity_type": self.entity_type,
            "description": self.description,
            "source_file": self.source_file,
            "type": "documented_entity",
        })
        return obj