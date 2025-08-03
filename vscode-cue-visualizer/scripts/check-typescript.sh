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

# 5. TypeScript tests (for efficiency, skip if no test files changed)
TEST_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E 'test.*\.ts$' || true)
if [ -n "$TEST_FILES" ]; then
    echo "🧪 Running TypeScript tests..."
    npm run test
fi

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ TypeScript checks completed in ${duration}s"

# Save duration for performance monitoring
echo "$duration" > /tmp/ts-duration