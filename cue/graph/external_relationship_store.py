from typing import List, Dict, Any
from cue.graph.relationship.external_relationship import ExternalRelationship
from cue.graph.relationship.relationship_type import RelationshipType


class ExternalRelationshipStore:
    def __init__(self):
        self.relationships: List[ExternalRelationship] = []

    def add_relationship(self, relationship: ExternalRelationship):
        self.relationships.append(relationship)

    def create_and_add_relationship(self, start_node_id: str, end_node_id: str, rel_type: RelationshipType):
        relationship = ExternalRelationship(start_node_id, end_node_id, rel_type)
        self.add_relationship(relationship)

    def get_relationships_as_objects(self) -> List[Dict[str, Any]]:
        return [relationship.as_object() for relationship in self.relationships]
