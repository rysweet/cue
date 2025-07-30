"""Cypher query builder for graph traversals."""

from typing import List, Dict, Any, Optional


class QueryBuilder:
    """Builds Cypher queries for various graph operations."""
    
    @staticmethod
    def find_files_query(file_paths: List[str]) -> str:
        """Build query to find FILE nodes by path."""
        # Handle both absolute and relative paths
        path_conditions = []
        for path in file_paths:
            # Match on path ending for flexibility
            path_conditions.append(f"n.path ENDS WITH '{path}'")
        
        where_clause = " OR ".join(path_conditions)
        
        return f"""
        MATCH (n:FILE)
        WHERE {where_clause}
        RETURN n
        """
    
    @staticmethod
    def get_file_context_query(file_path: str, max_depth: int = 2) -> str:
        """Build query to get comprehensive context for a file."""
        return f"""
        // Find the file node
        MATCH (file:FILE)
        WHERE file.path ENDS WITH $file_path
        
        // Get direct contents (classes, functions)
        OPTIONAL MATCH (file)-[:CONTAINS]->(content)
        WHERE content:CLASS OR content:FUNCTION
        
        // Get imports and dependencies
        OPTIONAL MATCH (file)-[:IMPORTS]->(imported)
        
        // Get files that import this file
        OPTIONAL MATCH (importer:FILE)-[:IMPORTS]->(file)
        
        // Get documentation nodes
        OPTIONAL MATCH (doc:DOCUMENTATION_FILE)-[:DOCUMENTS]->(file)
        
        // Get LLM descriptions if available
        OPTIONAL MATCH (file)<-[:DESCRIBES]-(file_desc:DESCRIPTION)
        OPTIONAL MATCH (content)<-[:DESCRIBES]-(content_desc:DESCRIPTION)
        
        // Get related filesystem nodes
        OPTIONAL MATCH (file)-[:HAS_FILE]->(fs:FILESYSTEM_FILE)
        
        RETURN file, 
               COLLECT(DISTINCT content) as contents,
               COLLECT(DISTINCT imported) as imports,
               COLLECT(DISTINCT importer) as importers,
               COLLECT(DISTINCT doc) as documentation,
               file_desc,
               COLLECT(DISTINCT content_desc) as content_descriptions,
               fs as filesystem_node
        """
    
    @staticmethod
    def find_symbol_query(symbol_name: str, symbol_type: Optional[str] = None) -> str:
        """Build query to find nodes matching a symbol name."""
        type_filter = ""
        if symbol_type:
            type_filter = f"AND (n:{symbol_type.upper()})"
        
        return f"""
        // Exact match
        MATCH (n)
        WHERE n.name = $symbol_name {type_filter}
        RETURN n, 'exact' as match_type
        
        UNION
        
        // Case-insensitive match
        MATCH (n)
        WHERE toLower(n.name) = toLower($symbol_name) {type_filter}
        RETURN n, 'case_insensitive' as match_type
        
        UNION
        
        // Contains match (for partial matches)
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower($symbol_name) {type_filter}
        RETURN n, 'partial' as match_type
        
        ORDER BY 
            CASE match_type 
                WHEN 'exact' THEN 0 
                WHEN 'case_insensitive' THEN 1 
                ELSE 2 
            END,
            size(n.name)
        LIMIT 10
        """
    
    @staticmethod
    def get_symbol_context_query(symbol_id: str) -> str:
        """Build query to get comprehensive context for a symbol."""
        return f"""
        // Find the symbol node
        MATCH (symbol)
        WHERE id(symbol) = $symbol_id
        
        // Get containing file
        OPTIONAL MATCH (file:FILE)-[:CONTAINS]->(symbol)
        
        // Get inheritance/implementation relationships
        OPTIONAL MATCH (symbol)-[:INHERITS_FROM]->(parent)
        OPTIONAL MATCH (symbol)-[:IMPLEMENTS]->(interface)
        OPTIONAL MATCH (child)-[:INHERITS_FROM]->(symbol)
        
        // Get method/attribute relationships for classes
        OPTIONAL MATCH (symbol)-[:HAS_METHOD]->(method:FUNCTION)
        OPTIONAL MATCH (symbol)-[:HAS_ATTRIBUTE]->(attr)
        
        // Get usage relationships
        OPTIONAL MATCH (caller)-[:CALLS]->(symbol)
        WHERE caller:FUNCTION OR caller:METHOD
        OPTIONAL MATCH (symbol)-[:CALLS]->(callee)
        
        // Get reference relationships
        OPTIONAL MATCH (referencer)-[:REFERENCES]->(symbol)
        
        // Get documentation
        OPTIONAL MATCH (doc:DOCUMENTATION_FILE)-[:DOCUMENTS]->(symbol)
        OPTIONAL MATCH (doc:DOCUMENTED_ENTITY {name: symbol.name})
        
        // Get LLM description
        OPTIONAL MATCH (symbol)<-[:DESCRIBES]-(description:DESCRIPTION)
        
        // Get related concepts
        OPTIONAL MATCH (symbol)-[:IMPLEMENTS_CONCEPT]->(concept:CONCEPT)
        
        RETURN symbol,
               file,
               COLLECT(DISTINCT parent) as parents,
               COLLECT(DISTINCT interface) as interfaces,
               COLLECT(DISTINCT child) as children,
               COLLECT(DISTINCT method) as methods,
               COLLECT(DISTINCT attr) as attributes,
               COLLECT(DISTINCT caller) as callers,
               COLLECT(DISTINCT callee) as callees,
               COLLECT(DISTINCT referencer) as referencers,
               COLLECT(DISTINCT doc) as documentation,
               description,
               COLLECT(DISTINCT concept) as concepts
        """
    
    @staticmethod
    def analyze_change_impact_query(entity_names: List[str]) -> str:
        """Build query to analyze impact of changing specific entities."""
        name_list = ", ".join([f"'{name}'" for name in entity_names])
        
        return f"""
        // Find all nodes matching the entity names
        MATCH (target)
        WHERE target.name IN [{name_list}]
        
        // Find direct dependencies
        OPTIONAL MATCH (target)<-[:CALLS|REFERENCES|IMPORTS|INHERITS_FROM|IMPLEMENTS]-(dependent)
        
        // Find containing files
        OPTIONAL MATCH (file:FILE)-[:CONTAINS]->(target)
        
        // Find test files
        OPTIONAL MATCH (test:FILE)-[:TESTS]->(target)
        WHERE test.path CONTAINS 'test'
        
        // Find related documentation
        OPTIONAL MATCH (doc:DOCUMENTATION_FILE)-[:DOCUMENTS]->(target)
        
        // Aggregate results
        RETURN target,
               COLLECT(DISTINCT dependent) as dependents,
               COLLECT(DISTINCT file) as containing_files,
               COLLECT(DISTINCT test) as test_files,
               COLLECT(DISTINCT doc) as documentation
        """
    
    @staticmethod
    def find_related_patterns_query(concept_name: str) -> str:
        """Build query to find code implementing specific patterns/concepts."""
        return f"""
        // Find concept nodes
        MATCH (concept:CONCEPT)
        WHERE concept.name CONTAINS $concept_name
        
        // Find implementing code
        OPTIONAL MATCH (implementer)-[:IMPLEMENTS_CONCEPT]->(concept)
        
        // Find related documentation
        OPTIONAL MATCH (doc:DOCUMENTATION_FILE)-[:CONTAINS_CONCEPT]->(concept)
        
        RETURN concept,
               COLLECT(DISTINCT implementer) as implementers,
               COLLECT(DISTINCT doc) as documentation
        """