from typing import TYPE_CHECKING, Optional
from blarify.graph.node.types.node import Node
from blarify.graph.node.types.node_labels import NodeLabels

if TYPE_CHECKING:
    from blarify.graph.graph_environment import GraphEnvironment


class DescriptionNode(Node):
    """Node representing an LLM-generated description of a code element."""
    
    description_text: str
    target_node_id: str
    llm_model: str
    
    def __init__(
        self,
        path: str,
        name: str,
        level: int,
        description_text: str,
        target_node_id: str,
        llm_model: str = "gpt-4",
        parent: "Node" = None,
        graph_environment: "GraphEnvironment" = None,
    ):
        super().__init__(
            label=NodeLabels.DESCRIPTION,
            path=path,
            name=name,
            level=level,
            parent=parent,
            graph_environment=graph_environment,
        )
        self.description_text = description_text
        self.target_node_id = target_node_id
        self.llm_model = llm_model
    
    @property
    def node_repr_for_identifier(self) -> str:
        return f"/DESCRIPTION[{self.target_node_id}]"
    
    def as_object(self) -> dict:
        obj = super().as_object()
        obj["attributes"].update({
            "description_text": self.description_text,
            "target_node_id": self.target_node_id,
            "llm_model": self.llm_model,
        })
        return obj