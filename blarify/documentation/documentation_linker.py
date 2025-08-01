import os
import logging
from typing import List, Dict, Any, TYPE_CHECKING
from difflib import SequenceMatcher

if TYPE_CHECKING:
    from blarify.graph.graph import Graph
    from blarify.graph.node import Node

logger = logging.getLogger(__name__)


class DocumentationLinker:
    """
    Links documentation nodes to relevant code nodes in the graph.
    
    This class finds matches between documented entities/concepts and actual code nodes,
    creating relationships between documentation and implementation.
    """
    
    def __init__(self):
        """Initialize the documentation linker."""
        pass
    
    def find_code_matches(self, doc_entity: Dict[str, Any], graph: "Graph") -> List["Node"]:
        """
        Find code nodes that match a documented entity.
        
        Args:
            doc_entity: Dictionary with entity information (name, type, description)
            graph: The code graph to search in
            
        Returns:
            List of matching code nodes
        """
        matches: List["Node"] = []
        entity_name = doc_entity.get("name", "")
        _entity_type = doc_entity.get("type", "")  # Future use for type-specific matching
        
        if not entity_name:
            return matches
        
        # Get all nodes from graph
        all_nodes = graph.get_all_nodes()
        
        for node in all_nodes:
            # Skip non-code nodes
            if hasattr(node, 'label') and node.label.value in ['DESCRIPTION', 'FILESYSTEM', 'FILESYSTEM_FILE', 
                                                               'FILESYSTEM_DIRECTORY', 'DOCUMENTATION_FILE', 
                                                               'CONCEPT', 'DOCUMENTED_ENTITY']:
                continue
            
            # Exact name match
            if node.name == entity_name:
                matches.append(node)
                continue
            
            # Case-insensitive match
            if node.name.lower() == entity_name.lower():
                matches.append(node)
                continue
            
            # Fuzzy matching for similar names
            similarity = self._calculate_similarity(entity_name, node.name)
            if similarity > 0.8:  # 80% similarity threshold
                matches.append(node)
        
        # Sort by relevance (exact matches first)
        matches.sort(key=lambda n: (n.name != entity_name, n.name.lower() != entity_name.lower()))
        
        return matches
    
    def find_code_matches_by_reference(self, code_ref: Dict[str, Any], graph: "Graph") -> List["Node"]:
        """
        Find code nodes based on explicit code references in documentation.
        
        Args:
            code_ref: Dictionary with code reference (text, type)
            graph: The code graph to search in
            
        Returns:
            List of matching code nodes
        """
        matches: List["Node"] = []
        ref_text = code_ref.get("text", "")
        ref_type = code_ref.get("type", "")
        
        if not ref_text:
            return matches
        
        all_nodes = graph.get_all_nodes()
        
        # Handle different reference types
        if ref_type == "file":
            matches.extend(self._find_nodes_by_path(ref_text, all_nodes))
        elif ref_type == "class":
            matches.extend(self._find_nodes_by_class_name(ref_text, all_nodes))
        elif ref_type == "method" or ref_type == "function":
            matches.extend(self._find_nodes_by_method_name(ref_text, all_nodes))
        else:
            # Try to infer type from reference text
            if '/' in ref_text or ref_text.endswith('.py') or ref_text.endswith('.js'):
                matches.extend(self._find_nodes_by_path(ref_text, all_nodes))
            elif '.' in ref_text and ref_text.count('.') == 1:
                # Might be ClassName.method
                class_name, method_name = ref_text.split('.')
                matches.extend(self._find_nodes_by_class_and_method(class_name, method_name, all_nodes))
            else:
                # Try as class or function name
                matches.extend(self._find_nodes_by_name(ref_text, all_nodes))
        
        return matches
    
    def link_concepts_to_code(self, concept: Dict[str, Any], graph: "Graph") -> List["Node"]:
        """
        Find code nodes that might implement a documented concept.
        
        Args:
            concept: Dictionary with concept information (name, description)
            graph: The code graph to search in
            
        Returns:
            List of code nodes that might implement the concept
        """
        matches: List["Node"] = []
        concept_name = concept.get("name", "").lower()
        _concept_desc = concept.get("description", "").lower()  # Future use for description-based matching
        
        # Keywords that suggest implementation
        implementation_keywords = [
            "pattern", "algorithm", "architecture", "design", "approach",
            "strategy", "factory", "singleton", "observer", "mvc", "mvvm"
        ]
        
        # Check if concept is a known pattern
        is_pattern = any(keyword in concept_name for keyword in implementation_keywords)
        
        all_nodes = graph.get_all_nodes()
        
        for node in all_nodes:
            # Skip non-code nodes
            if hasattr(node, 'label') and node.label.value not in ['CLASS', 'FUNCTION', 'METHOD', 'MODULE']:
                continue
            
            node_name_lower = node.name.lower()
            
            # Check if node name contains concept keywords
            if is_pattern:
                # For patterns, look for partial matches
                concept_words = concept_name.split()
                if any(word in node_name_lower for word in concept_words if len(word) > 3):
                    matches.append(node)
            else:
                # For other concepts, look for more specific matches
                if concept_name in node_name_lower or self._calculate_similarity(concept_name, node_name_lower) > 0.7:
                    matches.append(node)
        
        return matches
    
    def _find_nodes_by_path(self, path_ref: str, nodes: List["Node"]) -> List["Node"]:
        """Find nodes that match a file path reference."""
        matches: List["Node"] = []
        
        # Normalize path separators
        path_ref = path_ref.replace('\\', '/')
        
        for node in nodes:
            if hasattr(node, 'path'):
                node_path = node.path.replace('\\', '/')
                
                # Check if path reference is in node path
                if path_ref in node_path:
                    matches.append(node)
                elif node_path.endswith(path_ref):
                    matches.append(node)
                elif os.path.basename(node_path) == os.path.basename(path_ref):
                    matches.append(node)
        
        return matches
    
    def _find_nodes_by_class_name(self, class_name: str, nodes: List["Node"]) -> List["Node"]:
        """Find class nodes by name."""
        matches: List["Node"] = []
        
        for node in nodes:
            if hasattr(node, 'label') and node.label.value == 'CLASS':
                if node.name == class_name or node.name.lower() == class_name.lower():
                    matches.append(node)
        
        return matches
    
    def _find_nodes_by_method_name(self, method_name: str, nodes: List["Node"]) -> List["Node"]:
        """Find method or function nodes by name."""
        matches: List["Node"] = []
        
        # Remove parentheses if present
        method_name = method_name.replace('()', '').strip()
        
        for node in nodes:
            if hasattr(node, 'label') and node.label.value in ['METHOD', 'FUNCTION']:
                if node.name == method_name or node.name.lower() == method_name.lower():
                    matches.append(node)
        
        return matches
    
    def _find_nodes_by_class_and_method(self, class_name: str, method_name: str, nodes: List["Node"]) -> List["Node"]:
        """Find method nodes within a specific class."""
        matches: List["Node"] = []
        
        # First find the class
        class_nodes = self._find_nodes_by_class_name(class_name, nodes)
        
        # Then find methods within those classes
        for class_node in class_nodes:
            # Look for methods that are children of the class
            for node in nodes:
                if (hasattr(node, 'label') and node.label.value == 'METHOD' and
                    hasattr(node, 'parent') and node.parent == class_node and
                    (node.name == method_name or node.name.lower() == method_name.lower())):
                    matches.append(node)
        
        return matches
    
    def _find_nodes_by_name(self, name: str, nodes: List["Node"]) -> List["Node"]:
        """Find nodes by name regardless of type."""
        matches: List["Node"] = []
        
        for node in nodes:
            if node.name == name or node.name.lower() == name.lower():
                matches.append(node)
        
        return matches
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()