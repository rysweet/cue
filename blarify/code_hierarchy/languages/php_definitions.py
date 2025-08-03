from typing import Dict, Optional, Set, TYPE_CHECKING
from tree_sitter import Language, Parser, Node as TreeSitterNode
from blarify.code_hierarchy.languages.FoundRelationshipScope import FoundRelationshipScope
from blarify.code_hierarchy.languages.language_definitions import LanguageDefinitions


import tree_sitter_php as tsphp

if TYPE_CHECKING:
    from blarify.graph.relationship import RelationshipType
    from blarify.graph.node import NodeLabels


class PhpDefinitions(LanguageDefinitions):
    """
    This class defines the PHP language server and its file extensions.
    """

    CONTROL_FLOW_STATEMENTS = ["if_statement", "while_statement", "for_statement"]
    CONSEQUENCE_STATEMENTS = ["compound_statement"]

    @staticmethod
    def get_language_name() -> str:
        return "php"

    @staticmethod
    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".php": Parser(Language(tsphp.language_php())),
        }

    @staticmethod
    def should_create_node(node: TreeSitterNode) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node, ["class_declaration", "function_definition", "method_declaration"]
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
        
        return {
            "class_declaration": NodeLabels.CLASS,
            "function_definition": NodeLabels.FUNCTION,
            "method_declaration": NodeLabels.FUNCTION,
        }[type]

    @staticmethod
    def get_language_file_extensions() -> Set[str]:
        return {".php"}
    
    @staticmethod
    def get_relationship_type(node: TreeSitterNode, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        return PhpDefinitions._find_relationship_type(
            node_label=node.type,
            node_in_point_reference=node_in_point_reference,
        )
    
    @staticmethod
    def _find_relationship_type(node_label: str, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        from blarify.graph.node import NodeLabels
        
        relationship_types = PhpDefinitions._get_relationship_types_by_label()
        # Convert string to NodeLabels enum
        node_label_enum = NodeLabels(node_label)
        relevant_relationship_types = relationship_types.get(node_label_enum, {})

        return LanguageDefinitions._traverse_and_find_relationships(
            node_in_point_reference, relevant_relationship_types
        )

    @staticmethod
    def _get_relationship_types_by_label() -> Dict["NodeLabels", Dict[str, "RelationshipType"]]:
        from blarify.graph.relationship import RelationshipType
        from blarify.graph.node import NodeLabels
        return {
            NodeLabels.CLASS: {
                "namespace_use_declaration": RelationshipType.IMPORTS,
                "base_clause": RelationshipType.INHERITS,
                "object_creation_expression": RelationshipType.INSTANTIATES,
                "typing": RelationshipType.TYPES,
                "simple_parameter": RelationshipType.TYPES,
            },
            NodeLabels.FUNCTION: {
                "function_call_expression": RelationshipType.CALLS,
                "member_call_expression": RelationshipType.CALLS,
                "namespace_use_declaration": RelationshipType.IMPORTS,
                "assignment_expression": RelationshipType.ASSIGNS,
            },
        }
