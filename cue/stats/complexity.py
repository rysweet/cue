from dataclasses import dataclass
from statistics import stdev, mean
from tree_sitter import Node
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from cue.code_hierarchy.languages.language_definitions import LanguageDefinitions


@dataclass
class NestingStats:
    max_indentation: int
    min_indentation: int
    average_indentation: float
    sd: float


class CodeComplexityCalculator:
    DEFAULT_INDENTATION = 4

    @staticmethod
    def calculate_nesting_stats(node: Node, extension: str) -> NestingStats:
        # Import here to avoid circular dependencies
        language_definitions = CodeComplexityCalculator._get_language_definitions(extension)
        if not language_definitions:
            return NestingStats(0, 0, 0, 0)

        indentation_per_line = CodeComplexityCalculator.__get_nesting_levels(node, language_definitions)

        if indentation_per_line == []:
            return NestingStats(0, 0, 0, 0)

        max_indentation = max(indentation_per_line)
        min_indentation = min(indentation_per_line)
        average_indentation = mean(indentation_per_line)
        sd = stdev(indentation_per_line) if len(indentation_per_line) > 1 else 0

        return NestingStats(max_indentation, min_indentation, average_indentation, sd)
    
    @staticmethod
    def _get_language_definitions(extension: str) -> Optional["LanguageDefinitions"]:
        """Get language definitions for an extension without circular imports."""
        from cue.code_hierarchy.languages import get_language_definition
        
        # Map of file extensions to language names
        extension_to_language = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.rb': 'ruby',
            '.cs': 'csharp',
            '.go': 'go',
            '.php': 'php',
            '.java': 'java',
        }
        
        language_name = extension_to_language.get(extension)
        if not language_name:
            return None
            
        definition_class = get_language_definition(language_name)
        if definition_class:
            return definition_class()
        return None

    @staticmethod
    def __get_nesting_levels(node: Node, language_definitions: "LanguageDefinitions") -> list[int]:
        depths: list[int] = []

        for child in node.named_children:
            if not language_definitions.should_create_node(child):
                depths.append(CodeComplexityCalculator.__calculate_max_nesting_depth(child, language_definitions))

        return depths

    @staticmethod
    def __calculate_max_nesting_depth(node: Node, language_definitions: "LanguageDefinitions") -> int:
        consequence_statements: List[str] = getattr(language_definitions, 'CONSEQUENCE_STATEMENTS', [])
        control_flow_statements: List[str] = getattr(language_definitions, 'CONTROL_FLOW_STATEMENTS', [])

        depths: list[int] = []
        depth = 0
        for child in node.named_children:
            if language_definitions.should_create_node(child):
                continue

            if child.type in control_flow_statements or child.type in consequence_statements:
                depth += CodeComplexityCalculator.__calculate_max_nesting_depth(child, language_definitions)
                if child.type in consequence_statements:
                    depth += 1

            depths.append(depth)
            depth = 0

        return max(depths) if depths else 0
    
    @staticmethod
    def calculate_parameter_count(node: Node) -> int:
        """
        Calculate the number of parameters in a function definition node.
        """
        # Remove unreachable code - node parameter is typed as Node, not Optional[Node]
        
        if parameters_node := node.child_by_field_name("parameters"):
            return len(parameters_node.named_children)
        return 0


if __name__ == "__main__":
    code = """
def foo():
    if True:
        print("Hello")
    else:
        print("World")
"""
    # Fix: missing extension parameter
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser
    
    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(bytes(code, "utf8"))
    
    stats = CodeComplexityCalculator.calculate_nesting_stats(tree.root_node, ".py")
    print(stats)
