import unittest
from unittest.mock import patch, MagicMock
import os
from blarify.llm_descriptions.llm_service import LLMService


class TestLLMService(unittest.TestCase):
    
    def setUp(self):
        # Mock environment variables (using both old and new key names)
        self.env_patcher = patch.dict(os.environ, {
            'AZURE_OPENAI_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_MODEL_CHAT': 'test-deployment',
            'AZURE_OPENAI_API_VERSION': '2025-01-01-preview',
            'ENABLE_LLM_DESCRIPTIONS': 'true'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('blarify.llm_descriptions.llm_service.AzureOpenAI')
    def test_init_with_environment_variables(self, mock_azure_openai):
        service = LLMService()
        
        self.assertEqual(service.api_key, 'test-key')
        self.assertEqual(service.endpoint, 'https://test.openai.azure.com/')
        self.assertEqual(service.deployment_name, 'test-deployment')
        self.assertTrue(service.enabled)
        
        mock_azure_openai.assert_called_once()
    
    def test_init_with_disabled_llm(self):
        with patch.dict(os.environ, {'ENABLE_LLM_DESCRIPTIONS': 'false'}):
            service = LLMService()
            self.assertFalse(service.enabled)
            self.assertIsNone(service.client)
    
    def test_init_with_missing_config(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                LLMService()
            
            self.assertIn("Azure OpenAI configuration is incomplete", str(context.exception))
    
    @patch('blarify.llm_descriptions.llm_service.AzureOpenAI')
    def test_generate_description(self, mock_azure_openai):
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is a test description."
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        description = service.generate_description("Test prompt")
        
        self.assertEqual(description, "This is a test description.")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('blarify.llm_descriptions.llm_service.AzureOpenAI')
    def test_generate_description_disabled(self, mock_azure_openai):
        with patch.dict(os.environ, {'ENABLE_LLM_DESCRIPTIONS': 'false'}):
            service = LLMService()
            description = service.generate_description("Test prompt")
            
            self.assertIsNone(description)
            mock_azure_openai.assert_not_called()
    
    @patch('blarify.llm_descriptions.llm_service.AzureOpenAI')
    def test_generate_batch_descriptions(self, mock_azure_openai):
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test description"
        mock_client.chat.completions.create.return_value = mock_response
        
        service = LLMService()
        prompts = [
            {"id": "node1", "prompt": "Prompt 1"},
            {"id": "node2", "prompt": "Prompt 2"}
        ]
        
        results = service.generate_batch_descriptions(prompts, batch_size=2)
        
        self.assertEqual(len(results), 2)
        self.assertIn("node1", results)
        self.assertIn("node2", results)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
    
    @patch('blarify.llm_descriptions.llm_service.AzureOpenAI')
    @patch('blarify.llm_descriptions.llm_service.time.sleep')
    def test_retry_on_exception(self, mock_sleep, mock_azure_openai):
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client
        
        # Mock the response to fail twice then succeed
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))])
        ]
        
        service = LLMService()
        description = service.generate_description("Test prompt")
        
        self.assertEqual(description, "Success")
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == '__main__':
    unittest.main()