import unittest
from unittest.mock import MagicMock, patch, Mock, call
from blarify.code_references.lsp_helper import (
    LspQueryHelper,
    FileExtensionNotSupported
)
from blarify.code_references.types.Reference import Reference


class TestLspQueryHelper(unittest.TestCase):
    """Test cases for LspQueryHelper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root_uri = "file:///test/project"
        self.helper = LspQueryHelper(self.root_uri)
        
    def test_init(self):
        """Test LspQueryHelper initialization."""
        helper = LspQueryHelper("file:///test", "localhost", 8080)
        self.assertEqual(helper.root_uri, "file:///test")
        self.assertEqual(helper.entered_lsp_servers, {})
        self.assertEqual(helper.language_to_lsp_server, {})
        
    def test_get_language_definition_for_extension_python(self):
        """Test getting language definition for Python files."""
        from blarify.code_hierarchy.languages import PythonDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".py")
        self.assertEqual(result, PythonDefinitions)
        
    def test_get_language_definition_for_extension_javascript(self):
        """Test getting language definition for JavaScript files."""
        from blarify.code_hierarchy.languages import JavascriptDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".js")
        self.assertEqual(result, JavascriptDefinitions)
        
    def test_get_language_definition_for_extension_typescript(self):
        """Test getting language definition for TypeScript files."""
        from blarify.code_hierarchy.languages import TypescriptDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".ts")
        self.assertEqual(result, TypescriptDefinitions)
        
    def test_get_language_definition_for_extension_ruby(self):
        """Test getting language definition for Ruby files."""
        from blarify.code_hierarchy.languages import RubyDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".rb")
        self.assertEqual(result, RubyDefinitions)
        
    def test_get_language_definition_for_extension_csharp(self):
        """Test getting language definition for C# files."""
        from blarify.code_hierarchy.languages import CsharpDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".cs")
        self.assertEqual(result, CsharpDefinitions)
        
    def test_get_language_definition_for_extension_go(self):
        """Test getting language definition for Go files."""
        from blarify.code_hierarchy.languages import GoDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".go")
        self.assertEqual(result, GoDefinitions)
        
    def test_get_language_definition_for_extension_php(self):
        """Test getting language definition for PHP files."""
        from blarify.code_hierarchy.languages import PhpDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".php")
        self.assertEqual(result, PhpDefinitions)
        
    def test_get_language_definition_for_extension_java(self):
        """Test getting language definition for Java files."""
        from blarify.code_hierarchy.languages import JavaDefinitions
        
        result = LspQueryHelper.get_language_definition_for_extension(".java")
        self.assertEqual(result, JavaDefinitions)
        
    def test_get_language_definition_for_unsupported_extension(self):
        """Test getting language definition for unsupported file extension."""
        with self.assertRaises(FileExtensionNotSupported) as context:
            LspQueryHelper.get_language_definition_for_extension(".xyz")
        self.assertIn('File extension ".xyz" is not supported', str(context.exception))
        
    @patch('blarify.code_references.lsp_helper.SyncLanguageServer')
    @patch('blarify.code_references.lsp_helper.MultilspyConfig')
    @patch('blarify.code_references.lsp_helper.MultilspyLogger')
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_create_lsp_server(self, mock_path_calc, mock_logger, mock_config, mock_sync_server):
        """Test creating an LSP server."""
        # Mock language definitions
        mock_lang_def = MagicMock()
        mock_lang_def.get_language_name.return_value = "python"
        
        # Mock PathCalculator
        mock_path_calc.uri_to_path.return_value = "/test/project"
        
        # Mock config
        mock_config_instance = MagicMock()
        mock_config.from_dict.return_value = mock_config_instance
        
        # Mock logger
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        
        # Mock SyncLanguageServer
        mock_server = MagicMock()
        mock_sync_server.create.return_value = mock_server
        
        # Call the method
        result = self.helper._create_lsp_server(mock_lang_def, timeout=20)
        
        # Assertions
        mock_lang_def.get_language_name.assert_called_once()
        mock_config.from_dict.assert_called_once_with({"code_language": "python"})
        mock_logger.assert_called_once()
        mock_path_calc.uri_to_path.assert_called_once_with(self.root_uri)
        mock_sync_server.create.assert_called_once_with(
            mock_config_instance, 
            mock_logger_instance, 
            "/test/project", 
            timeout=20
        )
        self.assertEqual(result, mock_server)
        
    def test_get_or_create_lsp_server_existing(self):
        """Test getting existing LSP server."""
        # Setup existing server
        mock_server = MagicMock()
        self.helper.language_to_lsp_server["python"] = mock_server
        
        # Mock get_language_definition_for_extension
        with patch.object(self.helper, 'get_language_definition_for_extension') as mock_get_lang:
            mock_lang_def = MagicMock()
            mock_lang_def.get_language_name.return_value = "python"
            mock_get_lang.return_value = mock_lang_def
            
            result = self.helper._get_or_create_lsp_server(".py")
            
        self.assertEqual(result, mock_server)
        
    def test_get_or_create_lsp_server_new(self):
        """Test creating new LSP server when none exists."""
        mock_server = MagicMock()
        
        with patch.object(self.helper, 'get_language_definition_for_extension') as mock_get_lang:
            with patch.object(self.helper, '_create_lsp_server') as mock_create:
                with patch.object(self.helper, '_initialize_lsp_server') as mock_init:
                    mock_lang_def = MagicMock()
                    mock_lang_def.get_language_name.return_value = "python"
                    mock_get_lang.return_value = mock_lang_def
                    mock_create.return_value = mock_server
                    
                    result = self.helper._get_or_create_lsp_server(".py", timeout=30)
                    
        mock_create.assert_called_once_with(mock_lang_def, 30)
        mock_init.assert_called_once_with("python", mock_server)
        self.assertEqual(self.helper.language_to_lsp_server["python"], mock_server)
        self.assertEqual(result, mock_server)
        
    def test_initialize_lsp_server(self):
        """Test initializing LSP server."""
        mock_server = MagicMock()
        mock_context = MagicMock()
        mock_server.start_server.return_value = mock_context
        
        self.helper._initialize_lsp_server("python", mock_server)
        
        mock_server.start_server.assert_called_once()
        mock_context.__enter__.assert_called_once()
        self.assertEqual(self.helper.entered_lsp_servers["python"], mock_context)
        
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_get_paths_where_node_is_referenced(self, mock_path_calc):
        """Test getting references for a node."""
        # Mock node
        mock_node = MagicMock()
        mock_node.extension = ".py"
        mock_node.path = "file:///test/file.py"
        mock_node.definition_range.start_dict = {"line": 10, "character": 5}
        
        # Mock LSP server
        mock_server = MagicMock()
        mock_references = [
            {"uri": "file:///test/ref1.py", "range": {"start": {"line": 20, "character": 10}, "end": {"line": 20, "character": 20}}},
            {"uri": "file:///test/ref2.py", "range": {"start": {"line": 30, "character": 15}, "end": {"line": 30, "character": 25}}}
        ]
        
        with patch.object(self.helper, '_get_or_create_lsp_server') as mock_get_server:
            with patch.object(self.helper, '_request_references_with_exponential_backoff') as mock_request:
                mock_get_server.return_value = mock_server
                mock_request.return_value = mock_references
                
                result = self.helper.get_paths_where_node_is_referenced(mock_node)
                
        mock_get_server.assert_called_once_with(".py")
        mock_request.assert_called_once_with(mock_node, mock_server)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Reference)
        
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_request_references_with_exponential_backoff_success(self, mock_path_calc):
        """Test successful reference request."""
        mock_node = MagicMock()
        mock_node.extension = ".py"
        mock_node.path = "file:///test/file.py"
        mock_node.definition_range.start_dict = {"line": 10, "character": 5}
        
        mock_lsp = MagicMock()
        mock_references = [{"uri": "file:///test/ref.py"}]
        mock_lsp.request_references.return_value = mock_references
        mock_path_calc.get_relative_path_from_uri.return_value = "file.py"
        
        result = self.helper._request_references_with_exponential_backoff(mock_node, mock_lsp)
        
        self.assertEqual(result, mock_references)
        mock_lsp.request_references.assert_called_once_with(
            file_path="file.py",
            line=10,
            column=5
        )
        
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_request_references_with_exponential_backoff_retry(self, mock_path_calc):
        """Test reference request with retry on timeout."""
        mock_node = MagicMock()
        mock_node.extension = ".py"
        mock_node.path = "file:///test/file.py"
        mock_node.definition_range.start_dict = {"line": 10, "character": 5}
        
        mock_lsp = MagicMock()
        mock_lsp.request_references.side_effect = [TimeoutError(), [{"uri": "file:///test/ref.py"}]]
        mock_path_calc.get_relative_path_from_uri.return_value = "file.py"
        
        with patch.object(self.helper, '_restart_lsp_for_extension') as mock_restart:
            with patch.object(self.helper, '_get_or_create_lsp_server') as mock_get_server:
                mock_get_server.return_value = mock_lsp
                
                result = self.helper._request_references_with_exponential_backoff(mock_node, mock_lsp)
                
        mock_restart.assert_called_once_with(extension=".py")
        self.assertEqual(len(result), 1)
        
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_request_references_with_exponential_backoff_failure(self, mock_path_calc):
        """Test reference request failing after all retries."""
        mock_node = MagicMock()
        mock_node.extension = ".py"
        mock_node.path = "file:///test/file.py"
        mock_node.definition_range.start_dict = {"line": 10, "character": 5}
        
        mock_lsp = MagicMock()
        mock_lsp.request_references.side_effect = TimeoutError()
        mock_path_calc.get_relative_path_from_uri.return_value = "file.py"
        
        with patch.object(self.helper, '_restart_lsp_for_extension') as mock_restart:
            with patch.object(self.helper, '_get_or_create_lsp_server') as mock_get_server:
                mock_get_server.return_value = mock_lsp
                
                result = self.helper._request_references_with_exponential_backoff(mock_node, mock_lsp)
                
        self.assertEqual(result, [])
        self.assertEqual(mock_restart.call_count, 2)
        
    def test_restart_lsp_for_extension(self):
        """Test restarting LSP server for an extension."""
        mock_server = MagicMock()
        
        with patch.object(self.helper, 'get_language_definition_for_extension') as mock_get_lang:
            with patch.object(self.helper, 'exit_lsp_server') as mock_exit:
                with patch.object(self.helper, '_create_lsp_server') as mock_create:
                    with patch.object(self.helper, '_initialize_lsp_server') as mock_init:
                        mock_lang_def = MagicMock()
                        mock_lang_def.get_language_name.return_value = "python"
                        mock_get_lang.return_value = mock_lang_def
                        mock_create.return_value = mock_server
                        
                        self.helper._restart_lsp_for_extension(".py")
                        
        mock_exit.assert_called_once_with("python")
        mock_create.assert_called_once_with(mock_lang_def)
        mock_init.assert_called_once_with(language="python", lsp=mock_server)
        self.assertEqual(self.helper.language_to_lsp_server["python"], mock_server)
        
    def test_restart_lsp_for_extension_connection_error(self):
        """Test restarting LSP server with connection error."""
        with patch.object(self.helper, 'get_language_definition_for_extension') as mock_get_lang:
            with patch.object(self.helper, 'exit_lsp_server') as mock_exit:
                with patch.object(self.helper, '_create_lsp_server') as mock_create:
                    with patch.object(self.helper, '_initialize_lsp_server') as mock_init:
                        mock_lang_def = MagicMock()
                        mock_lang_def.get_language_name.return_value = "python"
                        mock_get_lang.return_value = mock_lang_def
                        mock_init.side_effect = ConnectionResetError()
                        
                        # Should not raise exception
                        self.helper._restart_lsp_for_extension(".py")
                        
    @patch('blarify.code_references.lsp_helper.threading.Thread')
    def test_exit_lsp_server_with_context(self, mock_thread_class):
        """Test exiting LSP server with context manager."""
        mock_context = MagicMock()
        self.helper.entered_lsp_servers["python"] = mock_context
        self.helper.language_to_lsp_server["python"] = MagicMock()
        
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = False
        mock_thread_class.return_value = mock_thread
        
        self.helper.exit_lsp_server("python")
        
        mock_thread.start.assert_called_once()
        mock_thread.join.assert_called_once_with(timeout=5)
        self.assertNotIn("python", self.helper.entered_lsp_servers)
        self.assertNotIn("python", self.helper.language_to_lsp_server)
        
    @patch('blarify.code_references.lsp_helper.threading.Thread')
    def test_exit_lsp_server_with_timeout(self, mock_thread_class):
        """Test exiting LSP server when context manager times out."""
        mock_context = MagicMock()
        self.helper.entered_lsp_servers["python"] = mock_context
        self.helper.language_to_lsp_server["python"] = MagicMock()
        
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = True  # Thread still alive = timeout
        mock_thread_class.return_value = mock_thread
        
        with patch.object(self.helper, '_manual_cleanup_lsp_server') as mock_cleanup:
            self.helper.exit_lsp_server("python")
            mock_cleanup.assert_called_once_with("python")
            
    def test_exit_lsp_server_no_context(self):
        """Test exiting LSP server without context manager."""
        self.helper.language_to_lsp_server["python"] = MagicMock()
        
        with patch.object(self.helper, '_manual_cleanup_lsp_server') as mock_cleanup:
            self.helper.exit_lsp_server("python")
            mock_cleanup.assert_called_once_with("python")
            
    @patch('blarify.code_references.lsp_helper.psutil')
    @patch('blarify.code_references.lsp_helper.asyncio')
    def test_manual_cleanup_lsp_server(self, mock_asyncio, mock_psutil):
        """Test manual cleanup of LSP server."""
        # Mock server and process
        mock_server = MagicMock()
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_server.language_server.server.process = mock_process
        
        # Mock loop
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = True
        mock_server.loop = mock_loop
        
        self.helper.language_to_lsp_server["python"] = mock_server
        
        # Mock psutil
        mock_psutil.pid_exists.return_value = True
        mock_child = MagicMock()
        mock_psutil.Process.return_value.children.return_value = [mock_child]
        
        # Mock asyncio
        mock_task = MagicMock()
        mock_asyncio.all_tasks.return_value = [mock_task]
        mock_future = MagicMock()
        mock_asyncio.run_coroutine_threadsafe.return_value = mock_future
        
        self.helper._manual_cleanup_lsp_server("python")
        
        # Assertions
        mock_psutil.pid_exists.assert_called_once_with(12345)
        mock_child.terminate.assert_called_once()
        mock_process.terminate.assert_called_once()
        mock_task.cancel.assert_called_once()
        mock_loop.call_soon_threadsafe.assert_called_once_with(mock_loop.stop)
        
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_get_definition_path_for_reference(self, mock_path_calc):
        """Test getting definition path for a reference."""
        mock_reference = MagicMock()
        mock_reference.uri = "file:///test/ref.py"
        mock_reference.range.start.line = 20
        mock_reference.range.start.character = 10
        
        mock_definitions = [{"uri": "file:///test/def.py"}]
        
        with patch.object(self.helper, '_get_or_create_lsp_server') as mock_get_server:
            with patch.object(self.helper, '_request_definition_with_exponential_backoff') as mock_request:
                mock_request.return_value = mock_definitions
                
                result = self.helper.get_definition_path_for_reference(mock_reference, ".py")
                
        self.assertEqual(result, "file:///test/def.py")
        
    @patch('blarify.code_references.lsp_helper.PathCalculator')
    def test_get_definition_path_for_reference_no_definitions(self, mock_path_calc):
        """Test getting definition path when no definitions found."""
        mock_reference = MagicMock()
        
        with patch.object(self.helper, '_get_or_create_lsp_server'):
            with patch.object(self.helper, '_request_definition_with_exponential_backoff') as mock_request:
                mock_request.return_value = []
                
                result = self.helper.get_definition_path_for_reference(mock_reference, ".py")
                
        self.assertEqual(result, "")
        
    def test_shutdown_exit_close(self):
        """Test shutting down all LSP servers."""
        self.helper.language_to_lsp_server = {
            "python": MagicMock(),
            "javascript": MagicMock()
        }
        
        with patch.object(self.helper, 'exit_lsp_server') as mock_exit:
            self.helper.shutdown_exit_close()
            
        self.assertEqual(mock_exit.call_count, 2)
        mock_exit.assert_has_calls([call("python"), call("javascript")], any_order=True)
        self.assertEqual(len(self.helper.language_to_lsp_server), 0)
        self.assertEqual(len(self.helper.entered_lsp_servers), 0)
        
    def test_shutdown_exit_close_with_error(self):
        """Test shutting down with error handling."""
        self.helper.language_to_lsp_server = {"python": MagicMock()}
        
        with patch.object(self.helper, 'exit_lsp_server') as mock_exit:
            mock_exit.side_effect = Exception("Test error")
            
            # Should not raise exception
            self.helper.shutdown_exit_close()
            
        self.assertEqual(len(self.helper.language_to_lsp_server), 0)


if __name__ == '__main__':
    unittest.main()