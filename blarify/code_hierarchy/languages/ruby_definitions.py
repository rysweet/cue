from typing import Dict, Set, Optional, TYPE_CHECKING
from blarify.code_hierarchy.languages.FoundRelationshipScope import FoundRelationshipScope



from tree_sitter import Parser, Node as TreeSitterNode, Language
import tree_sitter_ruby as tsruby

if TYPE_CHECKING:
    from blarify.graph.relationship import RelationshipType
    from blarify.graph.node import NodeLabels
from .language_definitions import LanguageDefinitions


class RubyDefinitions(LanguageDefinitions):
    CONTROL_FLOW_STATEMENTS = ["for", "if", "elsif", "unless", "while"]
    CONSEQUENCE_STATEMENTS = ["do", "then"]

    @staticmethod
    def get_language_name() -> str:
        return "ruby"

    @staticmethod
    def should_create_node(node: TreeSitterNode) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node, ["class", "method", "singleton_method"]
        )

    @staticmethod
    def get_identifier_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    @staticmethod
    def get_body_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    @staticmethod
    def get_node_label_from_type(type: str) -> "NodeLabels":
        from blarify.graph.node import NodeLabels
        
        if type == "class":
            return NodeLabels.CLASS
        if type == "method":
            return NodeLabels.FUNCTION
        if type == "singleton_method":
            return NodeLabels.FUNCTION
        # If no match found, raise error instead of returning None
        raise ValueError(f"Unknown node type: {type}")

    @staticmethod
    def get_relationship_type(node: TreeSitterNode, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        return RubyDefinitions._find_relationship_type(
            node_label=node.type,
            node_in_point_reference=node_in_point_reference,
        )

    @staticmethod
    def _find_relationship_type(node_label: str, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        from blarify.graph.relationship import RelationshipType
        from blarify.graph.node import NodeLabels
        
        # Traverse up to find the named parent
        named_parent = node_in_point_reference
        rel_types = RubyDefinitions._get_relationship_types_by_label()
        found_relationship_scope = None

        while named_parent is not None and found_relationship_scope is None:
            if (
                named_parent.type == "call"
                and node_label == NodeLabels.CLASS
                and RubyDefinitions._is_call_method_indentifier_new(named_parent)
            ):
                return FoundRelationshipScope(
                    node_in_scope=named_parent, relationship_type=RelationshipType.INSTANTIATES
                )

            if named_parent.type == "assignment":
                return FoundRelationshipScope(node_in_scope=named_parent, relationship_type=RelationshipType.ASSIGNS)

            # Convert string to NodeLabels enum
            node_label_enum = NodeLabels(node_label)
            found_relationship_scope = RubyDefinitions._get_relationship_type_for_node(
                tree_sitter_node=named_parent, relationships_types=rel_types[node_label_enum]
            )

            named_parent = named_parent.parent
        return found_relationship_scope

    @staticmethod
    def _is_call_method_indentifier_new(node: TreeSitterNode) -> bool:
        method_node = node.child_by_field_name("method")
        return method_node is not None and method_node.text == b"new"

    @staticmethod
    def _get_relationship_types_by_label() -> Dict["NodeLabels", Dict[str, "RelationshipType"]]:
        from blarify.graph.relationship import RelationshipType
        from blarify.graph.node import NodeLabels
        return {
            NodeLabels.CLASS: {"superclass": RelationshipType.INHERITS},
            NodeLabels.FUNCTION: {
                "call": RelationshipType.CALLS,
            },
        }

    @staticmethod
    def _get_relationship_type_for_node(
        tree_sitter_node: Optional[TreeSitterNode], relationships_types: Dict[str, "RelationshipType"]
    ) -> Optional["RelationshipType"]:
        if tree_sitter_node is None:
            return None

        for field_name, relationship_type in relationships_types.items():
            if tree_sitter_node.type == field_name:
                return relationship_type

        return None

    @staticmethod
    def get_language_file_extensions() -> Set[str]:
        return {".rb"}

    @staticmethod
    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".rb": Parser(Language(tsruby.language())),
        }
