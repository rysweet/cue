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

## Architecture

### TypeScript Quality Pipeline
- **Prettier**: Automatic code formatting
- **ESLint**: Linting with auto-fixing
- **TypeScript Compiler**: Compilation validation
- **VS Code Extension Build**: Package verification
- **Selective Testing**: Run tests for changed files

### Python Quality Pipeline
- **Ruff**: Code formatting and comprehensive linting
- **pyright**: Type checking integration
- **pytest**: Selective test execution
- **Poetry Integration**: Works within virtual environment

### Cross-Language Integration
- **Shared Configuration**: Consistent JSON, YAML, Markdown formatting
- **API Compatibility**: Validation for TypeScript-Python interfaces
- **Performance Monitoring**: Execution time tracking
- **Secret Detection**: Security scanning across all files

## Troubleshooting

### Common Issues

#### "Pre-commit hook failed"
1. Check which language pipeline failed in output
2. Run language-specific fixes:
   - TypeScript: `npx prettier --write src/ && npx eslint --fix src/`
   - Python: `cd bundled && poetry run ruff format . && poetry run ruff check --fix .`
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
poetry run ruff format --check .
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