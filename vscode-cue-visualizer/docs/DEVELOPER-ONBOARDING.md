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
- [ ] Editor plugins configured: Prettier, ESLint, Ruff
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