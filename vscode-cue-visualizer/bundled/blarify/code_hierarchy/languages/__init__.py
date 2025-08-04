from .language_definitions import LanguageDefinitions, BodyNodeNotFound, IdentifierNodeNotFound
from .fallback_definitions import FallbackDefinitions

# Import language-specific definitions conditionally to avoid failures
# when tree-sitter language modules are not installed
import importlib
import warnings

# Dictionary to store successfully imported language definitions
_language_definitions = {}

# Try to import each language definition module
_language_modules = {
    'python': ('python_definitions', 'PythonDefinitions'),
    'javascript': ('javascript_definitions', 'JavascriptDefinitions'),
    'typescript': ('typescript_definitions', 'TypescriptDefinitions'),
    'ruby': ('ruby_definitions', 'RubyDefinitions'),
    'csharp': ('csharp_definitions', 'CsharpDefinitions'),
    'go': ('go_definitions', 'GoDefinitions'),
    'php': ('php_definitions', 'PhpDefinitions'),
    'java': ('java_definitions', 'JavaDefinitions'),
}

for lang_name, (module_name, class_name) in _language_modules.items():
    try:
        module = importlib.import_module(f'.{module_name}', package='blarify.code_hierarchy.languages')
        definition_class = getattr(module, class_name)
        _language_definitions[lang_name] = definition_class
        # Make the class available at module level for backward compatibility
        globals()[class_name] = definition_class
    except ImportError as e:
        warnings.warn(f"Could not import {lang_name} language support: {e}. {lang_name} files will be skipped.")
    except Exception as e:
        warnings.warn(f"Error importing {lang_name} language support: {e}. {lang_name} files will be skipped.")

# Function to get available language definitions
def get_available_languages():
    """Returns a list of available language names that have been successfully imported."""
    return list(_language_definitions.keys())

def get_language_definition(language_name):
    """Returns the language definition class for the given language name, or None if not available."""
    return _language_definitions.get(language_name)