from typing import Any, Dict
from cue.graph.node.types.node_labels import NodeLabels
from cue.graph.node.types.definition_node import DefinitionNode  # type: ignore[import-cycles]


class FileNode(DefinitionNode):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(label=NodeLabels.FILE, **kwargs)

    @property
    def node_repr_for_identifier(self) -> str:
        return "/" + self.name

    def as_object(self) -> Dict[str, Any]:
        obj = super().as_object()
        obj["attributes"]["text"] = self.code_text
        return obj
