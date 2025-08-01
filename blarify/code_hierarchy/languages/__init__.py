# Lazy import to avoid circular dependencies
# Import language definitions classes only when needed at runtime

def __getattr__(name: str):
    """Lazy loading to prevent import cycles"""
    if name == "LanguageDefinitions":
        from .language_definitions import LanguageDefinitions
        return LanguageDefinitions
    elif name == "BodyNodeNotFound":
        from .language_definitions import BodyNodeNotFound
        return BodyNodeNotFound
    elif name == "IdentifierNodeNotFound":
        from .language_definitions import IdentifierNodeNotFound
        return IdentifierNodeNotFound
    elif name == "PythonDefinitions":
        from .python_definitions import PythonDefinitions
        return PythonDefinitions
    elif name == "JavascriptDefinitions":
        from .javascript_definitions import JavascriptDefinitions
        return JavascriptDefinitions
    elif name == "TypescriptDefinitions":
        from .typescript_definitions import TypescriptDefinitions
        return TypescriptDefinitions
    elif name == "RubyDefinitions":
        from .ruby_definitions import RubyDefinitions
        return RubyDefinitions
    elif name == "FallbackDefinitions":
        from .fallback_definitions import FallbackDefinitions
        return FallbackDefinitions
    elif name == "CsharpDefinitions":
        from .csharp_definitions import CsharpDefinitions
        return CsharpDefinitions
    elif name == "GoDefinitions":
        from .go_definitions import GoDefinitions
        return GoDefinitions
    elif name == "PhpDefinitions":
        from .php_definitions import PhpDefinitions
        return PhpDefinitions
    elif name == "JavaDefinitions":
        from .java_definitions import JavaDefinitions
        return JavaDefinitions
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")