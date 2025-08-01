from typing import Optional, Set, Dict
from blarify.code_hierarchy.languages.FoundRelationshipScope import FoundRelationshipScope
from .language_definitions import LanguageDefinitions
from blarify.graph.relationship import RelationshipType
from blarify.graph.node import NodeLabels
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser, Node as TreeSitterNode




class CsharpDefinitions(LanguageDefinitions):
    CONTROL_FLOW_STATEMENTS = []
    CONSEQUENCE_STATEMENTS = []
    @staticmethod
    def get_language_name() -> str:
        return "csharp"

    @staticmethod
    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".cs": Parser(Language(tscsharp.language())),
        }

    @staticmethod
    def should_create_node(node: TreeSitterNode) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node,
            [
                "method_declaration",
                "class_declaration",
                "interface_declaration",
                "constructor_declaration",
                "record_declaration",
            ],
        )

    @staticmethod
    def get_identifier_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    @staticmethod
    def get_body_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    @staticmethod
    def get_relationship_type(node: TreeSitterNode, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        # This method should analyze tree-sitter nodes, not graph nodes
        # For now, return None as a placeholder - this needs proper implementation
        return None

    @staticmethod
    def get_node_label_from_type(type: str) -> "NodeLabels":
        from blarify.graph.node import NodeLabels
        return {
            "class_declaration": NodeLabels.CLASS,
            "method_declaration": NodeLabels.FUNCTION,
            "interface_declaration": NodeLabels.CLASS,
            "constructor_declaration": NodeLabels.FUNCTION,
            "record_declaration": NodeLabels.CLASS,
        }[type]

    @staticmethod
    def get_language_file_extensions() -> Set[str]:
        return {".cs"}

    @staticmethod
    def _find_relationship_type(node_label: str, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        relationship_types = CsharpDefinitions._get_relationship_types_by_label()
        # Convert string to NodeLabels enum
        node_label_enum = NodeLabels(node_label)
        relevant_relationship_types = relationship_types.get(node_label_enum, {})

        return LanguageDefinitions._traverse_and_find_relationships(
            node_in_point_reference, relevant_relationship_types
        )

    @staticmethod
    def _get_relationship_types_by_label() -> Dict[NodeLabels, Dict[str, RelationshipType]]:
        return {
            NodeLabels.CLASS: {
                "object_creation_expression": RelationshipType.INSTANTIATES,
                "using_directive": RelationshipType.IMPORTS,
                "variable_declaration": RelationshipType.TYPES,
                "parameter": RelationshipType.TYPES,
                "base_list": RelationshipType.INHERITS,
            },
            NodeLabels.FUNCTION: {
                "invocation_expression": RelationshipType.CALLS,
            },
        }
