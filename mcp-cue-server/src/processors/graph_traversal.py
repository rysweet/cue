"""Graph traversal logic for extracting context from Neo4j."""

from typing import List, Dict, Any, Optional
from neo4j import Driver
import logging

from ..config import Config
from ..tools.query_builder import QueryBuilder

logger = logging.getLogger(__name__)


class GraphTraversal:
    """Handles graph traversal operations."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
        self.query_builder = QueryBuilder()
    
    def find_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Find FILE nodes matching the given paths."""
        query = self.query_builder.find_files_query(file_paths)
        
        with self.driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run(query)
            files = []
            for record in result:
                node = record["n"]
                files.append(self._node_to_dict(node))
            return files
    
    def get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive context for a file."""
        query = self.query_builder.get_file_context_query(
            file_path, 
            Config.MAX_TRAVERSAL_DEPTH
        )
        
        with self.driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run(query, file_path=file_path)
            record = result.single()
            
            if not record:
                return {}
            
            context = {
                "file": self._node_to_dict(record["file"]),
                "contents": [self._node_to_dict(n) for n in record["contents"] if n],
                "imports": [self._node_to_dict(n) for n in record["imports"] if n],
                "importers": [self._node_to_dict(n) for n in record["importers"] if n],
                "documentation": [self._node_to_dict(n) for n in record["documentation"] if n],
                "description": self._node_to_dict(record["file_desc"]) if record["file_desc"] else None,
                "content_descriptions": [self._node_to_dict(n) for n in record["content_descriptions"] if n],
                "filesystem_node": self._node_to_dict(record["filesystem_node"]) if record["filesystem_node"] else None
            }
            
            return context
    
    def find_symbol(self, symbol_name: str, symbol_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find nodes matching a symbol name."""
        query = self.query_builder.find_symbol_query(symbol_name, symbol_type)
        
        with self.driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run(query, symbol_name=symbol_name)
            symbols = []
            for record in result:
                node = record["n"]
                match_type = record["match_type"]
                symbol_dict = self._node_to_dict(node)
                symbol_dict["match_type"] = match_type
                symbols.append(symbol_dict)
            return symbols
    
    def get_symbol_context(self, symbol_node_id: int) -> Dict[str, Any]:
        """Get comprehensive context for a symbol."""
        query = self.query_builder.get_symbol_context_query(str(symbol_node_id))
        
        with self.driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run(query, symbol_id=symbol_node_id)
            record = result.single()
            
            if not record:
                return {}
            
            context = {
                "symbol": self._node_to_dict(record["symbol"]),
                "file": self._node_to_dict(record["file"]) if record["file"] else None,
                "parents": [self._node_to_dict(n) for n in record["parents"] if n],
                "interfaces": [self._node_to_dict(n) for n in record["interfaces"] if n],
                "children": [self._node_to_dict(n) for n in record["children"] if n],
                "methods": [self._node_to_dict(n) for n in record["methods"] if n],
                "attributes": [self._node_to_dict(n) for n in record["attributes"] if n],
                "callers": [self._node_to_dict(n) for n in record["callers"] if n],
                "callees": [self._node_to_dict(n) for n in record["callees"] if n],
                "referencers": [self._node_to_dict(n) for n in record["referencers"] if n],
                "documentation": [self._node_to_dict(n) for n in record["documentation"] if n],
                "description": self._node_to_dict(record["description"]) if record["description"] else None,
                "concepts": [self._node_to_dict(n) for n in record["concepts"] if n]
            }
            
            return context
    
    def analyze_change_impact(self, entity_names: List[str]) -> Dict[str, Any]:
        """Analyze the impact of changing specific entities."""
        query = self.query_builder.analyze_change_impact_query(entity_names)
        
        with self.driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run(query)
            
            impacts = {}
            for record in result:
                target = self._node_to_dict(record["target"])
                target_name = target.get("name", target.get("path", "unknown"))
                
                impacts[target_name] = {
                    "target": target,
                    "dependents": [self._node_to_dict(n) for n in record["dependents"] if n],
                    "containing_files": [self._node_to_dict(n) for n in record["containing_files"] if n],
                    "test_files": [self._node_to_dict(n) for n in record["test_files"] if n],
                    "documentation": [self._node_to_dict(n) for n in record["documentation"] if n]
                }
            
            return impacts
    
    def find_patterns(self, concept_name: str) -> Dict[str, Any]:
        """Find code implementing specific patterns or concepts."""
        query = self.query_builder.find_related_patterns_query(concept_name)
        
        with self.driver.session(database=Config.NEO4J_DATABASE) as session:
            result = session.run(query, concept_name=concept_name)
            
            patterns = []
            for record in result:
                pattern = {
                    "concept": self._node_to_dict(record["concept"]),
                    "implementers": [self._node_to_dict(n) for n in record["implementers"] if n],
                    "documentation": [self._node_to_dict(n) for n in record["documentation"] if n]
                }
                patterns.append(pattern)
            
            return {"patterns": patterns}
    
    def _node_to_dict(self, node) -> Optional[Dict[str, Any]]:
        """Convert a Neo4j node to a dictionary."""
        if not node:
            return None
        
        # Get all properties
        props = dict(node)
        
        # Add node metadata
        props["_id"] = node.id
        props["_labels"] = list(node.labels)
        
        return props
    
    def get_extended_context(self, start_nodes: List[Dict[str, Any]], depth: int = 2) -> Dict[str, Any]:
        """Get extended context by traversing from start nodes."""
        # This would implement a more sophisticated traversal
        # For now, we'll use the specific context methods
        extended_context = {
            "nodes": start_nodes,
            "relationships": [],
            "depth": depth
        }
        
        # TODO: Implement generic traversal logic
        return extended_context