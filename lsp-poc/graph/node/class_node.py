from graph.node import NodeLabels, DefinitionNode

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from LSP.types import Reference


class ClassNode(DefinitionNode):
    name: str
    definition_range: "Reference"
    node_range: "Reference"
    code_text: str
    level: int

    def __init__(self, **kwargs):
        super().__init__(label=NodeLabels.CLASS, **kwargs)

    @property
    def node_repr_for_identifier(self) -> str:
        return "#" + self.name

    def as_object(self) -> dict:
        obj = super().as_object()
        obj["attributes"]["start_line"] = self.node_range.range.start.line
        obj["attributes"]["end_line"] = self.node_range.range.end.line
        obj["attributes"]["text"] = self.code_text
        return obj
