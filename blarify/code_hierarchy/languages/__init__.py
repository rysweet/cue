from .language_definitions import LanguageDefinitions, BodyNodeNotFound, IdentifierNodeNotFound
from .fallback_definitions import FallbackDefinitions

# Public API exports
__all__ = [
    'LanguageDefinitions', 'BodyNodeNotFound', 'IdentifierNodeNotFound', 'FallbackDefinitions',
    'get_available_languages', 'get_language_definition'
]

# Import language-specific definitions conditionally to avoid failures
# when tree-sitter language modules are not installed
import importlib
import warnings
from typing import List, Dict, Type, Optional

# Dictionary to store successfully imported language definitions
_language_definitions: Dict[str, Type[LanguageDefinitions]] = {}

# Language module definitions for lazy loading
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

def __getattr__(name: str):
    """Lazy import mechanism to break circular dependencies."""
    # First check if it's a known language definition class
    for lang_name, (module_name, class_name) in _language_modules.items():
        if name == class_name:
            if name not in globals():
                try:
                    module = importlib.import_module(f'.{module_name}', package='blarify.code_hierarchy.languages')
                    definition_class = getattr(module, class_name)
                    _language_definitions[lang_name] = definition_class
                    globals()[class_name] = definition_class
                    return definition_class
                except ImportError as e:
                    warnings.warn(f"Could not import {lang_name} language support: {e}. {lang_name} files will be skipped.")
                    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
                except Exception as e:
                    warnings.warn(f"Error importing {lang_name} language support: {e}. {lang_name} files will be skipped.")
                    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
            else:
                return globals()[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Function to get available language definitions
def get_available_languages() -> List[str]:
    """Returns a list of available language names that have been successfully imported."""
    # Force import all languages to check availability
    for lang_name, (module_name, class_name) in _language_modules.items():
        if lang_name not in _language_definitions:
            try:
                module = importlib.import_module(f'.{module_name}', package='blarify.code_hierarchy.languages')
                definition_class = getattr(module, class_name)
                _language_definitions[lang_name] = definition_class
            except (ImportError, Exception):
                pass  # Language not available
    return list(_language_definitions.keys())

def get_language_definition(language_name: str) -> Optional[Type[LanguageDefinitions]]:
    """Returns the language definition class for the given language name, or None if not available."""
    # Try to load if not already loaded
    if language_name not in _language_definitions and language_name in _language_modules:
        module_name, class_name = _language_modules[language_name]
        try:
            module = importlib.import_module(f'.{module_name}', package='blarify.code_hierarchy.languages')
            definition_class = getattr(module, class_name)
            _language_definitions[language_name] = definition_class
        except (ImportError, Exception):
            return None
    return _language_definitions.get(language_name)