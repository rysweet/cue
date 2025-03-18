from dataclasses import dataclass
import math
from statistics import stdev, mean


@dataclass
class NestingStats:
    max_indentation: int
    min_indentation: int
    average_indentation: float
    sd: float

class CodeComplexityCalculator:
    DEFAULT_INDENTATION = 4
    
    @staticmethod
    def calculate_nesting_stats(code: str):
        code.replace("\t", "    ")
        lines = code.splitlines()
        
        
        spaces_used_for_indentation = CodeComplexityCalculator.__calculate_number_of_spaces_used_as_indentation(code)
        
        indentation_per_line = [CodeComplexityCalculator.__count_indentation(line, spaces_used_for_indentation) for line in lines]
        
        if indentation_per_line == []:
            return NestingStats(0, 0, 0, 0)
        
        max_indentation = max(indentation_per_line)
        min_indentation = min(indentation_per_line)
        average_indentation = mean(indentation_per_line)
        sd = stdev(indentation_per_line) if len(indentation_per_line) > 1 else 0
        
        return NestingStats(max_indentation, min_indentation, average_indentation, sd)
        
    def __count_indentation(line: str, spaces_used_for_indentation: int):
        return math.ceil((len(line) - len(line.lstrip())) / spaces_used_for_indentation)
    
    def __calculate_number_of_spaces_used_as_indentation(code: str):
        lines = code.splitlines()
        
        
        for line in lines:
            indentation = len(line) - len(line.lstrip())
            if indentation > 0:
                return indentation
        
        return CodeComplexityCalculator.DEFAULT_INDENTATION
        
    

if __name__ == "__main__":
    code = """
def foo():
    if True:
        print("Hello")
    else:
        print("World")
"""
    stats = CodeComplexityCalculator.calculate_nesting_stats(code)
    print(stats)