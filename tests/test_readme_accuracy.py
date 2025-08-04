"""
Tests to validate the accuracy of information in README.md
"""
import os
import pytest
from pathlib import Path
import json
import re
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python versions


def test_readme_exists():
    """Test that README.md exists in the root directory."""
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md should exist in root directory"


def test_python_version_accuracy():
    """Test that Python version requirements in README match pyproject.toml."""
    # Read pyproject.toml
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml should exist"
    
    with open(pyproject_path, 'rb') as f:
        pyproject_data = tomllib.load(f)
    
    python_requirement = pyproject_data['tool']['poetry']['dependencies']['python']
    
    # Read README.md
    readme_path = Path("README.md")
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Check if Python version is mentioned correctly
    assert "3.10-3.14" in readme_content, "README should mention correct Python version range"
    assert ">=3.10,<=3.14" in python_requirement, "pyproject.toml should have matching Python requirement"


def test_package_name_consistency():
    """Test that package name is consistent between README and pyproject.toml."""
    # Read pyproject.toml
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, 'rb') as f:
        pyproject_data = tomllib.load(f)
    
    package_name = pyproject_data['tool']['poetry']['name']
    
    # Read README.md
    readme_path = Path("README.md")
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Check package installation command
    assert f"pip install {package_name}" in readme_content, f"README should mention 'pip install {package_name}'"


def test_vscode_extension_directory_exists():
    """Test that VS Code extension directory mentioned in README exists."""
    vscode_dir = Path("vscode-blarify-visualizer")
    assert vscode_dir.exists() and vscode_dir.is_dir(), "vscode-blarify-visualizer directory should exist"
    
    # Check for key files
    package_json = vscode_dir / "package.json"
    assert package_json.exists(), "VS Code extension should have package.json"


def test_mcp_server_directory_exists():
    """Test that MCP server directory mentioned in README exists."""
    mcp_dir = Path("mcp-blarify-server")
    assert mcp_dir.exists() and mcp_dir.is_dir(), "mcp-blarify-server directory should exist"
    
    # Check for key files
    requirements = mcp_dir / "requirements.txt"
    server_py = mcp_dir / "src" / "server.py"
    assert requirements.exists(), "MCP server should have requirements.txt"
    assert server_py.exists(), "MCP server should have src/server.py"


def test_language_support_accuracy():
    """Test that language support claims match actual implementation."""
    # Check if language definition files exist
    lang_dir = Path("cue/code_hierarchy/languages")
    assert lang_dir.exists(), "Language definitions directory should exist"
    
    # Core languages mentioned in README
    core_languages = ["python", "javascript", "typescript", "java", "go"]
    additional_languages = ["ruby", "csharp", "php"]
    
    for lang in core_languages + additional_languages:
        lang_file = lang_dir / f"{lang}_definitions.py"
        assert lang_file.exists(), f"Language definition for {lang} should exist"


def test_architecture_components_exist():
    """Test that architectural components mentioned in README exist."""
    # Core directories mentioned in architecture
    core_dirs = [
        "cue/code_hierarchy",
        "cue/code_references", 
        "cue/db_managers",
        "cue/documentation",
        "cue/filesystem",
        "cue/graph",
        "cue/llm_descriptions",
        "cue/project_file_explorer"
    ]
    
    for dir_path in core_dirs:
        path = Path(dir_path)
        assert path.exists() and path.is_dir(), f"Directory {dir_path} should exist"


def test_example_code_imports():
    """Test that example code imports in README are valid."""
    # Test GraphBuilder import
    try:
        from cue.prebuilt.graph_builder import GraphBuilder
    except ImportError:
        pytest.fail("GraphBuilder import from README example should work")
    
    # Test Neo4jManager import
    try:
        from cue.db_managers.neo4j_manager import Neo4jManager
    except ImportError:
        pytest.fail("Neo4jManager import from README example should work")


def test_quickstart_guide_exists():
    """Test that quickstart guide referenced in README exists."""
    quickstart_path = Path("docs/quickstart.md")
    assert quickstart_path.exists(), "Quickstart guide should exist at docs/quickstart.md"


def test_github_links_format():
    """Test that GitHub links in README are properly formatted."""
    readme_path = Path("README.md")
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Check for GitHub repository URL
    assert "github.com/rysweet/cue" in readme_content, "README should contain correct GitHub repository URL"
    
    # Check for issues link
    assert "https://github.com/rysweet/cue/issues" in readme_content, "README should contain GitHub issues link"


def test_license_file_exists():
    """Test that license file referenced in README exists."""
    license_paths = [Path("LICENSE.md"), Path("LICENSE"), Path("LICENSE.txt")]
    license_exists = any(path.exists() for path in license_paths)
    assert license_exists, "License file should exist (LICENSE.md, LICENSE, or LICENSE.txt)"


def test_neo4j_container_manager_exists():
    """Test that Neo4j container manager mentioned in README exists."""
    container_manager_dir = Path("neo4j-container-manager")
    assert container_manager_dir.exists(), "neo4j-container-manager directory should exist"
    
    package_json = container_manager_dir / "package.json"
    assert package_json.exists(), "Neo4j container manager should have package.json"


def test_environment_variables_documented():
    """Test that documented environment variables are comprehensive."""
    readme_path = Path("README.md")
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Key environment variables that should be documented
    required_env_vars = [
        "NEO4J_URI",
        "NEO4J_USERNAME", 
        "NEO4J_PASSWORD",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "ENABLE_LLM_DESCRIPTIONS"
    ]
    
    for env_var in required_env_vars:
        assert env_var in readme_content, f"Environment variable {env_var} should be documented in README"


def test_commands_exist_in_vscode_extension():
    """Test that VS Code commands mentioned in README exist in package.json."""
    vscode_dir = Path("vscode-blarify-visualizer")
    package_json = vscode_dir / "package.json"
    
    if package_json.exists():
        with open(package_json, 'r') as f:
            package_data = json.load(f)
        
        # Check if commands are defined
        if 'contributes' in package_data and 'commands' in package_data['contributes']:
            commands = [cmd['command'] for cmd in package_data['contributes']['commands']]
            
            # Commands mentioned in README
            expected_commands_patterns = [
                r".*[Aa]nalyze.*[Ww]orkspace.*",
                r".*[Ss]how.*[Vv]isualization.*",
                r".*[Uu]pdate.*[Gg]raph.*"
            ]
            
            # At least some commands should match patterns
            found_commands = 0
            for pattern in expected_commands_patterns:
                for cmd in commands:
                    if re.search(pattern, cmd, re.IGNORECASE):
                        found_commands += 1
                        break
            
            assert found_commands > 0, "VS Code extension should have commands matching README descriptions"


def test_tree_sitter_dependencies():
    """Test that tree-sitter dependencies mentioned in README are in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, 'rb') as f:
        pyproject_data = tomllib.load(f)
    
    dependencies = pyproject_data['tool']['poetry']['dependencies']
    
    # Core tree-sitter parsers that should be present
    expected_parsers = [
        "tree-sitter-python",
        "tree-sitter-javascript", 
        "tree-sitter-typescript",
        "tree-sitter-java",
        "tree-sitter-go"
    ]
    
    for parser in expected_parsers:
        assert parser in dependencies, f"Tree-sitter parser {parser} should be in dependencies"


def test_docs_directory_exists():
    """Test that docs directory referenced in README exists."""
    docs_dir = Path("docs")
    assert docs_dir.exists() and docs_dir.is_dir(), "docs directory should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])