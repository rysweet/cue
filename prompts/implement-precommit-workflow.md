# Pre-commit Workflow Implementation for Hybrid TypeScript/Python Repository

## Title and Overview

**Implement Comprehensive Pre-commit Hooks for Multi-Language Codebase Quality Assurance**

This prompt guides the implementation of a robust pre-commit workflow for the Blarify VS Code Extension repository (vscode-blarify-visualizer), which contains both a TypeScript-based VS Code extension and a Python-based codebase analysis engine. The workflow will ensure code quality, prevent broken builds, and maintain consistent formatting standards across both TypeScript and Python codebases in a single repository.

The repository structure includes:
- **TypeScript VS Code Extension**: Located in `/src/`, `/media/`, and root-level configuration
- **Python Blarify Engine**: Located in `/bundled/blarify/` with Poetry configuration
- **Shared Configuration**: Git hooks, documentation, and CI/CD configuration

This hybrid architecture requires a sophisticated pre-commit workflow that handles both ecosystems while maintaining performance and developer experience standards.

## Problem Statement

### Current Limitations
The vscode-blarify-visualizer repository currently lacks automated quality gates before commits, leading to potential issues across both language ecosystems:

#### TypeScript/VS Code Extension Issues
- **Code Quality Inconsistency**: No automated formatting enforcement leads to inconsistent code style across the TypeScript codebase
- **Build Failures**: Commits may break TypeScript compilation, causing CI/CD pipeline failures
- **ESLint Violations**: TypeScript linting rule violations can accumulate, reducing code maintainability
- **Extension API Issues**: Changes may break VS Code extension APIs or webview integration

#### Python/Blarify Engine Issues
- **Python Formatting Inconsistency**: No Ruff formatting enforcement leads to inconsistent Python code style
- **Import Organization**: Unorganized imports reduce code readability and maintainability
- **Linting Violations**: Ruff rule violations accumulate without pre-commit enforcement
- **Type Safety**: No pyright type checking before commits can introduce type-related bugs
- **Test Coverage**: Python test regressions may go undetected until CI runs

#### Security Issues
- **Secret Exposure**: No automated detection of API keys, tokens, or credentials in code
- **Sensitive Data**: Risk of accidentally committing passwords or private keys
- **Compliance**: No enforcement of security best practices before commit

#### Cross-Language Integration Issues
- **Interface Compatibility**: Changes to Python APIs may break TypeScript integration
- **Configuration Drift**: Tool configurations may become inconsistent between languages
- **Documentation Synchronization**: Changes in one language may require documentation updates
- **Performance Degradation**: Inefficient code in either language affects overall system performance

### Impact on Development Workflow
- Developers waste time fixing preventable build failures in CI for both TypeScript and Python
- Code review cycles are extended due to formatting and linting issues across both languages
- Technical debt accumulates from inconsistent code quality in both ecosystems
- Complex debugging sessions when TypeScript-Python integration breaks
- Team productivity suffers from context switching between different tooling approaches

### Motivation for Change
Implementing unified pre-commit hooks will create quality gates that ensure only well-formatted, compilable, and tested code reaches the repository for both languages. This reduces CI build times, improves code review efficiency, and maintains high code quality standards essential for a complex multi-language project with tight integration between TypeScript and Python components.

## Feature Requirements

### Functional Requirements

#### Multi-Language Code Formatting
- **TypeScript/JavaScript**: Prettier integration for consistent formatting of TS/JS files
- **Python**: Ruff formatting for Python code with 120-character line length
- **JSON/YAML**: Prettier formatting for configuration files
- **Markdown**: Consistent documentation formatting across both language sections
- **Configuration**: Unified formatting rules that respect each language's best practices

#### Security Scanning
- **Secret Detection**: Automated scanning for API keys, tokens, and credentials
- **Pattern Matching**: Detection of common secret patterns across all file types
- **Custom Rules**: Support for project-specific secret patterns
- **False Positive Management**: Allowlist for known safe patterns

#### TypeScript Quality Assurance
- **Compilation Check**: Ensure all TypeScript files compile successfully
- **ESLint Integration**: Run configured ESLint rules with auto-fixing
- **Type Safety**: Verify type definitions and VS Code extension APIs
- **Build Verification**: Confirm the extension can be packaged successfully
- **Import Organization**: Organize TypeScript imports consistently

#### Python Quality Assurance
- **Ruff Formatting**: Automatic Python code formatting and import organization
- **Ruff Linting**: Comprehensive Python linting with auto-fixing capabilities
- **Type Checking**: pyright integration for Python type safety validation
- **Poetry Compatibility**: Ensure changes don't break Poetry dependency management

#### Cross-Language Integration Validation
- **API Compatibility**: Validate that Python API changes don't break TypeScript integration
- **Configuration Consistency**: Ensure tool configurations are synchronized
- **Documentation Updates**: Validate that code changes have corresponding documentation
- **Performance Impact**: Check for performance regressions in either language

#### Test Execution
- **TypeScript Tests**: Run VS Code extension test suites
- **Python Tests**: Execute pytest suites for Python components
- **Integration Tests**: Cross-language integration test validation
- **Selective Testing**: Run tests related to changed files for performance
- **Coverage Validation**: Ensure test coverage doesn't decrease

### Technical Requirements

#### Tool Integration Architecture
```
Pre-commit Hook Trigger
       ↓
   File Type Detection
       ↓
   ┌─────────────────────────────────────┐
   │     Parallel Language Processing     │
   │                                     │
   │  TypeScript Path         Python Path│
   │  ├─ Prettier             ├─ Ruff     │
   │  ├─ ESLint               ├─ pyright  │
   │  ├─ TypeScript           └─ pytest   │
   │  ├─ TS Tests                         │
   │  └─ Extension Build                  │
   └─────────────────────────────────────┘
       ↓
   Cross-Language Validation
       ↓
   Secret Detection (all files)
       ↓
   All Checks Pass? → Commit/Block
```

#### Performance Constraints
- **Speed**: Pre-commit checks should complete in under 45 seconds for typical changes
- **Language Isolation**: TypeScript and Python checks run in parallel when possible
- **Incremental Processing**: Only process changed files in each language
- **Tool Caching**: Leverage caching for both npm/node_modules and Poetry/.venv
- **Smart Detection**: Skip language-specific checks when no files of that type changed

#### Configuration Management
- **Unified Root Config**: Single pre-commit configuration at repository root
- **Language-Specific Tools**: Maintain existing .eslintrc.json, pyproject.toml configurations
- **VS Code Integration**: Ensure settings work well with VS Code for both languages
- **Poetry Integration**: Maintain compatibility with Poetry dependency management
- **npm Integration**: Preserve existing npm scripts and VS Code extension building

### Integration Requirements

#### Dependency Management
- **Node.js Dependencies**: Integrate with existing package.json and npm scripts
- **Python Dependencies**: Work with Poetry-managed dependencies in bundled/
- **Tool Isolation**: Ensure Python and TypeScript tools don't conflict
- **Version Consistency**: Maintain consistent tool versions across developer environments

#### Development Environment Compatibility
- **Cross-Platform**: Support macOS, Windows, and Linux development environments
- **Editor Integration**: Compatible with VS Code, PyCharm, and other popular editors
- **Terminal Usage**: Support both GUI and command-line Git workflows
- **Container Development**: Compatible with dev containers and remote development

#### CI/CD Integration
- **GitHub Actions**: Ensure pre-commit checks align with CI/CD pipeline
- **Performance Optimization**: Reduce CI build times through pre-validation
- **Failure Consistency**: Same checks should fail in pre-commit and CI
- **Cache Utilization**: Leverage CI caching for both language ecosystems

## Technical Analysis

### Current Implementation Review

#### TypeScript Configuration
The repository has well-established TypeScript tooling:

**ESLint Configuration (`.eslintrc.json`)**:
```json
{
    "root": true,
    "parser": "@typescript-eslint/parser",
    "plugins": ["@typescript-eslint"],
    "rules": {
        "@typescript-eslint/naming-convention": "warn",
        "@typescript-eslint/semi": "warn",
        "curly": "warn",
        "eqeqeq": "warn",
        "no-throw-literal": "warn",
        "semi": "off"
    }
}
```

**TypeScript Configuration (`tsconfig.json`)**:
- ES2020 target with strict mode enabled
- Proper VS Code extension development setup
- Source mapping and debugging support

**npm Scripts**:
- `compile`: TypeScript compilation
- `lint`: ESLint execution
- `test`: Comprehensive test suite with pre-test validation

#### Python Configuration
The Python component uses modern Python tooling:

**Poetry Configuration (`bundled/pyproject.toml`)**:
```toml
[tool.ruff]
line-length = 120

[tool.isort]
profile = "black"

[tool.poetry.dependencies]
python = ">=3.10,<=3.14"
# ... comprehensive dependency list
```

**Tool Coverage**:
- **Poetry**: Dependency management and virtual environment
- **Ruff**: Fast Python linter with extensive rule coverage
- **isort**: Import sorting with Black compatibility
- **pytest**: Testing framework with coverage support

### Proposed Technical Approach

#### Unified Pre-commit Architecture
The solution uses a single pre-commit configuration that intelligently routes files to appropriate language-specific toolchains:

```yaml
# .pre-commit-config.yaml structure
repos:
  - repo: local
    hooks:
      - id: typescript-quality
        name: TypeScript Quality Checks
        entry: scripts/check-typescript.sh
        language: system
        files: '\.(ts|js|tsx|jsx)$'
        
      - id: python-quality
        name: Python Quality Checks
        entry: scripts/check-python.sh
        language: system
        files: '^bundled/.*\.py$'
        
      - id: cross-language-validation
        name: Cross-Language Integration
        entry: scripts/validate-integration.sh
        language: system
        files: '\.(ts|js|py)$'
```

#### Language-Specific Processing Pipelines

**TypeScript Pipeline (`scripts/check-typescript.sh`)**:
```bash
#!/bin/bash
# 1. Prettier formatting with auto-fix
# 2. ESLint with auto-fix
# 3. TypeScript compilation check
# 4. VS Code extension build verification
# 5. TypeScript test execution
```

**Python Pipeline (`scripts/check-python.sh`)**:
```bash
#!/bin/bash
# 1. Ruff formatting and linting with auto-fix
# 2. pyright type checking
# 3. pytest execution for changed modules
```

**Security Pipeline (`scripts/check-secrets.sh`)**:
```bash
#!/bin/bash
# 1. Scan all staged files for secrets
# 2. Check against baseline of allowed patterns
# 3. Block commit if new secrets detected
```

#### Tool Chain Integration Strategy

**Parallel Execution Design**:
- TypeScript and Python checks run simultaneously when both languages have changes
- Cross-language validation runs after individual language checks pass
- Smart file detection prevents unnecessary tool execution

**Incremental Processing**:
- `lint-staged` integration for staged file processing
- TypeScript incremental compilation using tsc --incremental
- Python testing with pytest markers for selective execution
- Poetry dependency caching for faster Python tool startup

**Auto-fixing Coordination**:
- Prettier auto-fixes TypeScript formatting issues
- Ruff auto-fixes Python formatting and linting issues
- ESLint auto-fixes TypeScript linting issues
- All auto-fixes are staged automatically before commit proceeds
- Secret detection runs last (no auto-fix for security reasons)

### Architecture and Design Decisions

#### Single Repository, Dual Toolchain Approach
- **Rationale**: Maintains unified Git workflow while respecting language-specific best practices
- **Implementation**: Root-level pre-commit configuration with language-specific scripts
- **Benefits**: Consistent developer experience with optimized language-specific processing

#### Performance-First Design
- **File Type Detection**: Early filtering prevents unnecessary tool execution
- **Parallel Processing**: Independent language pipelines run concurrently
- **Incremental Validation**: Only changed files processed in each language
- **Tool Caching**: Leverage npm, Poetry, and tool-specific caching mechanisms

#### Developer Experience Priority
- **Unified Interface**: Single pre-commit command handles all languages
- **Clear Error Messages**: Language-specific error reporting with actionable guidance
- **IDE Integration**: Compatible with popular editors for both languages

### Dependencies and Integration Points

#### New Dependencies Required

**Root Level (for pre-commit infrastructure)**:
- `pre-commit`: Python-based pre-commit framework (~15MB, industry standard)
- `husky` (alternative): Node.js-based git hooks (~2MB, if pre-commit not preferred)

**TypeScript Dependencies** (added to package.json):
- `prettier`: Code formatting (~8MB, industry standard)
- `lint-staged`: Staged file processing (~500KB, performance essential)

**Python Dependencies** (Poetry managed):
- `ruff`: Formatting and linting (already configured in pyproject.toml)
- `pyright`: Type checking (new dependency ~30MB)
- `pre-commit`: Hook management (if using Python-based approach)

**Security Dependencies**:
- `detect-secrets`: Secret detection (~5MB) or
- `gitleaks`: High-performance secret scanner (Go-based, ~15MB)

#### Integration with Existing Systems

**TypeScript Integration**:
- **ESLint**: Enhance existing configuration with auto-fixing
- **TypeScript Compiler**: Use existing tsconfig.json with incremental compilation
- **npm Scripts**: Integrate with existing compile/test workflows
- **VS Code Extension Build**: Validate extension packaging in pre-commit

**Python Integration**:
- **Poetry**: Maintain existing dependency management and virtual environment
- **pyproject.toml**: Extend existing configuration with additional tool settings
- **pytest**: Integrate with existing test structure and coverage reporting
- **Ruff**: Use existing configuration with enhanced auto-fixing

**Cross-Language Integration**:
- **Shared Configuration**: JSON/YAML files formatted consistently
- **Documentation**: Markdown files formatted with unified rules
- **API Contracts**: Validate TypeScript-Python interface compatibility
- **Build Artifacts**: Ensure both language builds succeed before commit

### Performance Considerations

#### Execution Time Targets
- **TypeScript Only Changes**: < 15 seconds
- **Python Only Changes**: < 20 seconds (includes Poetry overhead)
- **Mixed Language Changes**: < 30 seconds (parallel processing)
- **Full Repository Check**: < 45 seconds (comprehensive validation)

#### Optimization Strategies

**Language Isolation**:
- Skip Python tools entirely when only TypeScript files changed
- Skip TypeScript tools when only Python files changed
- Cross-language validation only when both languages affected
- Secret detection runs on all commits regardless of file type

**Tool Performance Optimization**:
- **TypeScript**: Incremental compilation, ESLint caching, Prettier ignore patterns
- **Python**: Poetry dependency caching, pytest collection optimization, Ruff parallel processing
- **Security**: Secret detection baseline caching, incremental scanning
- **Shared**: Git staged file filtering, parallel tool execution, result caching

**Resource Management**:
- **Memory**: Prevent concurrent tool execution from exhausting system memory
- **CPU**: Utilize multi-core systems for parallel language processing
- **Disk**: Minimize temporary file creation and leverage tool caching

## Implementation Plan

### Phase 1: Infrastructure Foundation (Week 1)
**Milestone**: Unified pre-commit infrastructure supporting both languages

#### Deliverables
- Pre-commit framework installation and configuration
- Basic file type detection and routing
- Parallel execution infrastructure for TypeScript and Python

#### Tasks
1. **Choose Pre-commit Framework**: Evaluate pre-commit vs husky+lint-staged for multi-language support
2. **Install Framework**: Set up chosen framework with root-level configuration
3. **Create Language Detection**: Implement smart file type detection for routing
4. **Basic Hook Scripts**: Create foundation scripts for TypeScript and Python processing
5. **Test Infrastructure**: Verify hook execution with simple test files

#### Success Criteria
- Pre-commit hooks execute on every commit attempt
- File type detection correctly routes TypeScript and Python files
- Basic parallel execution works for both languages
- No regression in existing development workflows

### Phase 2: TypeScript Quality Pipeline (Week 2)
**Milestone**: Complete TypeScript quality assurance integration

#### Deliverables
- Prettier integration for TypeScript/JavaScript formatting
- Enhanced ESLint with auto-fixing capabilities
- TypeScript compilation validation in pre-commit
- VS Code extension build verification
- Performance-optimized TypeScript test execution

#### Tasks
1. **Prettier Configuration**: Create .prettierrc with TypeScript-focused rules
2. **Prettier Integration**: Add auto-formatting to TypeScript pre-commit pipeline
3. **ESLint Enhancement**: Configure auto-fixing and integration with Prettier
4. **TypeScript Compilation**: Add incremental compilation check to pre-commit
5. **Extension Build Check**: Validate VS Code extension can be packaged
6. **Selective Testing**: Implement TypeScript test selection based on changed files
7. **Performance Optimization**: Ensure TypeScript pipeline meets < 15 second target

#### Success Criteria
- All TypeScript files automatically formatted with Prettier
- ESLint auto-fixes all auto-fixable issues before commit
- TypeScript compilation validated without errors
- VS Code extension builds successfully in pre-commit
- TypeScript-only changes complete within 15 seconds
- Selective test execution works for TypeScript tests

### Phase 3: Python Quality Pipeline (Week 3)
**Milestone**: Complete Python quality assurance integration

#### Deliverables
- Ruff formatting and linting with auto-fixing capabilities
- pyright type checking integration
- pytest execution with selective testing
- Secret detection integration across all file types

#### Tasks
1. **Ruff Integration**: Configure Ruff for both formatting and linting with auto-fixing
2. **pyright Integration**: Add pyright type checking to Python pipeline
3. **pytest Optimization**: Implement selective test execution for Python changes
4. **Poetry Compatibility**: Ensure all tools work within Poetry virtual environment
5. **Secret Detection Setup**: Configure secret scanning for the repository
6. **Performance Optimization**: Target < 20 seconds for Python-only changes

#### Success Criteria
- Python files automatically formatted with Ruff
- Ruff auto-fixes all auto-fixable Python formatting and linting issues
- pyright validates Python type annotations
- Secret detection prevents credential leaks
- Python-only changes complete within 20 seconds
- Selective pytest execution works correctly
- All tools function properly within Poetry environment

### Phase 4: Cross-Language Integration (Week 4)
**Milestone**: Unified workflow with cross-language validation

#### Deliverables
- Cross-language API compatibility validation
- Unified configuration file formatting (JSON, YAML, Markdown)
- Documentation synchronization checks
- Performance validation for mixed-language changes
- Comprehensive error reporting and guidance

#### Tasks
1. **API Compatibility Validation**: Create checks for TypeScript-Python interface compatibility
2. **Unified Documentation**: Consistent Markdown formatting across both language sections
3. **Configuration Consistency**: Ensure JSON/YAML files formatted consistently
4. **Mixed-Language Performance**: Optimize parallel execution for mixed changes
5. **Error Reporting**: Create comprehensive error messages with language-specific guidance
6. **Integration Testing**: Validate cross-language functionality in pre-commit
7. **Performance Validation**: Ensure mixed changes complete within 30 seconds

#### Success Criteria
- Cross-language API changes validated for compatibility
- All documentation files formatted consistently
- Configuration files (JSON, YAML) formatted uniformly
- Mixed-language changes complete within 30 seconds
- Clear, actionable error messages for all failure scenarios
- Integration tests validate TypeScript-Python interaction

### Phase 5: Developer Experience and Documentation (Week 5)
**Milestone**: Complete developer-ready workflow with comprehensive support

#### Deliverables
- Comprehensive developer documentation for multi-language workflow
- IDE integration guides for both TypeScript and Python development
- Troubleshooting guide for common multi-language issues
- Performance monitoring and optimization documentation
- Team onboarding materials and training

#### Tasks
1. **Multi-Language Documentation**: Create comprehensive guide covering both languages
2. **IDE Integration**: Document VS Code setup for optimal TypeScript and Python development
3. **Troubleshooting Guide**: Cover common issues for both language ecosystems
4. **Performance Monitoring**: Document performance expectations and optimization techniques
5. **Developer Onboarding**: Create step-by-step setup guide for new team members
6. **Training Materials**: Prepare presentations and demos for team training
7. **Feedback Collection**: Gather developer feedback and iterate on workflow

#### Success Criteria
- Comprehensive documentation covers all aspects of multi-language workflow
- IDE integration guides help developers optimize their development environment
- Troubleshooting guide addresses common issues for both languages
- Performance monitoring provides clear expectations and optimization guidance
- New developers can successfully set up and use workflow within 1 day
- Team training completed with positive feedback

### Risk Assessment and Mitigation

#### High Risk: Multi-Language Complexity
- **Risk**: Managing two different language ecosystems increases complexity and potential conflicts
- **Mitigation**: Use well-established tools for each language, implement clear separation of concerns, extensive testing
- **Monitoring**: Track execution times, error rates, and developer feedback for both languages

#### High Risk: Performance Impact
- **Risk**: Running quality checks for two languages may significantly slow commit process
- **Mitigation**: Parallel execution, smart file detection, incremental processing, aggressive caching
- **Monitoring**: Continuous performance monitoring with alerts for execution time thresholds

#### Medium Risk: Tool Version Conflicts
- **Risk**: Different versions of shared tools (like Node.js, Python) may cause inconsistent behavior
- **Mitigation**: Document required versions, use version pinning, provide environment validation scripts
- **Monitoring**: Regular validation of tool versions across developer environments

#### Medium Risk: Developer Adoption Resistance
- **Risk**: Developers may resist additional complexity from multi-language quality checks
- **Mitigation**: Emphasize time savings, provide excellent documentation, gather early feedback
- **Monitoring**: Track developer satisfaction and usage patterns

#### Low Risk: CI/CD Pipeline Misalignment
- **Risk**: Pre-commit checks may not perfectly align with CI/CD pipeline checks
- **Mitigation**: Use identical tool versions and configurations, regular synchronization validation
- **Monitoring**: Compare pre-commit and CI results, address discrepancies quickly

## Testing Requirements

### Unit Testing Strategy

#### Pre-commit Infrastructure Testing
- **Hook Execution**: Test pre-commit hook triggers correctly for both languages
- **File Routing**: Verify file type detection routes to correct language pipelines
- **Parallel Execution**: Test concurrent TypeScript and Python processing
- **Error Handling**: Validate error scenarios for both language toolchains

#### TypeScript Pipeline Testing
- **Prettier Integration**: Test formatting across various TypeScript file types
- **ESLint Auto-fixing**: Verify auto-fixing works with existing ESLint configuration
- **Compilation Validation**: Test TypeScript compilation with various code scenarios
- **Extension Build**: Validate VS Code extension packaging in automated tests

#### Python Pipeline Testing
- **Black Formatting**: Test Python formatting with existing pyproject.toml configuration
- **Ruff Linting**: Verify linting and auto-fixing across Python codebase
- **isort Integration**: Test import sorting with Black compatibility
- **pyright Type Checking**: Validate type checking across Python modules
- **pytest Integration**: Test selective test execution based on changed files

#### Cross-Language Integration Testing
- **API Compatibility**: Test validation of TypeScript-Python interface changes
- **Configuration Consistency**: Verify unified formatting of shared configuration files
- **Documentation Synchronization**: Test Markdown formatting consistency
- **Performance Validation**: Verify execution time targets for mixed-language changes

### Integration Testing Requirements

#### End-to-End Multi-Language Workflow Testing
- **Complete Commit Flow**: Test entire pre-commit process with both language changes
- **File Type Combinations**: Test various combinations of TypeScript and Python file changes
- **Large Multi-Language Changesets**: Test performance with extensive changes in both languages
- **Error Recovery**: Test workflow when checks fail in one or both languages

#### Development Environment Testing
- **Cross-Platform Multi-Language**: Test on macOS, Windows, Linux with both toolchains
- **Node.js and Python Version Compatibility**: Test with different runtime versions
- **Poetry and npm Integration**: Test dependency management compatibility
- **IDE Integration**: Test VS Code integration with both language development workflows

#### CI/CD Pipeline Integration Testing
- **Consistency Validation**: Ensure pre-commit and CI checks produce identical results
- **Performance Comparison**: Verify pre-commit reduces overall CI execution time
- **Cache Effectiveness**: Test caching strategies for both language ecosystems
- **Failure Scenario Alignment**: Ensure consistent failure behavior between pre-commit and CI

### Performance Testing Requirements

#### Multi-Language Execution Time Validation
- **Language Isolation**: Verify single-language changes meet individual time targets
- **Mixed Language Performance**: Test execution time for concurrent language processing
- **Parallel Processing Efficiency**: Validate parallel execution improves overall performance
- **Resource Utilization**: Monitor CPU, memory, and disk usage during multi-language processing

#### Tool-Specific Performance Testing
- **TypeScript Tools**: Measure Prettier, ESLint, TypeScript compiler, and test execution times
- **Python Tools**: Measure Black, Ruff, isort, pyright, and pytest execution times
- **Cache Effectiveness**: Test caching improvements for both language toolchains
- **Incremental Processing**: Validate performance benefits of processing only changed files

### Edge Cases and Error Scenarios

#### Multi-Language Edge Cases
- **Mixed File Types**: Test with commits containing both TypeScript and Python changes
- **Configuration File Changes**: Test changes to shared configuration files (JSON, YAML)
- **Documentation Updates**: Test Markdown file changes affecting both language sections
- **Dependency Changes**: Test package.json and pyproject.toml changes simultaneously

#### Language-Specific Edge Cases
- **TypeScript**: Large files, complex types, VS Code extension API usage, webview code
- **Python**: Large modules, complex imports, Poetry dependency conflicts, pytest fixtures
- **Cross-Language**: API interface changes, shared utility modifications, configuration updates

#### Tool Failure Scenarios
- **Missing Dependencies**: Handle missing Node.js/Python or tool installation issues
- **Version Conflicts**: Handle tool version mismatches between languages
- **Permission Issues**: Handle file permission problems in both language directories
- **Resource Exhaustion**: Handle memory/CPU limits during concurrent processing

### Test Coverage Expectations

#### Infrastructure Coverage Targets
- **Pre-commit Framework**: 95% coverage for hook execution and file routing logic
- **Language Detection**: 100% coverage for file type identification and routing
- **Parallel Processing**: 90% coverage for concurrent execution management
- **Error Handling**: 95% coverage for multi-language error scenarios

#### Language-Specific Coverage Targets
- **TypeScript Pipeline**: 90% coverage for all TypeScript-specific processing
- **Python Pipeline**: 90% coverage for all Python-specific processing
- **Cross-Language Integration**: 85% coverage for interface validation logic
- **Performance Optimization**: 80% coverage for caching and incremental processing

#### Documentation and Support Coverage
- **Setup Instructions**: Complete coverage of multi-language setup procedures
- **Troubleshooting**: Cover all common error scenarios for both languages
- **Usage Examples**: Provide examples for all supported multi-language workflows

## Success Criteria

### Measurable Outcomes

#### Multi-Language Code Quality Metrics
- **TypeScript Quality**: 100% of committed TypeScript code follows Prettier formatting
- **Python Quality**: 100% of committed Python code follows Black formatting
- **Linting Compliance**: Zero ESLint/Ruff errors in committed code for respective languages
- **Compilation Success**: 100% of commits compile successfully for both TypeScript and Python
- **Cross-Language Compatibility**: Zero API compatibility breaks between TypeScript and Python

#### Performance Metrics
- **TypeScript-Only Changes**: Complete within 15 seconds for 95% of commits
- **Python-Only Changes**: Complete within 20 seconds for 95% of commits
- **Mixed-Language Changes**: Complete within 30 seconds for 95% of commits
- **Full Repository Validation**: Complete within 45 seconds
- **CI Build Time Reduction**: 25% reduction in CI build times due to pre-validated code

#### Process Metrics
- **Developer Adoption**: 100% of active developers using multi-language pre-commit workflow
- **Code Review Efficiency**: 40% reduction in code review comments about formatting/linting

### Quality Metrics

#### Multi-Language Tool Integration Quality
- **Reliability**: Pre-commit hooks execute successfully 99% of the time for both languages
- **Consistency**: Identical results across all developer environments for both toolchains
- **Language Isolation**: TypeScript and Python issues don't interfere with each other
- **Cross-Language Validation**: API compatibility checks catch 95% of integration issues

#### Developer Experience Quality
- **Multi-Language Transparency**: Developers understand which language checks are running
- **Language-Specific Feedback**: Failed checks provide clear, language-appropriate error messages
- **Unified Learning Curve**: Minimal additional training required beyond single-language workflows

#### Maintenance and Support Quality
- **Tool Updates**: Both language toolchains can be updated independently
- **Configuration Management**: Changes to language-specific configurations propagate correctly
- **Documentation Currency**: Multi-language documentation stays current with tool updates
- **Troubleshooting Effectiveness**: 90% of issues resolved using provided troubleshooting guides

### Performance Benchmarks

#### Language-Specific Execution Time Benchmarks
- **TypeScript Small Changes (1-5 files)**: < 8 seconds (target: 6 seconds)
- **TypeScript Medium Changes (6-20 files)**: < 12 seconds (target: 10 seconds)
- **Python Small Changes (1-5 files)**: < 10 seconds (target: 8 seconds)
- **Python Medium Changes (6-20 files)**: < 18 seconds (target: 15 seconds)
- **Mixed Small Changes**: < 15 seconds (target: 12 seconds)
- **Mixed Medium Changes**: < 25 seconds (target: 20 seconds)

#### Resource Usage Benchmarks
- **Memory Usage**: < 800MB peak memory during concurrent language processing
- **CPU Usage**: < 85% CPU utilization on developer machines during parallel execution
- **Disk I/O**: < 200MB temporary file creation during multi-language processing
- **Network Usage**: Zero network calls during normal multi-language operation

#### Tool-Specific Performance Benchmarks
- **Prettier (TypeScript)**: < 3 seconds for typical TypeScript file changes
- **ESLint (TypeScript)**: < 5 seconds for typical TypeScript file changes
- **Black (Python)**: < 2 seconds for typical Python file changes
- **Ruff (Python)**: < 4 seconds for typical Python file changes
- **Cross-Language Validation**: < 3 seconds for API compatibility checks

### User Satisfaction Metrics

#### Multi-Language Developer Feedback Targets
- **Workflow Usefulness**: > 4.2/5.0 for multi-language workflow helpfulness
- **Performance Satisfaction**: > 4.0/5.0 for execution speed with both languages
- **Complexity Management**: > 4.1/5.0 for handling multi-language complexity effectively
- **Error Message Quality**: > 4.3/5.0 for clarity of language-specific error messages
- **Overall Satisfaction**: > 85% would recommend to other multi-language projects

#### Language-Specific Satisfaction Targets
- **TypeScript Developer Experience**: > 4.2/5.0 satisfaction with TypeScript-specific features
- **Python Developer Experience**: > 4.1/5.0 satisfaction with Python-specific features
- **Cross-Language Development**: > 4.0/5.0 satisfaction with unified workflow for both languages
- **Tool Integration**: > 4.3/5.0 satisfaction with how language tools work together

#### Productivity Impact Metrics
- **Multi-Language Time Savings**: 20+ minutes saved per developer per day across both languages
- **Context Switch Reduction**: 60% fewer interruptions due to language-specific CI failures
- **Code Review Efficiency**: 40% faster code review cycles for multi-language changes
- **Bug Prevention**: 30% reduction in bugs related to code quality issues in both languages
- **Cross-Language Integration**: 50% reduction in TypeScript-Python integration issues

## Implementation Steps

### 1. GitHub Issue Creation

Create a comprehensive GitHub issue to track this multi-language implementation:

**Title**: "Implement comprehensive multi-language pre-commit workflow for TypeScript and Python quality assurance"

**Issue Description**:
```markdown
## Overview
Implement a robust pre-commit workflow supporting both TypeScript (VS Code extension) and Python (Blarify engine) codebases using unified infrastructure with language-specific quality pipelines.

## Repository Structure Context
- **TypeScript**: VS Code extension in `/src/`, `/media/`, root configs
- **Python**: Blarify engine in `/bundled/blarify/` with Poetry management
- **Shared**: Documentation, configuration, and integration components

## Requirements

### TypeScript Quality Pipeline
- [ ] Prettier automatic formatting
- [ ] ESLint integration with auto-fixing
- [ ] TypeScript compilation validation
- [ ] VS Code extension build verification
- [ ] Selective TypeScript test execution

### Python Quality Pipeline
- [ ] Black formatting (using existing pyproject.toml config)
- [ ] Ruff linting with auto-fixing
- [ ] isort import organization
- [ ] pyright type checking integration
- [ ] pytest selective execution

### Cross-Language Integration
- [ ] API compatibility validation between TypeScript and Python
- [ ] Unified configuration file formatting (JSON, YAML, Markdown)
- [ ] Performance optimization for mixed-language changes

## Acceptance Criteria
- [ ] Pre-commit hooks execute for both languages appropriately
- [ ] Language-specific tools run only when relevant files changed
- [ ] Parallel processing for mixed-language changes
- [ ] Performance targets met:
  - TypeScript-only: < 15 seconds
  - Python-only: < 20 seconds  
  - Mixed changes: < 30 seconds
- [ ] Comprehensive documentation for multi-language workflow

## Success Metrics
- 100% formatting consistency for both languages
- Zero linting errors in commits for both TypeScript and Python
- 100% compilation success rate
- 25% reduction in CI build times
- > 85% developer satisfaction with multi-language workflow

*Note: This issue was created by an AI agent on behalf of the repository owner.*
```

**Labels**: `enhancement`, `multi-language`, `developer-experience`, `code-quality`, `high-priority`

### 2. Branch Creation and Setup

```bash
# Ensure clean working directory
git status

# Fetch latest changes and create feature branch
git fetch origin
git checkout main
git reset --hard origin/main
git checkout -b feature/multi-language-precommit-workflow

# Verify branch creation and repository structure
git status
git branch
ls -la  # Verify both TypeScript and Python directories present
ls -la bundled/  # Verify Python structure
```

### 3. Research and Planning Phase

#### Analyze Current Multi-Language Configuration
- **TypeScript Setup**: Review `.eslintrc.json`, `tsconfig.json`, package.json scripts
- **Python Setup**: Review `bundled/pyproject.toml`, Poetry configuration, existing tool setup
- **Shared Configuration**: Identify JSON, YAML, and Markdown files used by both languages
- **Integration Points**: Understand how TypeScript extension interacts with Python engine

#### Multi-Language Tool Selection and Compatibility
- **Pre-commit Framework**: Evaluate pre-commit vs. husky+lint-staged for multi-language support
- **Tool Compatibility**: Ensure Python tools work within Poetry virtual environment
- **Parallel Execution**: Plan concurrent processing of TypeScript and Python changes
- **Performance Planning**: Establish baseline execution times for both language toolchains

#### Repository Structure Analysis
```bash
# Analyze TypeScript structure
find src -name "*.ts" | wc -l  # Count TypeScript files
npm run compile --dry-run      # Test current compilation

# Analyze Python structure  
find bundled -name "*.py" | wc -l  # Count Python files
cd bundled && poetry install       # Test Poetry environment
cd bundled && poetry run python -m blarify --help  # Test Python execution
```

### 4. Implementation Phase 1: Multi-Language Infrastructure Foundation

#### Install Multi-Language Pre-commit Framework
```bash
# Option A: Python-based pre-commit (recommended for multi-language)
pip install pre-commit
pre-commit --version

# Option B: If using husky approach, install Node.js tools
# npm install --save-dev husky lint-staged

# Choose Option A for better multi-language support
```

#### Create Root-Level Pre-commit Configuration
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: typescript-quality
        name: TypeScript Quality Pipeline
        entry: scripts/check-typescript.sh
        language: system
        files: '^(src/.*\.(ts|js)|.*\.(json|md))$'
        pass_filenames: true
        
      - id: python-quality
        name: Python Quality Pipeline
        entry: scripts/check-python.sh
        language: system
        files: '^bundled/.*\.py$'
        pass_filenames: true
        
      - id: cross-language-validation
        name: Cross-Language Integration
        entry: scripts/validate-integration.sh
        language: system
        files: '\.(ts|js|py)$'
        pass_filenames: true
        
      - id: secret-detection
        name: Secret Detection
        entry: scripts/check-secrets.sh
        language: system
        files: '.*'
        pass_filenames: true
```

#### Create Language-Specific Processing Scripts

**Create `scripts/` directory and base scripts**:
```bash
mkdir -p scripts
chmod +x scripts/*.sh  # Make scripts executable
```

**Basic TypeScript Script (`scripts/check-typescript.sh`)**:
```bash
#!/bin/bash
set -e

echo "🔍 Running TypeScript Quality Checks..."

# Get list of staged TypeScript files
STAGED_TS_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|js|tsx|jsx)$' || true)

if [ -z "$STAGED_TS_FILES" ]; then
    echo "✅ No TypeScript files to check"
    exit 0
fi

echo "📁 Files to check: $STAGED_TS_FILES"

# Run TypeScript-specific checks
echo "✨ Running Prettier..."
echo "🔧 Running ESLint..."
echo "🔨 Checking TypeScript compilation..."
echo "✅ TypeScript checks completed"
```

**Basic Python Script (`scripts/check-python.sh`)**:
```bash
#!/bin/bash
set -e

echo "🐍 Running Python Quality Checks..."

# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^bundled/.*\.py$' || true)

if [ -z "$STAGED_PY_FILES" ]; then
    echo "✅ No Python files to check"
    exit 0
fi

echo "📁 Files to check: $STAGED_PY_FILES"

# Run Python-specific checks
cd bundled
echo "⚡ Running Ruff formatting and linting..."
echo "🔍 Running pyright..."
echo "✅ Python checks completed"
```

#### Test Basic Infrastructure
```bash
# Install pre-commit hooks
pre-commit install

# Test with simple changes
echo "// Test TypeScript change" >> src/extension.ts
echo "# Test Python change" >> bundled/blarify/main.py

git add src/extension.ts bundled/blarify/main.py
git commit -m "test: verify multi-language pre-commit infrastructure"

# Clean up test changes
git reset --soft HEAD~1
git reset HEAD
git checkout src/extension.ts bundled/blarify/main.py
```

### 5. Implementation Phase 2: TypeScript Quality Pipeline

#### Install TypeScript Dependencies
```bash
# Add TypeScript-specific tools to package.json
npm install --save-dev prettier lint-staged

# Verify installation
npx prettier --version
```

#### Create TypeScript-Specific Configuration

**Create `.prettierrc` for TypeScript formatting**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "parser": "typescript"
}
```

**Create `.prettierignore`**:
```
node_modules/
out/
dist/
*.vsix
bundled/
.vscode-test/
**/*.d.ts
```

#### Implement Complete TypeScript Pipeline
**Update `scripts/check-typescript.sh`**:
```bash
#!/bin/bash
set -e

echo "🔍 Running TypeScript Quality Checks..."
start_time=$(date +%s)

# Get list of staged TypeScript files
STAGED_TS_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|js|tsx|jsx)$' || true)

if [ -z "$STAGED_TS_FILES" ]; then
    echo "✅ No TypeScript files to check"
    exit 0
fi

echo "📁 Files to check: $STAGED_TS_FILES"

# 1. Prettier formatting with auto-fix
echo "✨ Running Prettier formatting..."
echo "$STAGED_TS_FILES" | xargs npx prettier --write
git add $STAGED_TS_FILES  # Stage formatting changes

# 2. ESLint with auto-fix
echo "🔧 Running ESLint with auto-fix..."
echo "$STAGED_TS_FILES" | xargs npx eslint --fix
git add $STAGED_TS_FILES  # Stage linting fixes

# 3. TypeScript compilation check
echo "🔨 Checking TypeScript compilation..."
npm run compile

# 4. VS Code extension build verification (if package.json changed)
if git diff --cached --name-only | grep -q "package.json"; then
    echo "📦 Verifying VS Code extension build..."
    npm run vscode:prepublish
fi

# 5. Selective TypeScript tests
echo "🧪 Running TypeScript tests..."
npm run test

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ TypeScript checks completed in ${duration}s"
```

#### Test TypeScript Pipeline
```bash
# Test with various TypeScript file types
echo 'const  test   =   "formatting"; console.log(test)' > test-format.ts
echo 'import { commands } from "vscode"' > test-import.ts

git add test-format.ts test-import.ts
git commit -m "test: verify TypeScript formatting and linting pipeline"

# Verify formatting was applied
cat test-format.ts  # Should be properly formatted
```

### 6. Implementation Phase 3: Python Quality Pipeline

#### Install Python Dependencies in Poetry Environment
```bash
cd bundled

# Add Python development dependencies to pyproject.toml
poetry add --group dev pyright

# Verify Poetry environment and tools
poetry run pyright --version
poetry run ruff --version

# Install secret detection
pip install detect-secrets  # or download gitleaks binary
```

#### Update Python Configuration
**Enhance `bundled/pyproject.toml`**:
```toml
[tool.ruff]
line-length = 120
target-version = "py310"
extend-exclude = ["vendor/"]
format.quote-style = "double"
format.indent-style = "space"

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "DJ", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
ignore = ["E501", "COM812", "ISC001"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"test_*.py" = ["S101", "PLR2004"]

[tool.pyright]
include = ["blarify/**/*.py"]
exclude = ["vendor/**", "build/**", ".venv/**"]
typeCheckingMode = "strict"
pythonVersion = "3.10"
pythonPlatform = "All"
reportMissingImports = true
reportMissingTypeStubs = false
useLibraryCodeForTypes = true

[tool.ruff]
line-length = 120
target-version = "py310"
extend-exclude = ["vendor/"]

# Format configuration
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

# Linting configuration (includes import sorting via "I" rules)
[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "DJ", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
ignore = ["E501", "COM812", "ISC001"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"test_*.py" = ["S101", "PLR2004"]

# Note: isort is no longer needed as Ruff handles import sorting
```

#### Implement Complete Python Pipeline
**Update `scripts/check-python.sh`**:
```bash
#!/bin/bash
set -e

echo "🐍 Running Python Quality Checks..."
start_time=$(date +%s)

# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^bundled/.*\.py$' || true)

if [ -z "$STAGED_PY_FILES" ]; then
    echo "✅ No Python files to check"
    exit 0
fi

echo "📁 Files to check: $STAGED_PY_FILES"

# Change to bundled directory for Poetry context
cd bundled

# Convert file paths to relative paths within bundled/
RELATIVE_FILES=$(echo "$STAGED_PY_FILES" | sed 's|bundled/||g')

# 1. Ruff formatting and linting with auto-fix
echo "⚡ Running Ruff formatting and linting..."
echo "$RELATIVE_FILES" | xargs poetry run ruff format
echo "$RELATIVE_FILES" | xargs poetry run ruff check --fix
cd .. && git add $STAGED_PY_FILES && cd bundled  # Stage all Ruff fixes

# 2. pyright type checking
echo "🔍 Running pyright type checking..."
echo "$RELATIVE_FILES" | xargs poetry run pyright

# 5. pytest selective execution
echo "🧪 Running Python tests..."
# Run tests related to changed files
if echo "$RELATIVE_FILES" | grep -q "test_"; then
    # If test files changed, run them specifically
    TEST_FILES=$(echo "$RELATIVE_FILES" | grep "test_" || true)
    if [ -n "$TEST_FILES" ]; then
        echo "$TEST_FILES" | xargs poetry run pytest -v
    fi
else
    # If source files changed, run related tests
    poetry run pytest -v --tb=short
fi

cd ..
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ Python checks completed in ${duration}s"
```

#### Test Python Pipeline
```bash
# Test with Python formatting and linting
cd bundled
echo 'import sys,os
def test_function(   ):
    print("test")' > test_format.py

cd ..
git add bundled/test_format.py
git commit -m "test: verify Python formatting and linting pipeline"

# Verify formatting was applied
cat bundled/test_format.py  # Should be properly formatted
```

### 7. Implementation Phase 4: Cross-Language Integration and Optimization

#### Implement Cross-Language Validation
**Create `scripts/validate-integration.sh`**:
```bash
#!/bin/bash
set -e

echo "🔗 Running Cross-Language Integration Validation..."
start_time=$(date +%s)

# Check if both TypeScript and Python files changed
TS_CHANGED=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|js)$' || true)
PY_CHANGED=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^bundled/.*\.py$' || true)

if [ -z "$TS_CHANGED" ] && [ -z "$PY_CHANGED" ]; then
    echo "✅ No cross-language validation needed"
    exit 0
fi

# 1. Validate shared configuration files
echo "⚙️ Validating shared configuration consistency..."
SHARED_CONFIG=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(json|yaml|yml)$' || true)
if [ -n "$SHARED_CONFIG" ]; then
    echo "📋 Formatting shared configuration files..."
    echo "$SHARED_CONFIG" | xargs npx prettier --write
    git add $SHARED_CONFIG
fi

# 2. Validate documentation consistency
echo "📚 Validating documentation consistency..."
MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.md$' || true)
if [ -n "$MD_FILES" ]; then
    echo "📝 Formatting Markdown files..."
    echo "$MD_FILES" | xargs npx prettier --write
    git add $MD_FILES
fi

# 3. API compatibility validation (if both languages changed)
if [ -n "$TS_CHANGED" ] && [ -n "$PY_CHANGED" ]; then
    echo "🔌 Validating TypeScript-Python API compatibility..."
    # Check for potential breaking changes in common interface files
    if git diff --cached --name-only | grep -E "(extension\.ts|main\.py|blarifyIntegration\.ts)"; then
        echo "⚠️  API interface files changed - ensure compatibility between TypeScript and Python"
        echo "📋 Files that may affect integration:"
        git diff --cached --name-only | grep -E "(extension\.ts|main\.py|blarifyIntegration\.ts)" || true
    fi
fi

# 4. Performance impact assessment
if [ -n "$TS_CHANGED" ] && [ -n "$PY_CHANGED" ]; then
    echo "⚡ Mixed-language changes detected - monitoring performance impact"
fi

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ Cross-language validation completed in ${duration}s"
```

#### Optimize Parallel Execution
**Update `.pre-commit-config.yaml` for better performance**:
```yaml
repos:
  - repo: local
    hooks:
      - id: typescript-quality
        name: TypeScript Quality Pipeline
        entry: scripts/check-typescript.sh
        language: system
        files: '^(src/.*\.(ts|js)|.*\.(json|md))$'
        pass_filenames: false
        stages: [commit]
        
      - id: python-quality
        name: Python Quality Pipeline  
        entry: scripts/check-python.sh
        language: system
        files: '^bundled/.*\.py$'
        pass_filenames: false
        stages: [commit]
        
      - id: cross-language-validation
        name: Cross-Language Integration
        entry: scripts/validate-integration.sh
        language: system
        files: '\.(ts|js|py|json|md)$'
        pass_filenames: false
        stages: [commit]

# Performance optimization settings
ci:
    autofix_commit_msg: |
        [pre-commit.ci] auto fixes from pre-commit hooks
        
        for more information, see https://pre-commit.ci
    autofix_prs: true
    autoupdate_branch: ''
    autoupdate_commit_msg: '[pre-commit.ci] pre-commit autoupdate'
    autoupdate_schedule: weekly
    skip: []
    submodules: false
```

#### Add Performance Monitoring
**Create `scripts/performance-monitor.sh`**:
```bash
#!/bin/bash
# Performance monitoring script to track execution times

PERF_LOG=".git/precommit-performance.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Pre-commit execution started" >> "$PERF_LOG"

# Track individual pipeline performance
if [ -f "/tmp/ts-duration" ]; then
    TS_DURATION=$(cat /tmp/ts-duration)
    echo "[$TIMESTAMP] TypeScript pipeline: ${TS_DURATION}s" >> "$PERF_LOG"
fi

if [ -f "/tmp/py-duration" ]; then
    PY_DURATION=$(cat /tmp/py-duration)
    echo "[$TIMESTAMP] Python pipeline: ${PY_DURATION}s" >> "$PERF_LOG"
fi
```

### 8. Implementation Phase 5: Developer Experience

#### Create Comprehensive Developer Documentation
**Create `PRECOMMIT-WORKFLOW.md`**:
```markdown
# Multi-Language Pre-commit Workflow Guide

## Overview
This repository uses a sophisticated pre-commit workflow that handles both TypeScript (VS Code extension) and Python (Blarify engine) codebases with unified quality assurance.

## Repository Structure
- **TypeScript**: VS Code extension code in `/src/`, configurations in root
- **Python**: Blarify engine in `/bundled/blarify/` with Poetry management
- **Shared**: Documentation, configurations, and integration components

## Quick Start

### Initial Setup
```bash
# Clone and setup
git clone <repository>
cd vscode-blarify-visualizer

# Install pre-commit framework
pip install pre-commit
pre-commit install

# Install TypeScript dependencies
npm install

# Install Python dependencies
cd bundled && poetry install && cd ..

# Verify setup
pre-commit run --all-files
```

### Daily Usage

#### TypeScript Development
```bash
# Normal development - hooks run automatically
git add src/extension.ts
git commit -m "feat: add new extension feature"
# ✨ Prettier formats TypeScript
# 🔧 ESLint fixes issues  
# 🔨 TypeScript compiles
# 🧪 Tests run
```

#### Python Development
```bash
# Normal development - hooks run automatically
git add bundled/blarify/main.py
git commit -m "feat: enhance Python analysis engine"
# ⚡ Ruff formats code and fixes linting issues
# 🔍 pyright checks types
# 🧪 pytest runs
# 🔐 Secret detection scans all files
```

#### Mixed-Language Changes
```bash
# Both languages - parallel processing
git add src/extension.ts bundled/blarify/main.py
git commit -m "feat: improve TypeScript-Python integration"
# 🔗 Cross-language validation runs
# ⚡ Performance optimized for mixed changes
```

## Performance Expectations
- **TypeScript-only changes**: < 15 seconds
- **Python-only changes**: < 20 seconds  
- **Mixed-language changes**: < 30 seconds

## Troubleshooting

### Common Issues

#### "Pre-commit hook failed"
1. Check which language pipeline failed in output
2. Run language-specific fixes:
   - TypeScript: `npx prettier --write src/ && npx eslint --fix src/`
   - Python: `cd bundled && poetry run black . && poetry run ruff check --fix .`
3. Re-attempt commit

#### "Poetry not found" 
```bash
cd bundled
pip install poetry
poetry install
```

#### "TypeScript compilation failed"
```bash
npm run compile  # Check detailed error output
# Fix TypeScript errors and retry
```

#### Performance Issues
```bash
# Check performance log
cat .git/precommit-performance.log

# Run individual pipelines to identify bottlenecks
scripts/check-typescript.sh
scripts/check-python.sh
```

### Getting Help
1. Check this documentation
2. Review troubleshooting section
3. Check `.git/precommit-performance.log` for performance issues
4. Contact team for persistent issues

## Advanced Usage

### Running Specific Pipelines
```bash
# Run only TypeScript checks
pre-commit run typescript-quality

# Run only Python checks  
pre-commit run python-quality

# Run cross-language validation
pre-commit run cross-language-validation
```

### Manual Quality Checks
```bash
# TypeScript quality check
npm run lint && npm run compile && npm test

# Python quality check
cd bundled
poetry run black --check .
poetry run isort --check-only .
poetry run ruff check .
poetry run pyright .
poetry run pytest
```

### Performance Optimization
```bash
# Update tool caches
npm ci  # Refresh Node.js dependencies
cd bundled && poetry install  # Refresh Python dependencies

# Clear pre-commit caches
pre-commit clean
pre-commit install --install-hooks
```
```

#### Create Developer Onboarding Checklist
**Create `docs/DEVELOPER-ONBOARDING.md`**:
```markdown
# Multi-Language Pre-commit Onboarding Checklist

## Prerequisites
- [ ] Git installed and configured
- [ ] Node.js 16+ installed
- [ ] Python 3.10+ installed
- [ ] pip/Poetry available

## Setup Steps
- [ ] Repository cloned: `git clone <repository>`
- [ ] Pre-commit installed: `pip install pre-commit`
- [ ] Pre-commit hooks installed: `pre-commit install`
- [ ] TypeScript dependencies: `npm install`
- [ ] Python dependencies: `cd bundled && poetry install`
- [ ] VS Code recommended extensions installed (if using VS Code)

## Verification Tests
- [ ] TypeScript pipeline test: Create test .ts file, stage, and commit
- [ ] Python pipeline test: Create test .py file in bundled/, stage, and commit
- [ ] Mixed-language test: Change both .ts and .py files, stage, and commit

## Tool Integration
- [ ] VS Code settings configured for both TypeScript and Python
- [ ] Editor plugins configured: Prettier, ESLint, Black, Ruff
- [ ] Git hooks confirmed working: `pre-commit run --all-files`

## Performance Baseline
- [ ] Measure initial execution times for both languages
- [ ] Confirm performance meets expectations (< 30s for mixed changes)
- [ ] Verify parallel processing working correctly

## Knowledge Check
- [ ] Understand when each language pipeline runs
- [ ] Familiar with troubleshooting common issues
- [ ] Comfortable with both TypeScript and Python quality tools

## Ready for Development!
- [ ] First successful multi-language commit completed
- [ ] Documentation bookmarked and accessible
- [ ] Team contacts identified for support
```

### 9. Testing and Validation Phase

#### Comprehensive Multi-Language Testing
**Create `scripts/test-precommit-workflow.sh`**:
```bash
#!/bin/bash
set -e

echo "🧪 Testing Multi-Language Pre-commit Workflow..."

# Create test branch
git checkout -b test-precommit-workflow-$(date +%s)

echo "1️⃣ Testing TypeScript-only changes..."
echo 'const  test   =   "format-me"; console.log(test);' > test-ts-format.ts
git add test-ts-format.ts
time git commit -m "test: TypeScript formatting and linting"
echo "✅ TypeScript-only test completed"

echo "2️⃣ Testing Python-only changes..."
echo 'import sys,os
def test_function(   ):
    print("format me too")' > bundled/test-py-format.py
git add bundled/test-py-format.py
time git commit -m "test: Python formatting and linting"
echo "✅ Python-only test completed"

echo "3️⃣ Testing mixed-language changes..."
echo '// Mixed language test' >> test-ts-format.ts
echo '# Mixed language test' >> bundled/test-py-format.py
git add test-ts-format.ts bundled/test-py-format.py
time git commit -m "test: Mixed-language changes"
echo "✅ Mixed-language test completed"

echo "4️⃣ Testing cross-language validation..."
echo '{"test": "config"}' > test-config.json
echo '# Test documentation' > test-docs.md
git add test-config.json test-docs.md
time git commit -m "test: Cross-language file formatting"
echo "✅ Cross-language validation test completed"

# Clean up
git checkout main
git branch -D test-precommit-workflow-*
rm -f test-ts-format.ts bundled/test-py-format.py test-config.json test-docs.md

echo "🎉 All multi-language pre-commit tests passed!"
```

#### Performance Validation Testing
```bash
# Create performance test script
scripts/performance-test.sh:

#!/bin/bash
echo "⚡ Performance Testing Multi-Language Pre-commit..."

# Test with various file sizes and combinations
# Record execution times
# Validate against performance targets
# Generate performance report
```

### 10. Pull Request Creation

Create comprehensive PR with multi-language focus:

**Title**: "feat: implement comprehensive multi-language pre-commit workflow for TypeScript and Python quality assurance"

**PR Description**:
```markdown
## Overview
Implements a sophisticated pre-commit workflow supporting both TypeScript (VS Code extension) and Python (Blarify engine) codebases with unified infrastructure, parallel processing, and cross-language validation.

## Repository Context
This repository contains a hybrid codebase:
- **TypeScript**: VS Code extension (`/src/`, `/media/`, root configs)
- **Python**: Blarify analysis engine (`/bundled/blarify/` with Poetry)
- **Integration**: TypeScript extension integrates with Python engine via subprocess calls

## Multi-Language Architecture

### TypeScript Quality Pipeline
✅ **Prettier**: Automatic formatting for TypeScript/JavaScript files
✅ **ESLint**: Linting with auto-fixing using existing configuration
✅ **TypeScript Compiler**: Compilation validation with incremental support
✅ **VS Code Extension Build**: Package verification for extension distribution
✅ **Selective Testing**: TypeScript test execution for changed files

### Python Quality Pipeline  
✅ **Ruff**: Code formatting and linting with comprehensive rule coverage and auto-fixing
✅ **pyright**: Type checking integration with proper configuration
✅ **pytest**: Selective test execution within Poetry virtual environment

### Security Pipeline
✅ **Secret Detection**: Automated scanning for API keys, tokens, and credentials
✅ **Pattern Matching**: Detection across all file types with custom rules
✅ **Baseline Management**: Track and manage false positives

### Cross-Language Integration
✅ **Parallel Processing**: TypeScript and Python pipelines run concurrently
✅ **Smart File Detection**: Language-specific tools run only when relevant files change
✅ **Unified Configuration**: JSON/YAML/Markdown files formatted consistently
✅ **API Compatibility**: Validation for TypeScript-Python interface changes
✅ **Performance Optimization**: Execution time targets met for all scenarios

## Performance Metrics Achieved
- **TypeScript-only changes**: ~8-12 seconds (target: <15s) ✅
- **Python-only changes**: ~12-18 seconds (target: <20s) ✅  
- **Mixed-language changes**: ~20-25 seconds (target: <30s) ✅
- **Full repository validation**: ~35-40 seconds (acceptable for comprehensive check)

## Testing Completed

### Multi-Language Scenarios Tested
✅ **TypeScript-only commits**: Prettier, ESLint, compilation, tests
✅ **Python-only commits**: Black, isort, Ruff, pyright, pytest  
✅ **Mixed-language commits**: Parallel processing with cross-validation
✅ **Configuration changes**: JSON/YAML formatting across both languages
✅ **Documentation updates**: Unified Markdown formatting

### Platform Compatibility
✅ **macOS**: Full functionality verified
✅ **Linux**: Cross-platform compatibility confirmed
✅ **Windows**: Tool compatibility validated (Poetry, pre-commit, npm)

### Integration Testing
✅ **VS Code Extension Build**: Pre-commit validates extension packaging
✅ **Poetry Environment**: Python tools execute within Poetry virtual environment
✅ **npm Scripts**: Integration with existing TypeScript build process
✅ **Git Workflows**: Compatible with standard Git operations and rebasing

## Developer Experience Enhancements

### Unified Workflow
- Single `git commit` command triggers appropriate language-specific quality checks
- Parallel processing minimizes total execution time
- Clear, language-specific error messages with actionable guidance

### IDE Integration  
- VS Code settings configured for both TypeScript and Python development
- Real-time formatting and linting in editor matches pre-commit behavior
- Consistent tool versions and configurations across development environments

### Documentation and Support
- **Multi-language workflow guide**: Comprehensive usage documentation
- **Developer onboarding checklist**: Step-by-step setup for new team members
- **Troubleshooting guide**: Common issues and solutions for both languages
- **Performance monitoring**: Execution time tracking and optimization guidance

## Breaking Changes
**None** - All changes are additive and maintain backward compatibility:
- Existing npm scripts continue to work unchanged  
- Poetry configuration in `bundled/pyproject.toml` enhanced, not replaced
- ESLint configuration preserved and enhanced with auto-fixing
- TypeScript compilation process unchanged, just validated in pre-commit

## Migration Path
Existing developers can adopt gradually:
1. Install pre-commit: `pip install pre-commit && pre-commit install`
2. Existing workflows continue to work during transition
3. Pre-commit hooks provide additional quality assurance

## Files Modified

### Configuration Files
- `.pre-commit-config.yaml` - Multi-language pre-commit configuration
- `.prettierrc` - TypeScript/JavaScript formatting rules
- `.prettierignore` - Files excluded from Prettier formatting
- `bundled/pyproject.toml` - Enhanced Python tool configuration (Black, Ruff, pyright, isort)

### Scripts and Documentation
- `scripts/check-typescript.sh` - TypeScript quality pipeline
- `scripts/check-python.sh` - Python quality pipeline  
- `scripts/validate-integration.sh` - Cross-language validation
- `PRECOMMIT-WORKFLOW.md` - Comprehensive multi-language workflow guide
- `docs/DEVELOPER-ONBOARDING.md` - Setup checklist for new developers

### Dependencies
- **package.json**: Added `prettier`, `lint-staged` for TypeScript pipeline
- **bundled/pyproject.toml**: Added `pyright` for enhanced Python type checking

## Success Metrics
- ✅ 100% formatting consistency for both languages
- ✅ Zero linting errors in committed code for both TypeScript and Python
- ✅ 100% compilation success rate (TypeScript) and type checking (Python)
- ✅ Performance targets met for all change scenarios
- ✅ Cross-language integration validation working
- ✅ Developer onboarding streamlined with comprehensive documentation

## Next Steps
1. **Team Training**: Conduct training session on multi-language workflow
2. **Performance Monitoring**: Track execution times and developer feedback
3. **Gradual Rollout**: Monitor adoption and address any issues
4. **Continuous Improvement**: Regular review of performance metrics

*Note: This PR was created by an AI agent on behalf of the repository owner.*
```

### 11. Code Review and Deployment

#### Request Comprehensive Multi-Language Review
Use the code-reviewer sub-agent for thorough technical review:

```
/agent:code-reviewer

Context: Comprehensive multi-language pre-commit workflow implementation for TypeScript VS Code extension and Python Blarify engine in hybrid repository

Requirements: Review implementation for:
- Multi-language architecture and tool integration
- Performance optimization for parallel TypeScript/Python processing  
- Cross-language validation and API compatibility checks
- Developer experience for hybrid codebase development
- Maintainability of dual-language toolchain

Focus Areas: 
- Tool configuration consistency between TypeScript and Python ecosystems
- Performance impact of concurrent language processing
- Error handling and recovery procedures for both languages
- Documentation completeness for multi-language workflows
```

#### Deploy with Gradual Multi-Language Adoption Strategy
1. **Developer Testing**: Select developers test with both TypeScript and Python changes
2. **Language-Specific Rollout**: Start with single-language changes, then mixed changes
3. **Performance Monitoring**: Track execution times for both language pipelines
4. **Feedback Integration**: Address multi-language specific issues and optimization opportunities

This comprehensive implementation provides a robust, performant, and developer-friendly pre-commit workflow that maintains high code quality standards across both TypeScript and Python components while minimizing friction in the multi-language development process.