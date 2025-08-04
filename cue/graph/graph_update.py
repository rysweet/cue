from dataclasses import dataclass
from cue.graph.graph import Graph
from cue.graph.external_relationship_store import ExternalRelationshipStore
from typing import List, Dict, Any


@dataclass
class GraphUpdate:
    graph: Graph
    external_relationship_store: ExternalRelationshipStore

    def get_nodes_as_objects(self) -> List[Dict[str, Any]]:
        return self.graph.get_nodes_as_objects()

    def get_relationships_as_objects(self) -> List[Dict[str, Any]]:
        return (
            self.graph.get_relationships_as_objects() + self.external_relationship_store.get_relationships_as_objects()
        )
