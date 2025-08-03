from .language_definitions import LanguageDefinitions


class FallbackDefinitions(LanguageDefinitions):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get_language_file_extensions() -> set[str]:
        # Always return an empty set, never None
        return set()
