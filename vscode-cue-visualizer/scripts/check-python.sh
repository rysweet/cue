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

# 3. pytest selective execution
echo "🧪 Running Python tests..."
# Run tests related to changed files
if echo "$RELATIVE_FILES" | grep -q "test_"; then
    # If test files changed, run them specifically
    TEST_FILES=$(echo "$RELATIVE_FILES" | grep "test_" || true)
    if [ -n "$TEST_FILES" ]; then
        echo "$TEST_FILES" | xargs poetry run pytest -v
    fi
else
    # If source files changed, run related tests or all tests (depending on scope)
    poetry run pytest -v --tb=short -x  # Stop on first failure for efficiency
fi

cd ..
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ Python checks completed in ${duration}s"

# Save duration for performance monitoring
echo "$duration" > /tmp/py-duration