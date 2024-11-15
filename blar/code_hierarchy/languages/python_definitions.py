from .language_definitions import LanguageDefinitions
from graph.relationship import RelationshipType

import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from typing import Optional, Set, Dict

from graph.node import NodeLabels
from tree_sitter import Node
from graph.node import Node as GraphNode


class PythonDefinitions(LanguageDefinitions):
    def get_language_name() -> str:
        return "python"

    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".py": Parser(Language(tspython.language())),
        }

    def should_create_node(node: Node) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node, ["class_definition", "function_definition"]
        )

    def get_identifier_node(node: Node) -> Node:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    def get_body_node(node: Node) -> Node:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    def get_relationship_type(node: GraphNode, node_in_point_reference: Node) -> Optional[RelationshipType]:
        return PythonDefinitions._find_relationship_type(
            node_label=node.label,
            node_in_point_reference=node_in_point_reference,
        )

    def get_node_label_from_type(type: str) -> NodeLabels:
        return {
            "class_definition": NodeLabels.CLASS,
            "function_definition": NodeLabels.FUNCTION,
        }[type]

    def get_language_file_extensions() -> Set[str]:
        return {".py"}

    def _find_relationship_type(node_label: str, node_in_point_reference: Node) -> Optional[RelationshipType]:
        relationship_types = PythonDefinitions._get_relationship_types_by_label()
        relevant_relationship_types = relationship_types.get(node_label, {})

        return LanguageDefinitions._traverse_and_find_relationships(
            node_in_point_reference, relevant_relationship_types
        )

    def _get_relationship_types_by_label() -> dict[str, RelationshipType]:
        return {
            NodeLabels.CLASS: {
                "import_from_statement": RelationshipType.IMPORTS,
                "superclasses": RelationshipType.INHERITS,
                "call": RelationshipType.INSTANTIATES,
                "typing": RelationshipType.TYPING,
                "assignment": RelationshipType.ASSIGNMENT,
            },
            NodeLabels.FUNCTION: {
                "call": RelationshipType.CALLS,
                "interpolation": RelationshipType.CALLS,
                "import_from_statement": RelationshipType.IMPORTS,
                "assignment": RelationshipType.ASSIGNMENT,
            },
        }
