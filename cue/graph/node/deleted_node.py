from typing import Any
from cue.graph.node.types.node import Node
from cue.utils.path_calculator import PathCalculator


class DeletedNode(Node):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def _identifier(self):
        if self.graph_environment is None:
            raise ValueError("graph_environment is None")
        return PathCalculator.compute_relative_path_with_prefix(self.pure_path, self.graph_environment.root_path)
