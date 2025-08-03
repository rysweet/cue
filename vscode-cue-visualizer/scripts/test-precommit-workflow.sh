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
git checkout feature/multi-language-precommit-workflow
git branch -D test-precommit-workflow-*
rm -f test-ts-format.ts bundled/test-py-format.py test-config.json test-docs.md

echo "🎉 All multi-language pre-commit tests passed!"