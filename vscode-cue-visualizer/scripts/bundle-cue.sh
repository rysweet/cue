#!/bin/bash

# Bundle cue and its dependencies into the VS Code extension

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
BUNDLED_DIR="$EXT_DIR/bundled"

echo "Bundling cue into VS Code extension..."

# Clean and create bundled directory
rm -rf "$BUNDLED_DIR"
mkdir -p "$BUNDLED_DIR"

# Copy cue source
echo "Copying cue source..."
cp -r "$EXT_DIR/../cue" "$BUNDLED_DIR/"
cp "$EXT_DIR/../pyproject.toml" "$BUNDLED_DIR/"
cp "$EXT_DIR/../poetry.lock" "$BUNDLED_DIR/" 2>/dev/null || true

# Copy README.md to fix pyproject.toml reference
echo "Copying README.md for pyproject.toml..."
if [ -f "$EXT_DIR/../README.md" ]; then
    cp "$EXT_DIR/../README.md" "$BUNDLED_DIR/"
else
    # Create a minimal README.md if it doesn't exist
    cat > "$BUNDLED_DIR/README.md" << 'EOF'
# cue

A simple graph builder based on LSP calls for code visualization and analysis.

This is the bundled version included with the cue VS Code extension.
EOF
fi

# Copy neo4j-container-manager
echo "Copying neo4j-container-manager..."
if [ ! -d "$EXT_DIR/../neo4j-container-manager/dist" ]; then
    # Build it first if dist doesn't exist  
    echo "Building neo4j-container-manager..."
    cd "$EXT_DIR/../neo4j-container-manager"
    npm run build
    cd "$EXT_DIR"
fi

# Copy the built files and dependencies
cp -r "$EXT_DIR/../neo4j-container-manager/dist" "$BUNDLED_DIR/neo4j-container-manager"

# Copy package.json so Node can understand this is a proper module
cp "$EXT_DIR/../neo4j-container-manager/package.json" "$BUNDLED_DIR/neo4j-container-manager/"

# Copy node_modules to include all dependencies
echo "Copying neo4j-container-manager dependencies..."
cp -r "$EXT_DIR/../neo4j-container-manager/node_modules" "$BUNDLED_DIR/neo4j-container-manager/"

# Fix package.json paths since we're copying dist files to root
echo "Fixing neo4j-container-manager package.json paths..."
sed -i.bak 's|"dist/index.js"|"index.js"|g' "$BUNDLED_DIR/neo4j-container-manager/package.json"
sed -i.bak 's|"dist/index.d.ts"|"index.d.ts"|g' "$BUNDLED_DIR/neo4j-container-manager/package.json"
rm "$BUNDLED_DIR/neo4j-container-manager/package.json.bak" 2>/dev/null || true

# Create a requirements.txt from pyproject.toml
echo "Extracting dependencies..."
cd "$EXT_DIR/.."
poetry export --without-hashes --format requirements.txt > "$BUNDLED_DIR/requirements.txt" 2>/dev/null || {
    # Fallback: manually extract key dependencies
    cat > "$BUNDLED_DIR/requirements.txt" << EOF
neo4j>=5.14.0
tree-sitter>=0.23.0
tree-sitter-python>=0.23.2
tree-sitter-javascript>=0.23.0
tree-sitter-typescript>=0.23.2
pygls>=1.3.1
jedi>=0.19.2
pathspec>=0.12.1
requests>=2.32.3
typing-extensions>=4.12.2
psutil>=5.9.0
EOF
}

# Create a setup script for first-time users
cat > "$BUNDLED_DIR/setup.py" << 'EOF'
#!/usr/bin/env python3
"""Setup script to install cue dependencies in extension's virtual environment."""

import os
import sys
import subprocess
import venv
from pathlib import Path

def setup_cue():
    bundled_dir = Path(__file__).parent
    venv_dir = bundled_dir / "venv"
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("Creating Python virtual environment...")
        venv.create(venv_dir, with_pip=True)
    
    # Get the pip executable from the virtual environment
    if sys.platform == "win32":
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"
        python_exe = venv_dir / "bin" / "python"
    
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    requirements_file = bundled_dir / "requirements.txt"
    if requirements_file.exists():
        print("Installing dependencies...")
        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
    
    # Install cue in development mode
    cue_dir = bundled_dir / "cue"
    if cue_dir.exists():
        print("Installing cue...")
        try:
            subprocess.run([str(pip_exe), "install", "-e", str(bundled_dir)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing cue: {e}")
            # Check if pyproject.toml exists and has README reference
            pyproject_file = bundled_dir / "pyproject.toml"
            if pyproject_file.exists():
                print("Checking pyproject.toml for README.md reference...")
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    if 'readme = "README.md"' in content and not (bundled_dir / "README.md").exists():
                        print("Creating missing README.md file...")
                        with open(bundled_dir / "README.md", 'w') as readme:
                            readme.write("# cue\\n\\nA simple graph builder based on LSP calls.")
                        # Retry installation
                        print("Retrying cue installation...")
                        subprocess.run([str(pip_exe), "install", "-e", str(bundled_dir)], check=True)
                    else:
                        raise e
            else:
                raise e
    
    print("Setup complete!")
    return str(python_exe)

if __name__ == "__main__":
    setup_cue()
EOF

echo "Bundle complete!"
echo "The extension will set up Python dependencies on first run."