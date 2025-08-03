#!/usr/bin/env python3
"""Setup script to install Blarify dependencies in extension's virtual environment."""

import os
import sys
import subprocess
import venv
from pathlib import Path

def setup_blarify():
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
    
    # Install Blarify in development mode
    blarify_dir = bundled_dir / "blarify"
    if blarify_dir.exists():
        print("Installing Blarify...")
        try:
            subprocess.run([str(pip_exe), "install", "-e", str(bundled_dir)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing Blarify: {e}")
            # Check if pyproject.toml exists and has README reference
            pyproject_file = bundled_dir / "pyproject.toml"
            if pyproject_file.exists():
                print("Checking pyproject.toml for README.md reference...")
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    if 'readme = "README.md"' in content and not (bundled_dir / "README.md").exists():
                        print("Creating missing README.md file...")
                        with open(bundled_dir / "README.md", 'w') as readme:
                            readme.write("# Blarify\n\nA simple graph builder based on LSP calls.")
                        # Retry installation
                        print("Retrying Blarify installation...")
                        subprocess.run([str(pip_exe), "install", "-e", str(bundled_dir)], check=True)
                    else:
                        raise e
            else:
                raise e
    
    print("Setup complete!")
    return str(python_exe)

if __name__ == "__main__":
    setup_blarify()
