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
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        
    def parse_code(self, code):
        """Helper to parse Python code."""
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree.root_node
        
    def test_calculate_cyclomatic_complexity_simple(self):
        """Test cyclomatic complexity for simple function."""
        code = """
def simple_function(x):
    return x + 1
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        complexity = self.calculator.calculate_cyclomatic_complexity(func_node)
        
        # Simple function has complexity of 1
        self.assertEqual(complexity, 1)
        
    def test_calculate_cyclomatic_complexity_with_conditions(self):
        """Test cyclomatic complexity with if statements."""
        code = """
def function_with_conditions(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        return -x
    else:
        return 0
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        complexity = self.calculator.calculate_cyclomatic_complexity(func_node)
        
        # Should count: 1 base + 3 if/elif + 1 nested if = 5
        self.assertEqual(complexity, 5)
        
    def test_calculate_cyclomatic_complexity_with_loops(self):
        """Test cyclomatic complexity with loops."""
        code = """
def function_with_loops(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
        elif item < -10:
            break
    
    while total > 100:
        total = total / 2
        
    return total
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        complexity = self.calculator.calculate_cyclomatic_complexity(func_node)
        
        # Should count: 1 base + 1 for + 1 if + 1 elif + 1 while = 5
        self.assertEqual(complexity, 5)
        
    def test_calculate_cyclomatic_complexity_with_try_except(self):
        """Test cyclomatic complexity with exception handling."""
        code = """
def function_with_exceptions(x):
    try:
        result = 10 / x
        if result > 5:
            return result
    except ZeroDivisionError:
        return 0
    except ValueError:
        return -1
    finally:
        print("Done")
    
    return result
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        complexity = self.calculator.calculate_cyclomatic_complexity(func_node)
        
        # Should count: 1 base + 1 if + 2 except = 4
        self.assertGreaterEqual(complexity, 4)
        
    def test_calculate_cyclomatic_complexity_with_boolean_operators(self):
        """Test cyclomatic complexity with boolean operators."""
        code = """
def function_with_boolean_logic(a, b, c):
    if a and b or c:
        return True
    
    if a or (b and not c):
        return False
        
    return None
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        complexity = self.calculator.calculate_cyclomatic_complexity(func_node)
        
        # Should count boolean operators in conditions
        self.assertGreater(complexity, 3)
        
    def test_calculate_nesting_depth_flat(self):
        """Test nesting depth for flat function."""
        code = """
def flat_function():
    x = 1
    y = 2
    return x + y
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        stats = self.calculator.calculate_nesting_depth(func_node)
        
        self.assertEqual(stats.max_depth, 0)
        self.assertEqual(stats.average_depth, 0)
        
    def test_calculate_nesting_depth_nested(self):
        """Test nesting depth with nested structures."""
        code = """
def nested_function(data):
    for item in data:
        if item > 0:
            for i in range(item):
                if i % 2 == 0:
                    print(i)
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        stats = self.calculator.calculate_nesting_depth(func_node)
        
        # Maximum nesting: for -> if -> for -> if = 4
        self.assertEqual(stats.max_depth, 4)
        self.assertGreater(stats.average_depth, 0)
        
    def test_calculate_nesting_depth_with_functions(self):
        """Test nesting depth with nested function definitions."""
        code = """
def outer_function():
    def inner_function():
        def deeply_nested():
            if True:
                return 1
        return deeply_nested
    
    return inner_function
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        stats = self.calculator.calculate_nesting_depth(func_node)
        
        # Should count nested function definitions
        self.assertGreater(stats.max_depth, 2)
        
    def test_count_parameters_no_params(self):
        """Test parameter counting for parameterless function."""
        code = """
def no_params():
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        count = self.calculator.count_parameters(func_node)
        
        self.assertEqual(count, 0)
        
    def test_count_parameters_simple(self):
        """Test parameter counting for simple parameters."""
        code = """
def simple_params(a, b, c):
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        count = self.calculator.count_parameters(func_node)
        
        self.assertEqual(count, 3)
        
    def test_count_parameters_with_defaults(self):
        """Test parameter counting with default values."""
        code = """
def params_with_defaults(a, b=10, c=None):
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        count = self.calculator.count_parameters(func_node)
        
        self.assertEqual(count, 3)
        
    def test_count_parameters_with_args_kwargs(self):
        """Test parameter counting with *args and **kwargs."""
        code = """
def variadic_params(a, *args, b=1, **kwargs):
    pass
"""
        
        tree = self.parse_code(code)
        func_node = self.find_node_by_type(tree, "function_definition")
        
        count = self.calculator.count_parameters(func_node)
        
        # Should count: a + *args + b + **kwargs = 4
        self.assertEqual(count, 4)
        
    def test_count_lines_of_code(self):
        """Test counting lines of code."""
        code = """
def example_function():
    # This is a comment
    x = 1
    
    # Another comment
    y = 2
    
    return x + y
"""
        
        lines = self.calculator.count_lines_of_code(code)
        
        # Should count only non-empty, non-comment lines
        self.assertEqual(lines, 4)  # def, x=1, y=2, return
        
    def test_analyze_function_node(self):
        """Test complete function analysis."""
        code = """
def complex_function(a, b, c=None):
    '''A complex function for testing.'''
    result = 0
    
    for i in range(a):
        if i % 2 == 0:
            result += i
        else:
            for j in range(b):
                if j > i:
                    result -= j
                    
    if c is not None:
        result *= c
        
    return result
"""
        
        # Create a function node
        func_node = FunctionNode(
            id="test_func",
            name="complex_function",
            path="file:///test.py",
            level=1,
            start_line=1,
            end_line=17
        )
        
        # Mock file reading
        with patch.object(self.calculator, 'get_function_code', return_value=code):
            metrics = self.calculator.analyze_function(func_node)
            
        self.assertIn('cyclomatic_complexity', metrics)
        self.assertIn('nesting_depth', metrics)
        self.assertIn('parameter_count', metrics)
        self.assertIn('lines_of_code', metrics)
        
        self.assertGreater(metrics['cyclomatic_complexity'], 3)
        self.assertEqual(metrics['parameter_count'], 3)
        self.assertGreater(metrics['lines_of_code'], 5)
        
    def test_analyze_class_node(self):
        """Test analyzing complexity of a class."""
        code = """
class ExampleClass:
    def __init__(self, value):
        self.value = value
        
    def simple_method(self):
        return self.value
        
    def complex_method(self, x):
        if x > 0:
            for i in range(x):
                if i % 2 == 0:
                    yield i
        else:
            return []
"""
        
        # Create a class node
        class_node = ClassNode(
            id="test_class",
            name="ExampleClass",
            path="file:///test.py",
            level=1,
            start_line=1,
            end_line=15
        )
        
        with patch.object(self.calculator, 'get_class_code', return_value=code):
            metrics = self.calculator.analyze_class(class_node)
            
        self.assertIn('method_count', metrics)
        self.assertIn('total_complexity', metrics)
        self.assertIn('average_complexity', metrics)
        self.assertIn('max_complexity', metrics)
        
        self.assertEqual(metrics['method_count'], 3)  # __init__, simple_method, complex_method
        self.assertGreater(metrics['total_complexity'], 3)
        
    def find_node_by_type(self, node, node_type):
        """Helper to find first node of given type."""
        if node.type == node_type:
            return node
            
        for child in node.children:
            result = self.find_node_by_type(child, node_type)
            if result:
                return result
                
        return None


class TestNestingStats(unittest.TestCase):
    """Test NestingStats data class."""
    
    def test_nesting_stats_creation(self):
        """Test creating NestingStats instance."""
        stats = NestingStats(max_depth=3, average_depth=1.5)
        
        self.assertEqual(stats.max_depth, 3)
        self.assertEqual(stats.average_depth, 1.5)
        
    def test_nesting_stats_defaults(self):
        """Test NestingStats with default values."""
        stats = NestingStats()
        
        self.assertEqual(stats.max_depth, 0)
        self.assertEqual(stats.average_depth, 0.0)


if __name__ == '__main__':
    unittest.main()