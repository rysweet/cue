from typing import Dict, Set, Optional
from graph.node import Node as GraphNode, NodeLabels
from graph.relationship import RelationshipType

from tree_sitter import Parser, Node, Language
import tree_sitter_ruby as tsruby
from .language_definitions import LanguageDefinitions, BodyNodeNotFound


class RubyDefinitions(LanguageDefinitions):
    def get_language_name() -> str:
        return "ruby"

    def should_create_node(node: Node) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node, ["class", "method", "singleton_method"]
        )

    def get_identifier_node(node: Node) -> Node:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    def get_body_node(node: Node) -> Node:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    def get_node_label_from_type(type: str) -> NodeLabels:
        if type == "class":
            return NodeLabels.CLASS
        if type == "method":
            return NodeLabels.FUNCTION
        if type == "singleton_method":
            return NodeLabels.FUNCTION

    def get_relationship_type(node: GraphNode, node_in_point_reference: Node) -> Optional[RelationshipType]:
        return RubyDefinitions._find_relationship_type(
            node_label=node.label,
            node_in_point_reference=node_in_point_reference,
        )

    def _find_relationship_type(node_label: str, node_in_point_reference: Node) -> Optional[RelationshipType]:
        # Traverse up to find the named parent
        named_parent = node_in_point_reference
        rel_types = RubyDefinitions._get_relationship_types_by_label()
        type_found = None

        while named_parent is not None and type_found is None:
            if (
                named_parent.type == "call"
                and node_label == NodeLabels.CLASS
                and RubyDefinitions._is_call_method_indentifier_new(named_parent)
            ):
                return RelationshipType.INSTANTIATES

            type_found = RubyDefinitions._get_relationship_type_for_node(
                tree_sitter_node=named_parent, relationships_types=rel_types[node_label]
            )
            named_parent = named_parent.parent
        return type_found

    def _is_call_method_indentifier_new(node: Node) -> bool:
        return node.child_by_field_name("method").text == b"new"

    def _get_relationship_types_by_label() -> Dict[str, Dict[str, RelationshipType]]:
        return {
            NodeLabels.CLASS: {"superclass": RelationshipType.INHERITS},
            NodeLabels.FUNCTION: {
                "call": RelationshipType.CALLS,
            },
        }

    def _get_relationship_type_for_node(
        tree_sitter_node: Node, relationships_types: Dict[str, RelationshipType]
    ) -> Optional[RelationshipType]:
        if tree_sitter_node is None:
            return None

        for field_name, relationship_type in relationships_types.items():
            if tree_sitter_node.type == field_name:
                return relationship_type

        return None

    def get_language_file_extensions() -> Set[str]:
        return {".rb"}

    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".rb": Parser(Language(tsruby.language())),
        }
