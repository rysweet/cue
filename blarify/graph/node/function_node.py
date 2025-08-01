from typing import Any, Dict, TYPE_CHECKING
from blarify.graph.node import NodeLabels
from .types.definition_node import DefinitionNode

if TYPE_CHECKING:
    from blarify.stats.complexity import CodeComplexityCalculator


class FunctionNode(DefinitionNode):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(label=NodeLabels.FUNCTION, **kwargs)

    @property
    def node_repr_for_identifier(self) -> str:
        return "." + self.name

    def as_object(self) -> Dict[str, Any]:
        obj = super().as_object()
        obj["attributes"]["start_line"] = self.node_range.range.start.line
        obj["attributes"]["end_line"] = self.node_range.range.end.line
        obj["attributes"]["text"] = self.code_text
        
        # Import here to avoid circular dependencies
        from blarify.stats.complexity import CodeComplexityCalculator
        obj["attributes"]["stats_parameter_count"] = CodeComplexityCalculator.calculate_parameter_count(self._tree_sitter_node)
        return obj
