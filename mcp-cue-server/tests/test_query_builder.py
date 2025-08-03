"""Tests for query builder."""

from src.tools.query_builder import QueryBuilder


class TestQueryBuilder:
    """Test query builder functionality."""
    
    def test_find_files_query(self):
        """Test file finding query construction."""
        qb = QueryBuilder()
        
        # Single file
        query = qb.find_files_query(["src/main.py"])
        assert "MATCH (n:FILE)" in query
        assert "n.path ENDS WITH 'src/main.py'" in query
        
        # Multiple files
        query = qb.find_files_query(["src/main.py", "tests/test_main.py"])
        assert "n.path ENDS WITH 'src/main.py'" in query
        assert "n.path ENDS WITH 'tests/test_main.py'" in query
        assert " OR " in query
    
    def test_get_file_context_query(self):
        """Test file context query construction."""
        qb = QueryBuilder()
        query = qb.get_file_context_query("src/main.py", max_depth=2)
        
        # Check main components
        assert "MATCH (file:FILE)" in query
        assert "file.path ENDS WITH $file_path" in query
        assert "(file)-[:CONTAINS]->(content)" in query
        assert "(file)-[:IMPORTS]->(imported)" in query
        assert "(importer:FILE)-[:IMPORTS]->(file)" in query
        assert "(doc:DOCUMENTATION_FILE)-[:DOCUMENTS]->(file)" in query
        assert "RETURN file" in query
    
    def test_find_symbol_query(self):
        """Test symbol finding query construction."""
        qb = QueryBuilder()
        
        # Without type filter
        query = qb.find_symbol_query("UserService")
        assert "n.name = $symbol_name" in query
        assert "toLower(n.name) = toLower($symbol_name)" in query
        assert "toLower(n.name) CONTAINS toLower($symbol_name)" in query
        assert "UNION" in query
        
        # With type filter
        query = qb.find_symbol_query("UserService", "class")
        assert "AND (n:CLASS)" in query
    
    def test_get_symbol_context_query(self):
        """Test symbol context query construction."""
        qb = QueryBuilder()
        query = qb.get_symbol_context_query("123")
        
        # Check relationships
        assert "id(symbol) = $symbol_id" in query
        assert "(file:FILE)-[:CONTAINS]->(symbol)" in query
        assert "(symbol)-[:INHERITS_FROM]->(parent)" in query
        assert "(symbol)-[:HAS_METHOD]->(method:FUNCTION)" in query
        assert "(caller)-[:CALLS]->(symbol)" in query
        assert "RETURN symbol" in query
    
    def test_analyze_change_impact_query(self):
        """Test change impact analysis query."""
        qb = QueryBuilder()
        query = qb.analyze_change_impact_query(["UserService", "AuthController"])
        
        assert "target.name IN ['UserService', 'AuthController']" in query
        assert "(target)<-[:CALLS|REFERENCES|IMPORTS|INHERITS_FROM|IMPLEMENTS]-(dependent)" in query
        assert "(file:FILE)-[:CONTAINS]->(target)" in query
        assert "(test:FILE)-[:TESTS]->(target)" in query
        assert "test.path CONTAINS 'test'" in query
    
    def test_find_related_patterns_query(self):
        """Test pattern finding query."""
        qb = QueryBuilder()
        query = qb.find_related_patterns_query("Repository Pattern")
        
        assert "MATCH (concept:CONCEPT)" in query
        assert "concept.name CONTAINS $concept_name" in query
        assert "(implementer)-[:IMPLEMENTS_CONCEPT]->(concept)" in query
        assert "(doc:DOCUMENTATION_FILE)-[:CONTAINS_CONCEPT]->(concept)" in query