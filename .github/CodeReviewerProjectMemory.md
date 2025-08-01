# Code Reviewer Project Memory

Last Updated: 2025-08-01T20:35:00Z

This file maintains learnings and insights from code reviews to improve future reviews and maintain consistency.

## Code Review Memory - 2025-07-31

### PR #18: Improve test coverage for core modules

#### What I Learned
- The project uses pytest for testing with coverage reporting via pytest-cov
- Mock-based testing is preferred to avoid external dependencies (LSP servers, databases)
- Tests must be idempotent and manage their own resources
- Tree-sitter helper tests require careful mock setup due to parser initialization
- Graph filtering uses OR logic: relationships kept if either start OR end node is in paths_to_keep

#### Patterns to Watch
- Tests should follow Arrange-Act-Assert pattern for clarity
- Mock objects for nodes require specific attributes: id, path, label, relative_id
- Integration tests with actual language definitions provide better coverage than pure mocks
- Error simulation tests should cover realistic scenarios (ConnectionError, TimeoutError, etc.)

#### Common Issues
- Mock setup for tree-sitter parsing can be complex due to nested object structures
- LSP error handling tests need careful sequencing of side_effects
- Graph relationship filtering logic is not immediately intuitive (OR not AND)

---

## Project Architecture Insights

### Testing Infrastructure
- Tests located in `tests/` directory
- Fixtures in `tests/fixtures/` for reusable test components
- CI/CD uses GitHub Actions with Python 3.12
- Coverage threshold enforced in CI

### Key Modules and Their Responsibilities
- `blarify/code_hierarchy/tree_sitter_helper.py`: Parses code using tree-sitter
- `blarify/code_references/lsp_helper.py`: Manages LSP servers for symbol resolution
- `blarify/llm_descriptions/llm_service.py`: Handles LLM integration for descriptions
- `blarify/graph/graph.py`: Core graph operations and filtering

### Code Style and Conventions
- Python code formatted with Black
- Type hints encouraged but not universally enforced
- Docstrings follow Google style
- Error handling uses specific exceptions, not bare except

### Security Considerations
- Azure OpenAI keys managed via environment variables
- No credentials in code or test files
- Input validation required for all external data
- SQL parameterization used for database queries

---

## Review Guidelines Evolution

### Effective Review Practices
1. Check CI status before detailed review
2. Run tests locally when reviewing test changes
3. Verify mock objects match actual interfaces
4. Consider edge cases and error scenarios
5. Suggest specific improvements, not just identify issues

### Communication Patterns
- Use code blocks for specific suggestions
- Provide rationale for all requested changes
- Acknowledge good patterns and improvements
- Distinguish between critical issues and nice-to-haves

---

## Code Review Memory - 2025-08-01

### PR #19: feat: add specialized code review sub-agent for enhanced PR reviews

#### What I Learned
- Claude Code sub-agents require specific YAML frontmatter with name, description, and optional tools
- YAML tools should be specified as array format (- tool) not comma-separated string
- Sub-agent prompts should be comprehensive with clear responsibilities and structured processes
- Project memory files help maintain consistency across reviews and capture institutional knowledge
- Review formats should balance thoroughness with readability using emoji indicators

#### Patterns to Watch
- YAML frontmatter format consistency with Claude Code documentation
- Tool specifications should match available Claude Code tools exactly
- Memory file updates should be part of the sub-agent workflow
- Review checklists should be project-specific while covering universal quality standards

#### Good Practices Observed
- Comprehensive review checklist covering multiple dimensions (security, performance, testing)
- Clear prioritization of review issues (security > data corruption > performance)
- Structured review output format for consistency
- Integration of continuous learning through memory file updates
- Project-specific focus areas (graph operations, LSP integration, LLM handling)

---

## Future Improvements to Suggest
1. Increase type hint coverage across the codebase
2. Add mypy to CI pipeline for type checking
3. Create more integration tests for end-to-end scenarios
4. Document testing patterns in a dedicated guide
5. Consider property-based testing for complex logic

---

## Code Review Memory - 2025-08-01

### PR #19: feat: add specialized code review sub-agent for enhanced PR reviews

#### What I Learned
- Claude Code sub-agents require tools in comma-separated format with capitalized names (Read, Grep, etc.)
- Sub-agents must be placed in `.claude/agents/` directory with proper YAML frontmatter
- Not all standard Python development tools (bandit, safety, radon, pylint) are configured in every project
- Review priorities should align with team preferences (security > data corruption > performance confirmed)

#### Patterns to Watch
- YAML frontmatter formatting must match Claude Code documentation exactly
- Tool availability should be verified before recommending specific commands
- Memory files benefit from version/timestamp tracking
- Prompts in `/prompts/` are for planning, actual sub-agents go in `.claude/agents/`

#### Process Improvements
- Always verify tool configuration before including in review checklists
- Include "Last Updated" timestamps in memory files for tracking
- Separate implementation prompts from actual sub-agent definitions
- Test sub-agent invocation before finalizing implementation

---

## Code Review Memory - 2025-08-01

### PR #22: feat: implement WorkflowMaster sub-agent for workflow orchestration

#### What I Learned
- WorkflowMaster implements a comprehensive 9-phase workflow execution pattern for systematic development
- Claude Code sub-agents can coordinate with each other via explicit invocation patterns (e.g., `/agent:code-reviewer`)
- Workflow templates provide reusable patterns for different development scenarios (features vs bug fixes)
- State management through Memory.md enables graceful interruption and resumption of workflows
- TodoWrite tool integration enables real-time progress tracking throughout workflow execution
- Directory organization matters: `.claude/agents/` for agents, `.claude/docs/` for documentation, `.claude/templates/` for reusable patterns

#### Patterns to Watch
- YAML frontmatter in workflow-master.md follows correct format with proper tool specifications
- Error handling strategies should be comprehensive (git conflicts, test failures, CI/CD issues)
- Agent coordination requires explicit invocation syntax with proper agent naming
- Workflow phases should be executed in strict order to maintain quality gates
- State persistence patterns using Memory.md for workflow continuation

#### Architectural Insights
- WorkflowMaster serves as orchestrator for complete development lifecycles
- Integration with existing tools: GitHub CLI, TodoWrite, code-reviewer sub-agent
- Template-based approach enables standardization across different workflow types
- Quality standards enforcement through defined success criteria for each phase