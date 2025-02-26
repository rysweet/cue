from contextlib import asynccontextmanager
import logging
import os
import pathlib
from typing import AsyncIterator
from blarify.vendor.multilspy.language_server import LanguageServer
from blarify.vendor.multilspy.lsp_protocol_handler.server import ProcessLaunchInfo
import json


class DartLanguageServer(LanguageServer):
    """
    Provides Dart specific instantiation of the LanguageServer class. Contains various configurations and settings specific to Dart.
    """

    def __init__(self, config, logger, repository_root_path):
        """
        Creates a DartServer instance. This class is not meant to be instantiated directly. Use LanguageServer.create() instead.
        """

        executable_path = (
            "dart language-server --client-id my-editor.my-plugin --client-version 1.2"
        )
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=executable_path, cwd=repository_root_path),
            "dart",
        )

    def _get_initialize_params(self, repository_absolute_path: str):
        """
        Returns the initialize params for the Dart Language Server.
        """
        with open(
            os.path.join(os.path.dirname(__file__), "initialize_params.json"), "r"
        ) as f:
            d = json.load(f)

        del d["_description"]

        d["processId"] = os.getpid()
        assert d["rootPath"] == "$rootPath"
        d["rootPath"] = repository_absolute_path

        assert d["rootUri"] == "$rootUri"
        d["rootUri"] = pathlib.Path(repository_absolute_path).as_uri()

        assert d["workspaceFolders"][0]["uri"] == "$uri"
        d["workspaceFolders"][0]["uri"] = pathlib.Path(
            repository_absolute_path
        ).as_uri()

        assert d["workspaceFolders"][0]["name"] == "$name"
        d["workspaceFolders"][0]["name"] = os.path.basename(repository_absolute_path)

        return d

    @asynccontextmanager
    async def start_server(self) -> AsyncIterator["DartLanguageServer"]:
        """
        Start the language server and yield when the server is ready.
        """

        async def execute_client_command_handler(params):
            return []

        async def do_nothing(params):
            return

        async def check_experimental_status(params):
            pass

        async def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        self.server.on_request("client/registerCapability", do_nothing)
        self.server.on_notification("language/status", do_nothing)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request(
            "workspace/executeClientCommand", execute_client_command_handler
        )
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)
        self.server.on_notification("language/actionableNotification", do_nothing)
        self.server.on_notification(
            "experimental/serverStatus", check_experimental_status
        )

        async with super().start_server():
            self.logger.log(
                "Starting dart-language-server server process", logging.INFO
            )
            await self.server.start()
            initialize_params = self._get_initialize_params(self.repository_root_path)
            self.logger.log(
                "Sending initialize request to dart-language-server",
                logging.DEBUG,
            )
            init_response = await self.server.send_request(
                "initialize", initialize_params
            )
            self.logger.log(
                f"Received initialize response from dart-language-server: {init_response}",
                logging.INFO,
            )

            self.server.notify.initialized({})

            yield self

            await self.server.shutdown()
            await self.server.stop()
