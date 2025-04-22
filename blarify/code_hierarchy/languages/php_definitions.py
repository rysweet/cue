from typing import Dict, Set
from tree_sitter import Language, Node, Parser
from blarify.code_hierarchy.languages.language_definitions import LanguageDefinitions
import tree_sitter_php as tsphp

from blarify.graph.node.types.node_labels import NodeLabels


class PhpDefinitions(LanguageDefinitions):
    """
    This class defines the PHP language server and its file extensions.
    """

    CONTROL_FLOW_STATEMENTS = ["if_statement", "while_statement", "for_statement"]
    CONSEQUENCE_STATEMENTS = ["block"]

    def get_language_name() -> str:
        return "php"

    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".php": Parser(Language(tsphp.language_php())),
        }

    def should_create_node(node: Node) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node, ["class_delaration", "function_definition", "method_declaration"]
        )

    def get_identifier_node(node: Node) -> Node:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    def get_body_node(node: Node) -> Node:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    def get_node_label_from_type(type: str) -> NodeLabels:
        return {
            "class_declaration": NodeLabels.CLASS,
            "function_definition": NodeLabels.FUNCTION,
            "method_declaration": NodeLabels.FUNCTION,
        }[type]

    def get_language_file_extensions() -> Set[str]:
        return {".php"}
