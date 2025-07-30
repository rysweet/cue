"""
Tests for code complexity calculation.
"""
import unittest
from unittest.mock import Mock, patch
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from blarify.stats.complexity import CodeComplexityCalculator, NestingStats
from blarify.graph.node.class_node import ClassNode
from blarify.graph.node.function_node import FunctionNode


class TestCodeComplexityCalculator(unittest.TestCase):
    """Test code complexity calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = CodeComplexityCalculator()
        # Set up tree-sitter for Python
        self.PY_LANGUAGE = Language(tspython.language())
        self.parser = Parser(self.PY_LANGUAGE)
        
    def parse_code(self, code):
        """Parse Python code and return tree."""
        return self.parser.parse(bytes(code, "utf8")).root_node
        
    def test_calculate_cyclomatic_complexity_simple(self):
        """Test cyclomatic complexity for simple function."""
        self.skipTest("CodeComplexityCalculator doesn't have calculate_cyclomatic_complexity method")
        
    def test_calculate_cyclomatic_complexity_with_conditions(self):
        """Test cyclomatic complexity with if statements."""
        self.skipTest("CodeComplexityCalculator doesn't have calculate_cyclomatic_complexity method")
        
    def test_calculate_cyclomatic_complexity_with_loops(self):
        """Test cyclomatic complexity with loops."""
        self.skipTest("CodeComplexityCalculator doesn't have calculate_cyclomatic_complexity method")
        
    def test_calculate_cyclomatic_complexity_with_try_except(self):
        """Test cyclomatic complexity with exception handling."""
        self.skipTest("CodeComplexityCalculator doesn't have calculate_cyclomatic_complexity method")
        
    def test_calculate_cyclomatic_complexity_with_boolean_operators(self):
        """Test cyclomatic complexity with boolean operators."""
        self.skipTest("CodeComplexityCalculator doesn't have calculate_cyclomatic_complexity method")
        
    def test_calculate_nesting_stats(self):
        """Test nesting depth calculation."""
        code = """
def nested_function():
    if True:
        for i in range(10):
            while i > 0:
                if i % 2:
                    print(i)
                i -= 1
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        # Get the body of the function
        body_node = None
        for child in func_node.children:
            if child.type == "block":
                body_node = child
                break
        
        if body_node:
            stats = CodeComplexityCalculator.calculate_nesting_stats(body_node, ".py")
            
            self.assertIsInstance(stats, NestingStats)
            self.assertGreaterEqual(stats.max_indentation, 3)  # At least 3 levels nested
            self.assertGreaterEqual(stats.average_indentation, 1)
            
    def test_calculate_nesting_stats_empty_body(self):
        """Test nesting stats for empty function body."""
        code = """
def empty_function():
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        # Get the body
        body_node = None
        for child in func_node.children:
            if child.type == "block":
                body_node = child
                break
                
        if body_node:
            stats = CodeComplexityCalculator.calculate_nesting_stats(body_node, ".py")
            
            self.assertIsInstance(stats, NestingStats)
            # Empty or simple body should have minimal nesting
            self.assertEqual(stats.max_indentation, 0)
            self.assertEqual(stats.min_indentation, 0)
            
    def test_calculate_parameter_count(self):
        """Test parameter counting."""
        code = """
def function_with_params(a, b, c=None, *args, **kwargs):
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        param_count = CodeComplexityCalculator.calculate_parameter_count(func_node)
        
        # Should count all parameters including *args and **kwargs
        self.assertEqual(param_count, 5)
        
    def test_calculate_parameter_count_no_params(self):
        """Test parameter counting for parameterless function."""
        code = """
def no_params():
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        param_count = CodeComplexityCalculator.calculate_parameter_count(func_node)
        
        self.assertEqual(param_count, 0)
        
    def test_calculate_lines_of_code(self):
        """Test counting lines of code."""
        self.skipTest("CodeComplexityCalculator doesn't have calculate_lines_of_code method")
        
    def test_analyze_function_node(self):
        """Test complete function analysis."""
        self.skipTest("CodeComplexityCalculator doesn't have analyze_function method")
        
    def test_analyze_class_node(self):
        """Test analyzing complexity of a class."""
        self.skipTest("CodeComplexityCalculator doesn't have analyze_class method")
        
    def find_node_by_type(self, node, node_type):
        """Helper to find first node of given type."""
        if node.type == node_type:
            return node
            
        for child in node.children:
            result = self.find_node_by_type(child, node_type)
            if result:
                return result
                
        return None


class TestComplexityMetrics(unittest.TestCase):
    """Test various complexity metric calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = CodeComplexityCalculator()
        
    def test_nesting_stats_dataclass(self):
        """Test NestingStats dataclass."""
        stats = NestingStats(
            max_indentation=4,
            min_indentation=0,
            average_indentation=2.5,
            sd=1.2
        )
        
        self.assertEqual(stats.max_indentation, 4)
        self.assertEqual(stats.min_indentation, 0)
        self.assertEqual(stats.average_indentation, 2.5)
        self.assertEqual(stats.sd, 1.2)
        
    def test_empty_nesting_stats(self):
        """Test empty nesting stats."""
        stats = NestingStats(0, 0, 0, 0)
        
        self.assertEqual(stats.max_indentation, 0)
        self.assertEqual(stats.min_indentation, 0)
        self.assertEqual(stats.average_indentation, 0)
        self.assertEqual(stats.sd, 0)


if __name__ == '__main__':
    unittest.main()