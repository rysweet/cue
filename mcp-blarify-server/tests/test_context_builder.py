"""Tests for context builder."""

import pytest
from src.processors.context_builder import ContextBuilder


class TestContextBuilder:
    """Test context builder functionality."""
    
    @pytest.fixture
    def context_builder(self):
        """Create a context builder instance."""
        return ContextBuilder()
    
    def test_build_files_context_empty(self, context_builder):
        """Test building context with no files."""
        result = context_builder.build_files_context([])
        assert "No Files Found" in result
    
    def test_build_files_context_single_file(self, context_builder):
        """Test building context for a single file."""
        file_contexts = [{
            "file": {
                "path": "/src/main.py",
                "name": "main.py",
                "_labels": ["FILE"]
            },
            "contents": [
                {"name": "main", "_labels": ["FUNCTION"]},
                {"name": "App", "_labels": ["CLASS"]}
            ],
            "imports": [
                {"name": "os", "path": "os"},
                {"name": "sys", "path": "sys"}
            ]
        }]
        
        result = context_builder.build_files_context(file_contexts)
        assert "File: main.py" in result
        assert "Path**: `/src/main.py`" in result
        assert "FUNCTIONs: main" in result
        assert "CLASSs: App" in result
        assert "os" in result
        assert "sys" in result
    
    def test_build_symbol_context(self, context_builder):
        """Test building context for a symbol."""
        symbol_context = {
            "symbol": {
                "name": "UserService",
                "_labels": ["CLASS"],
                "_id": 123
            },
            "file": {
                "path": "/src/services/user_service.py"
            },
            "methods": [
                {"name": "create_user", "_labels": ["METHOD"]},
                {"name": "get_user", "_labels": ["METHOD"]}
            ],
            "callers": [
                {"name": "UserController", "path": "/src/controllers/user.py"}
            ]
        }
        
        result = context_builder.build_symbol_context(symbol_context)
        assert "Symbol: UserService" in result
        assert "Type**: CLASS" in result
        assert "Location**: `/src/services/user_service.py`" in result
        assert "create_user" in result
        assert "get_user" in result
        assert "Called by**: 1 locations" in result
    
    def test_build_change_plan_context(self, context_builder):
        """Test building context for change planning."""
        impact_analysis = {
            "UserService": {
                "target": {"name": "UserService"},
                "dependents": [{"name": "UserController"}],
                "containing_files": [{"path": "/src/services/user_service.py"}],
                "test_files": [{"path": "/tests/test_user_service.py"}]
            }
        }
        
        context = context_builder.build_change_plan_context(
            "Add email verification",
            impact_analysis
        )
        
        assert context["change_request"] == "Add email verification"
        assert context["affected_entities"] == ["UserService"]
        assert "/src/services/user_service.py" in context["affected_files"]
        assert "/tests/test_user_service.py" in context["test_files"]
        assert context["impact_summary"]["entities_affected"] == 1
    
    def test_truncate_context(self, context_builder):
        """Test context truncation."""
        # Create a long context
        long_text = "x" * (context_builder.max_context_length + 1000)
        
        result = context_builder._truncate_context(long_text)
        assert len(result) <= context_builder.max_context_length
        assert "context truncated" in result
    
    def test_group_by_type(self, context_builder):
        """Test grouping nodes by type."""
        nodes = [
            {"name": "func1", "_labels": ["FUNCTION"]},
            {"name": "func2", "_labels": ["FUNCTION"]},
            {"name": "Class1", "_labels": ["CLASS"]},
            {"name": "var1", "_labels": ["VARIABLE"]}
        ]
        
        grouped = context_builder._group_by_type(nodes)
        assert len(grouped["FUNCTION"]) == 2
        assert len(grouped["CLASS"]) == 1
        assert len(grouped["VARIABLE"]) == 1