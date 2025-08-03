import logging
import os
from pathlib import Path

from blarify.vendor.multilspy import SyncLanguageServer

from blarify.vendor.multilspy.multilspy_config import MultilspyConfig
from blarify.vendor.multilspy.multilspy_logger import MultilspyLogger


def ensure_language_server_installed(language: str) -> None:
    """
    Ensure that the language server for the given language is installed.
    """

    my_logger = logging.getLogger(__name__)

    # Use Any type to avoid partially unknown type issues
    from typing import Any, Dict
    config_dict: Dict[str, Any] = {"code_language": language}
    config = MultilspyConfig.from_dict(config_dict)  # type: ignore
    logger = MultilspyLogger()
    current_dir_path = os.path.join(str(Path(__file__).resolve().parent))

    if language == "csharp":
        print(f"Starting language server for {language}")
        from blarify.vendor.multilspy.language_servers.omnisharp.omnisharp import OmniSharp
        # Restore original call with 3 arguments as expected
        OmniSharp.setupRuntimeDependencies(None, logger, config)  # type: ignore
        print(f"Started language server for {language}")
        return

    print(f"Starting language server for {language}, current_dir_path: {current_dir_path}")

    try:
        print(f"Starting language server for {language}")
        lsp = SyncLanguageServer.create(
            config=config, logger=logger, repository_root_path=current_dir_path, timeout=15
        )
        with lsp.start_server():
            my_logger.info(f"Started language server for {language}")
    except Exception as e:
        my_logger.error(f"Failed to start language server for {language}: {e}")


if __name__ == "__main__":
    ensure_language_server_installed("csharp")
