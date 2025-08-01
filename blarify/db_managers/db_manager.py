from typing import List, Any
from abc import ABC, abstractmethod


class AbstractDbManager(ABC):
    @abstractmethod
    def close(self) -> None:
        """Close the connection to the database."""
        raise NotImplementedError

    @abstractmethod
    def save_graph(self, nodes: List[Any], edges: List[Any]) -> None:
        """Save nodes and edges to the database."""
        raise NotImplementedError

    @abstractmethod
    def create_nodes(self, nodeList: List[Any]) -> None:
        """Create nodes in the database."""
        raise NotImplementedError

    @abstractmethod
    def create_edges(self, edgesList: List[Any]) -> None:
        """Create edges between nodes in the database."""
        raise NotImplementedError

    @abstractmethod
    def detatch_delete_nodes_with_path(self, path: str) -> None:
        """Detach and delete nodes matching the given path."""
        raise NotImplementedError
