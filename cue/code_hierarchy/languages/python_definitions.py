from typing import Optional, Set, Dict, TYPE_CHECKING
from cue.code_hierarchy.languages.FoundRelationshipScope import FoundRelationshipScope
from .language_definitions import LanguageDefinitions


import tree_sitter_python as tspython

if TYPE_CHECKING:
    from cue.graph.relationship import RelationshipType
    from cue.graph.node import NodeLabels
from tree_sitter import Language, Parser, Node as TreeSitterNode



class PythonDefinitions(LanguageDefinitions):
    CONTROL_FLOW_STATEMENTS = ["if_statement", "while_statement", "for_statement"]
    CONSEQUENCE_STATEMENTS = ["block"]

    @staticmethod
    def get_language_name() -> str:
        return "python"

    @staticmethod
    def get_parsers_for_extensions() -> Dict[str, Parser]:
        return {
            ".py": Parser(Language(tspython.language())),
        }

    @staticmethod
    def should_create_node(node: TreeSitterNode) -> bool:
        return LanguageDefinitions._should_create_node_base_implementation(
            node, ["class_definition", "function_definition"]
        )

    @staticmethod
    def get_identifier_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_identifier_node_base_implementation(node)

    @staticmethod
    def get_body_node(node: TreeSitterNode) -> TreeSitterNode:
        return LanguageDefinitions._get_body_node_base_implementation(node)

    @staticmethod
    def get_relationship_type(node: TreeSitterNode, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        return PythonDefinitions._find_relationship_type(
            node_label=node.type,
            node_in_point_reference=node_in_point_reference,
        )

    @staticmethod
    def get_node_label_from_type(type: str) -> "NodeLabels":
        from cue.graph.node import NodeLabels
        
        return {
            "class_definition": NodeLabels.CLASS,
            "function_definition": NodeLabels.FUNCTION,
        }[type]

    @staticmethod
    def get_language_file_extensions() -> Set[str]:
        return {".py"}

    @staticmethod
    def _find_relationship_type(node_label: str, node_in_point_reference: TreeSitterNode) -> Optional[FoundRelationshipScope]:
        from cue.graph.node import NodeLabels

        # Map legacy string labels to NodeLabels enum
        label_map = {
            "class_definition": NodeLabels.CLASS,
            "function_definition": NodeLabels.FUNCTION,
            "class": NodeLabels.CLASS,
            "function": NodeLabels.FUNCTION,
        }
        node_label_enum = label_map.get(node_label, None)
        if node_label_enum is None:
            try:
                node_label_enum = NodeLabels(node_label)
            except Exception:
                return None

        relationship_types = PythonDefinitions._get_relationship_types_by_label()
        relevant_relationship_types = relationship_types.get(node_label_enum, {})

        return LanguageDefinitions._traverse_and_find_relationships(
            node_in_point_reference, relevant_relationship_types
        )

    @staticmethod
    def _get_relationship_types_by_label() -> Dict["NodeLabels", Dict[str, "RelationshipType"]]:
        from cue.graph.relationship import RelationshipType
        from cue.graph.node import NodeLabels
        return {
            NodeLabels.CLASS: {
                "import_from_statement": RelationshipType.IMPORTS,
                "superclasses": RelationshipType.INHERITS,
                "call": RelationshipType.INSTANTIATES,
                "typing": RelationshipType.TYPES,
                "assignment": RelationshipType.TYPES,
            },
            NodeLabels.FUNCTION: {
                "call": RelationshipType.CALLS,
                "interpolation": RelationshipType.CALLS,
                "import_from_statement": RelationshipType.IMPORTS,
                "assignment": RelationshipType.ASSIGNS,
            },
        }
