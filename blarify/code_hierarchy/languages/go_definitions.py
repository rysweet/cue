from typing import Optional, Set, Dict
from blarify.code_hierarchy.languages.FoundRelationshipScope import FoundRelationshipScope
from .language_definitions import LanguageDefinitions
from blarify.graph.relationship import RelationshipType
from blarify.graph.node import NodeLabels
import tree_sitter_go as tsgo
from tree_sitter import Language, Parser, Node as TreeSitterNode



class GoDefinitions(LanguageDefinitions):
    CONTROL_FLOW_STATEMENTS = []
    CONSEQUENCE_STATEMENTS = []
    
    @staticmethod
    def get_language_name() -> str:
        return "go"

    @staticmethod
    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".go": Parser(Language(tsgo.language())),
        }

    @staticmethod
    def should_create_node(node: TreeSitterNode) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node,
            ["type_spec", "type_alias", "method_declaration", "function_declaration"],
        )

    @staticmethod
    def get_identifier_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    @staticmethod
    def get_body_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    @staticmethod
    def get_relationship_type(node: TreeSitterNode, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        return GoDefinitions._find_relationship_type(
            node_label=node.type,
            node_in_point_reference=node_in_point_reference,
        )

    @staticmethod
    def get_node_label_from_type(type: str) -> "NodeLabels":
        from blarify.graph.node import NodeLabels
        return {
            "type_spec": NodeLabels.CLASS,
            "type_alias": NodeLabels.CLASS,
            "method_declaration": NodeLabels.FUNCTION,
            "function_declaration": NodeLabels.FUNCTION,
        }[type]

    @staticmethod
    def get_language_file_extensions() -> Set[str]:
        return {".go"}

    @staticmethod
    def _find_relationship_type(node_label: str, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        relationship_types = GoDefinitions._get_relationship_types_by_label()
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
                "import_declaration": RelationshipType.IMPORTS,
                "field_declaration": RelationshipType.TYPES,
                "composite_literal": RelationshipType.INSTANTIATES,
            },
            NodeLabels.FUNCTION: {
                "import_declaration": RelationshipType.IMPORTS,
                "call_expression": RelationshipType.CALLS,
            },
        }
