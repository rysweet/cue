We have forked a program called Blarify that uses tree-sitter and language server protocol servers to create a graph of a codebase AST and its bindings to symbols. This is a powerful tool for understanding code structure and relationships. Analyze this code base and remember its structure so that you can make plans about improving its test coverage.

## Problem Statement

The Blarify codebase has grown significantly with new features like filesystem nodes, documentation parsing, LLM descriptions, and MCP server integration. However, test coverage has not kept pace with feature development. Many critical modules lack comprehensive tests, making it difficult to ensure reliability and catch regressions. Without proper test coverage, bugs can slip into production, refactoring becomes risky, and new developers struggle to understand expected behavior.

Current testing gaps include:
1. Core graph operations and node/relationship management
2. Language-specific parsing and tree-sitter integration  
3. Database operations with Neo4j and FalkorDB
4. LLM integration and error handling
5. File system traversal and gitignore handling
6. MCP server functionality
7. Edge cases and error conditions

## Feature Overview

We will systematically improve test coverage across the Blarify codebase to achieve >80% coverage while ensuring all tests are idempotent, isolated, and suitable for CI/CD pipelines. The tests will use fixtures for consistent setup, mock external dependencies, and provide clear documentation of expected behavior.

The improvement will:
1. Measure current test coverage using Python's coverage tool
2. Identify modules with low or missing coverage
3. Write comprehensive unit and integration tests
4. Set up test database configurations isolated from dev/production
5. Create reusable fixtures and test utilities
6. Implement CI/CD pipeline with coverage reporting
7. Ensure all tests are idempotent and manage their own resources

## Technical Analysis

### Current Testing Infrastructure
- Tests exist in `tests/` and `mcp-blarify-server/tests/` directories
- Using Python's unittest framework
- Some tests for filesystem nodes, documentation parsing, LLM service
- No systematic coverage measurement or CI/CD integration
- Missing test database configuration

### Key Testing Requirements
1. **Isolation**: Tests must not affect dev/production databases or file systems
2. **Idempotency**: Tests must produce same results on repeated runs
3. **Speed**: Full test suite should complete in <5 minutes
4. **Clarity**: Test names and docstrings should document behavior
5. **Coverage**: Achieve >80% code coverage with meaningful tests

### Critical Modules Needing Tests

#### Core Graph Components
- `blarify/graph/graph.py`: Graph operations, node/relationship management
- `blarify/graph/node/*.py`: All node types and their serialization
- `blarify/graph/relationship/*.py`: Relationship creation and validation
- `blarify/graph/graph_update.py`: Graph update operations

#### Language Processing
- `blarify/code_hierarchy/languages/*.py`: Language definitions
- `blarify/code_hierarchy/tree_sitter_helper.py`: Tree-sitter integration
- `blarify/vendor/multilspy/*.py`: LSP server integration

#### Database Layer
- `blarify/db_managers/*.py`: Neo4j and FalkorDB operations
- Transaction handling and rollback
- Connection pooling and error recovery

#### File System Operations
- `blarify/project_file_explorer/*.py`: File traversal, gitignore
- `blarify/filesystem/*.py`: Filesystem graph generation
- Path handling and permission errors

#### LLM Integration
- `blarify/llm_descriptions/*.py`: Description generation
- API error handling and retries
- Prompt construction and response parsing

#### Documentation Processing
- `blarify/documentation/*.py`: Documentation parsing and linking
- Concept extraction and entity recognition

## Implementation Plan

### Phase 1: Infrastructure Setup

#### Coverage Measurement
1. Add coverage to pyproject.toml dependencies
2. Create .coveragerc configuration file
3. Set up coverage commands in project scripts
4. Generate initial coverage report to baseline

#### Test Database Configuration
1. Create `tests/conftest.py` with pytest fixtures
2. Set up test Neo4j container using testcontainers
3. Configure environment variables for test database
4. Implement database setup/teardown fixtures

#### CI/CD Pipeline
1. Create `.github/workflows/tests.yml`
2. Configure matrix testing for Python 3.10-3.12
3. Add coverage reporting with threshold checks
4. Cache dependencies for faster builds

### Phase 2: Test Implementation

#### Test Structure Template
```python
import unittest
from unittest.mock import Mock, patch
import tempfile
import shutil
from blarify.tests.fixtures import TestGraphFixture, create_test_file

class TestModuleName(unittest.TestCase):
    """Test suite for module functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.graph = TestGraphFixture()
        
    def tearDown(self):
        """Clean up test resources."""
        shutil.rmtree(self.test_dir)
        self.graph.cleanup()
    
    def test_happy_path(self):
        """Test normal operation with valid inputs."""
        # Arrange
        # Act  
        # Assert
        
    def test_edge_case(self):
        """Test behavior with edge case inputs."""
        # Test empty, None, boundary values
        
    def test_error_handling(self):
        """Test proper error handling and recovery."""
        # Test exceptions, timeouts, invalid data
```

#### Module-by-Module Testing

For each untested module:
1. Analyze module's public interface and dependencies
2. Create comprehensive test file following template
3. Test all public methods and functions
4. Include edge cases and error conditions
5. Mock external dependencies (databases, APIs, file system)
6. Verify test coverage locally before committing

### Phase 3: Test Quality Assurance

#### Test Fixtures and Utilities
Create `tests/fixtures/` directory with:
- `graph_fixtures.py`: Common graph structures for testing
- `node_factories.py`: Factory functions for test nodes
- `file_fixtures.py`: Test file creation utilities
- `mock_responses.py`: Mocked API responses for LLM, LSP

#### Integration Test Suite
Create end-to-end tests that verify:
- Complete graph building pipeline
- Multi-language project processing
- Documentation extraction and linking
- MCP server query handling

#### Performance Tests
- Benchmark graph operations with large datasets
- Test memory usage and cleanup
- Verify query performance

### Phase 4: Documentation and Maintenance

#### Test Documentation
1. Update README with test running instructions
2. Document test database setup
3. Create testing best practices guide
4. Add inline documentation to complex tests

#### Continuous Monitoring
1. Set up coverage trend tracking
2. Add pre-commit hooks for test runs
3. Create coverage badges for README
4. Regular review of flaky tests

## Success Criteria

The test coverage improvement is successful when:
1. Overall code coverage exceeds 80%
2. All critical modules have >90% coverage
3. Tests run reliably in CI/CD pipeline
4. Test suite completes in <5 minutes
5. No flaky tests (100% pass rate over 10 runs)
6. Clear documentation for running and writing tests
7. Test database configuration is fully isolated
8. All tests are idempotent and resource-safe

## Implementation Steps

Once you have analyzed the codebase and this plan:

1. **Create GitHub Issue**: Create an issue in https://github.com/rysweet/cue describing the test coverage improvement initiative with detailed plan
2. **Create Feature Branch**: Create branch `feature/test-coverage-improvement` and switch to it
3. **Set Up Infrastructure**: Install coverage tools, create test database config, set up CI/CD
4. **Measure Baseline**: Run coverage analysis and document current state
5. **Implement Tests Module by Module**: Start with most critical, least tested modules
6. **Create Test Fixtures**: Build reusable test infrastructure
7. **Add Integration Tests**: Create end-to-end test scenarios
8. **Update Documentation**: Document test setup and best practices
9. **Verify CI/CD**: Ensure all tests pass in GitHub Actions
10. **Create Pull Request**: Submit PR with comprehensive test improvements

Commit changes incrementally as you implement each component, with clear commit messages describing what was tested.

## Example Test Implementation

```python
# tests/test_graph_operations.py
import unittest
from unittest.mock import Mock, patch
from blarify.graph.graph import Graph
from blarify.graph.node.file_node import FileNode
from blarify.graph.relationship.relationship_type import RelationshipType
from tests.fixtures.graph_fixtures import create_test_graph

class TestGraphOperations(unittest.TestCase):
    """Test suite for core graph operations."""
    
    def setUp(self):
        """Set up test graph instance."""
        self.graph = create_test_graph()
        
    def test_add_node_success(self):
        """Test adding a node to the graph."""
        node = FileNode(
            path="file:///test/main.py",
            name="main.py",
            level=1
        )
        
        self.graph.add_node(node)
        
        retrieved = self.graph.get_node_by_id(node.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "main.py")
        
    def test_add_duplicate_node(self):
        """Test that duplicate nodes are handled correctly."""
        node1 = FileNode(path="file:///test/main.py", name="main.py", level=1)
        node2 = FileNode(path="file:///test/main.py", name="main.py", level=1)
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        # Should only have one node with this path
        nodes = self.graph.get_nodes_by_label("FILE")
        matching = [n for n in nodes if n.path == "file:///test/main.py"]
        self.assertEqual(len(matching), 1)
```

Once the work is complete, create a pull request on https://github.com/rysweet/cue to merge the branch into main, and review it carefully before merging.