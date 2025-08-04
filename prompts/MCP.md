We have forked a program called Blarify that uses tree-sitter and language server protocol servers to create a graph of a codebase AST and its bindings to symbols. This is a powerful tool for understanding code structure and relationships. Analyze this code base and remember its structure so that you can make plans about the new features we will add.

## Problem Statement

AI coding agents need sophisticated tools to understand and navigate complex codebases. While Blarify creates rich graph representations of code structure in Neo4j, there's currently no standardized way for AI agents to query and analyze this data. The Model Context Protocol (MCP) provides a standard for exposing tools to AI agents, but Blarify lacks an MCP server to bridge this gap.

AI agents struggle with:
1. Understanding the full context around specific code elements
2. Tracking dependencies and relationships across large codebases
3. Planning complex changes that affect multiple interconnected components
4. Accessing structured knowledge about code architecture and design patterns

## Feature Overview

We will build an MCP server that sits in front of the Neo4j graph database, providing a set of MCP tools that AI coding agents can use to query the graph and retrieve information about the codebase. The server will expose sophisticated query capabilities and use LLM-powered analysis to provide coherent, contextual information.

The MCP server will:
1. Leverage existing Neo4j MCP servers as a foundation
2. Provide custom tools for context retrieval and change planning
3. Use LLM to organize and structure query results into consumable Markdown
4. Handle complex multi-hop graph traversals intelligently
5. Support both Cypher queries and high-level semantic operations

## Technical Foundation

### Base MCP Servers
We'll build upon:
- **neo4j-contrib/mcp-neo4j-cypher**: Provides base Cypher query execution
- **neo4j-contrib/gds-agent**: Offers graph data science capabilities

### Custom MCP Tools

#### 1. `getContextForFiles`
**Purpose**: Retrieve comprehensive context for a list of files
**Input**: Array of file paths
**Process**:
- Execute Cypher queries to find FILE nodes matching the paths
- Traverse graph to configurable depth (default: 2-3 hops)
- Collect related nodes: classes, functions, dependencies, imports, documentation
- Include LLM summaries, filesystem relationships, and documentation links
- Use LLM to organize results into coherent Markdown structure

**Output Structure**:
```markdown
# Context for Files

## File: src/services/auth.py
### Overview
[LLM summary if available]

### Contains
- **Classes**: AuthService, TokenValidator
- **Functions**: authenticate(), validate_token()

### Dependencies
- Imports: jwt, datetime, User model
- Imported by: api/routes/auth.py, tests/test_auth.py

### Related Documentation
- docs/authentication.md describes the authentication flow
- README.md mentions AuthService configuration

### Related Concepts
- Implements: JWT Authentication pattern
- Part of: Security Module
```

#### 2. `getContextForSymbol`
**Purpose**: Retrieve context for a specific symbol (class, function, variable)
**Input**: Symbol name and optional type hint
**Process**:
- Search for nodes matching the symbol name
- Use fuzzy matching for variations
- Traverse to find definitions, usages, and relationships
- Include inheritance chains, implementations, and callers
- Gather documentation references and LLM descriptions

**Output Structure**:
```markdown
# Context for Symbol: UserService

## Definition
- **Type**: Class
- **Location**: src/services/user_service.py:45
- **Description**: [LLM summary]

## Implementation Details
### Methods
- `create_user(data: dict) -> User`
- `get_user(id: int) -> Optional[User]`
- `update_user(id: int, data: dict) -> User`

### Dependencies
- Inherits from: BaseService
- Uses: UserRepository, ValidationHelper
- Database: users table

### Usage
- Used by: UserController (api/controllers/user.py)
- Tests: tests/services/test_user_service.py
- Examples: docs/examples/user_management.md

### Related Patterns
- Implements: Repository Pattern
- Part of: Domain Model
```

#### 3. `buildPlanForChange`
**Purpose**: Analyze codebase and create implementation plan for a change request
**Input**: Change description/requirements
**Process**:
- Use LLM to extract entities and concepts from change request
- Query graph to find relevant existing code
- Analyze dependencies and impact radius
- Identify files to modify, create, or delete
- Consider test files and documentation updates
- Order changes by dependency

**Output Structure**:
```markdown
# Implementation Plan: Add Email Verification

## Summary
Add email verification to the user registration process.

## Impact Analysis
- **Affected Components**: UserService, AuthController, User model
- **New Components Needed**: EmailVerificationService, email templates
- **Database Changes**: Add `email_verified` column to users table

## Implementation Steps

### 1. Database Migration
- **File**: migrations/add_email_verification.sql
- **Action**: Create
- **Description**: Add email_verified boolean and verification_token fields

### 2. Update User Model
- **File**: src/models/user.py
- **Action**: Modify
- **Changes**: 
  - Add email_verified property
  - Add verification_token property
  - Update validation logic

### 3. Create Email Service
- **File**: src/services/email_service.py
- **Action**: Create
- **Description**: Service for sending verification emails

### 4. Update Registration Flow
- **File**: src/services/user_service.py
- **Action**: Modify
- **Changes**:
  - Generate verification token on registration
  - Send verification email
  - Add verify_email method

### 5. Add Verification Endpoint
- **File**: api/routes/auth.py
- **Action**: Modify
- **Changes**: Add /verify-email endpoint

### 6. Update Tests
- **Files**: 
  - tests/services/test_user_service.py
  - tests/api/test_auth.py
- **Action**: Modify
- **Changes**: Add tests for email verification flow

### 7. Update Documentation
- **File**: docs/authentication.md
- **Action**: Modify
- **Changes**: Document email verification process

## Dependencies to Consider
- Email service configuration (SMTP settings)
- Email template system
- Token expiration handling
- Rate limiting for email sends
```

## Implementation Requirements

### MCP Server Structure
```
mcp-cue-server/
├── src/
│   ├── server.py          # Main MCP server
│   ├── tools/
│   │   ├── context_tools.py    # getContextForFiles, getContextForSymbol
│   │   ├── planning_tools.py   # buildPlanForChange
│   │   └── query_builder.py    # Cypher query construction
│   ├── processors/
│   │   ├── graph_traversal.py  # Graph traversal logic
│   │   ├── context_builder.py  # Context organization
│   │   └── llm_processor.py    # LLM integration
│   └── config.py
├── tests/
├── requirements.txt
└── README.md
```

### Configuration
- Neo4j connection settings (host, port, credentials)
- Azure OpenAI configuration for LLM processing
- Traversal depth limits
- Context size limits
- Cache settings for frequent queries

### Neo4j Query Patterns
Efficient Cypher queries for:
1. Multi-hop traversals with relationship filtering
2. Full-text search across node properties
3. Pattern matching for code structures
4. Aggregation of related nodes by type

### LLM Integration
- Use Azure OpenAI to:
  1. Parse change requests into structured queries
  2. Organize graph results into coherent narratives
  3. Generate implementation step descriptions
  4. Identify implicit dependencies

### Error Handling
- Graceful handling of missing nodes
- Query timeout management
- LLM fallback for failed processing
- Clear error messages for AI agents

## Testing Strategy

1. **Unit Tests**: Test individual query builders and processors
2. **Integration Tests**: Test with sample Neo4j graphs
3. **End-to-End Tests**: Test MCP tool invocations
4. **LLM Mock Tests**: Test with mocked LLM responses

## Implementation Plan

1. Set up MCP server scaffold based on neo4j-cypher server
2. Implement basic Neo4j connection and query execution
3. Build graph traversal and context extraction logic
4. Integrate LLM for result processing
5. Implement the three custom tools
6. Add comprehensive error handling
7. Write tests for all components
8. Create documentation and usage examples
9. Package for deployment

Once you have analyzed the codebase and this plan, create an issue in the remote repo (https://github.com/rysweet/cue) to describe the feature. Then create a new branch, implement the MCP server following test-driven development practices, and create a pull request when complete.