#!/bin/bash
set -e

echo "🔐 Running Secret Detection..."
start_time=$(date +%s)

# Get list of all staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM || true)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No files to scan for secrets"
    exit 0
fi

echo "🔍 Scanning files for secrets..."

# Simple secret pattern detection (basic implementation)
# In production, you would use tools like detect-secrets or gitleaks
SECRET_PATTERNS=(
    "api_key.*['\"]([A-Za-z0-9_-]{20,})['\"]"
    "secret.*['\"]([A-Za-z0-9_-]{20,})['\"]"
    "password.*['\"]([A-Za-z0-9_!@#$%^&*()]{8,})['\"]"
    "token.*['\"]([A-Za-z0-9_-]{20,})['\"]"
    "-----BEGIN (RSA |DSA |EC |PGP )?PRIVATE KEY"
    "sk-[A-Za-z0-9]{32,}"  # OpenAI API keys
    "AKIA[0-9A-Z]{16}"     # AWS Access Key IDs
)

SECRETS_FOUND=false

for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        for pattern in "${SECRET_PATTERNS[@]}"; do
            if grep -qE "$pattern" "$file" 2>/dev/null; then
                echo "🚨 Potential secret detected in $file"
                echo "   Pattern: $pattern"
                SECRETS_FOUND=true
            fi
        done
    fi
done

if [ "$SECRETS_FOUND" = true ]; then
    echo "❌ Secret detection failed - please remove secrets before committing"
    echo "💡 Consider using environment variables or configuration files that are .gitignore'd"
    exit 1
fi

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ Secret detection completed in ${duration}s - no secrets found"