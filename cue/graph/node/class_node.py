from typing import TYPE_CHECKING, Any, Dict
from cue.graph.node.types.node_labels import NodeLabels
from cue.graph.node.types.definition_node import DefinitionNode

if TYPE_CHECKING:
    from cue.code_references.types import Reference


class ClassNode(DefinitionNode):
    name: str
    definition_range: "Reference"
    node_range: "Reference"
    code_text: str
    level: int

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(label=NodeLabels.CLASS, **kwargs)

    @property
    def node_repr_for_identifier(self) -> str:
        return "#" + self.name

    def as_object(self) -> Dict[str, Any]:
        obj = super().as_object()
        obj["attributes"]["start_line"] = self.node_range.range.start.line
        obj["attributes"]["end_line"] = self.node_range.range.end.line
        obj["attributes"]["text"] = self.code_text
        obj["attributes"]["stats_methods_defined"] = sum(1 for node in self._defines if node.label == NodeLabels.FUNCTION)
        return obj
