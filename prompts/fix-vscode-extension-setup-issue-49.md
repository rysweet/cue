# Fix VS Code Extension Setup Failure (Issue #49)

## Context
The Blarify VS Code extension is failing to set up correctly due to two critical issues:
1. A missing README.md file that's referenced in pyproject.toml causes pip install to fail
2. The extension attempts to run ingestion before setup completes

## Problem Statement
When the extension starts up, it tries to set up a Python environment by running `pip install -e` on the bundled directory. This fails because pyproject.toml references a README.md file that doesn't exist in the bundled extension directory. Additionally, the extension doesn't wait for setup to complete before attempting ingestion.

## Acceptance Criteria
1. Extension setup completes successfully without FileNotFoundError
2. All required files are properly bundled with the extension
3. Ingestion only starts after successful setup completion
4. Proper error handling and user feedback if setup fails
5. Extension can be installed and activated without errors

## Technical Requirements
1. Fix the missing README.md issue by either:
   - Including README.md in the bundled files
   - Updating pyproject.toml to not reference README.md
   - Creating a minimal README.md if needed
2. Implement proper setup/ingestion synchronization:
   - Setup must complete before ingestion starts
   - Clear success/failure states
   - Proper async/await or promise handling
3. Add error handling for setup failures
4. Test the complete setup flow

## Implementation Notes
- Check the VS Code extension bundling configuration
- Review pyproject.toml to understand README.md requirements
- Look at the setup.py and extension activation code
- Consider using VS Code's activation events properly
- May need to modify the extension's package.json

## Testing
1. Build and package the extension
2. Install in VS Code Insiders
3. Verify setup completes without errors
4. Verify ingestion only starts after setup
5. Test failure scenarios (e.g., network issues)

## Files to Review
- VS Code extension's package.json
- pyproject.toml in bundled directory
- setup.py
- Extension activation code
- Extension bundling/build configuration