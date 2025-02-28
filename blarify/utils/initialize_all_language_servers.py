import logging
import os
from pathlib import Path
from blarify.vendor.multilspy import SyncLanguageServer

from blarify.code_hierarchy.languages import (
    PythonDefinitions,
    JavascriptDefinitions,
    RubyDefinitions,
    TypescriptDefinitions,
    CsharpDefinitions,
    GoDefinitions,
)

from blarify.vendor.multilspy.multilspy_config import MultilspyConfig
from blarify.vendor.multilspy.multilspy_logger import MultilspyLogger


def initialize_all_language_servers():
    """
    Initialize all language servers
    """
    languages = [
        PythonDefinitions.get_language_name(),
        JavascriptDefinitions.get_language_name(),
        RubyDefinitions.get_language_name(),
        TypescriptDefinitions.get_language_name(),
        CsharpDefinitions.get_language_name(),
        GoDefinitions.get_language_name(),
    ]

    my_logger = logging.getLogger(__name__)

    for language in languages:
        config = MultilspyConfig.from_dict({"code_language": language})
        logger = MultilspyLogger()
        current_dir_path = os.path.join(str(Path(__file__).resolve().parent))

        print(f"Starting language server for {language}, current_dir_path: {current_dir_path}")

        try:
            lsp: SyncLanguageServer = SyncLanguageServer.create(
                config=config, logger=logger, repository_root_path=current_dir_path, timeout=15
            )
            with lsp.start_server():
                my_logger.info(f"Started language server for {language}")
        except Exception as e:
            my_logger.warning(f"Failed to start language server for {language}: {e}")


if __name__ == "__main__":
    initialize_all_language_servers()
