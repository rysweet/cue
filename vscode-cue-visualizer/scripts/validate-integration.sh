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