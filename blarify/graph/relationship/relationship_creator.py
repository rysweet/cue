from typing import List, TYPE_CHECKING, Any
from blarify.graph.relationship.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType

if TYPE_CHECKING:
    from blarify.graph.graph import Graph
    from blarify.graph.node.types.node import Node
    from blarify.code_references.types import Reference


class RelationshipCreator:
    @staticmethod
    def create_relationships_from_paths_where_node_is_referenced(
        references: list["Reference"], node: "Node", graph: "Graph", tree_sitter_helper: Any
    ) -> List[Relationship]:
        relationships: List[Relationship] = []
        for reference in references:
            file_node_reference = graph.get_file_node_by_path(path=reference.uri)
            if file_node_reference is None:
                continue

            node_referenced = file_node_reference.reference_search(reference=reference)
            if node.id == node_referenced.id:
                continue

            # Ensure both nodes are DefinitionNodes for get_reference_type
            if not hasattr(node, 'tree_sitter_node') or not hasattr(node_referenced, 'tree_sitter_node'):
                continue

            # Use node directly since we verified it has tree_sitter_node attribute
            found_relationship_scope = tree_sitter_helper.get_reference_type(
                original_node=node, reference=reference, node_referenced=node_referenced
            )

            if found_relationship_scope is None:
                continue

            if found_relationship_scope.node_in_scope is None:
                scope_text = ""
            else:
                # Handle potential None case for node_in_scope.text
                node_text = found_relationship_scope.node_in_scope.text
                scope_text = node_text.decode("utf-8") if node_text is not None else ""

            relationship = Relationship(
                start_node=node_referenced,
                end_node=node,
                rel_type=found_relationship_scope.relationship_type,
                scope_text=scope_text,
            )

            relationships.append(relationship)
        return relationships

    @staticmethod
    def _get_relationship_type(defined_node: "Node") -> RelationshipType:
        # Import at runtime to avoid circular dependencies
        from blarify.graph.node.types.node_labels import NodeLabels
        
        if defined_node.label == NodeLabels.FUNCTION:
            return RelationshipType.FUNCTION_DEFINITION
        elif defined_node.label == NodeLabels.CLASS:
            return RelationshipType.CLASS_DEFINITION
        else:
            raise ValueError(f"Node {defined_node.label} is not a valid definition node")

    @staticmethod
    def create_defines_relationship(node: "Node", defined_node: "Node") -> Relationship:
        rel_type = RelationshipCreator._get_relationship_type(defined_node)
        return Relationship(
            node,
            defined_node,
            rel_type,
        )

    @staticmethod
    def create_contains_relationship(folder_node: "Node", contained_node: "Node") -> Relationship:
        return Relationship(
            folder_node,
            contained_node,
            RelationshipType.CONTAINS,
        )
