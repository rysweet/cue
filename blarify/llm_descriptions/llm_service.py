import os
import logging
from typing import List, Dict, Optional, Any, Callable
from dotenv import load_dotenv
from openai import AzureOpenAI
import time
from functools import wraps

logger = logging.getLogger(__name__)

load_dotenv()


def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}")
                        raise
                    
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after error: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator


class LLMService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 500
    ):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_MODEL_CHAT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enabled = os.getenv("ENABLE_LLM_DESCRIPTIONS", "true").lower() == "true"
        self.client = None
        
        if not self.enabled:
            logger.info("LLM descriptions are disabled")
            return
        
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            raise ValueError(
                "Azure OpenAI configuration is incomplete. "
                "Please ensure AZURE_OPENAI_KEY (or AZURE_OPENAI_API_KEY), AZURE_OPENAI_ENDPOINT, "
                "and AZURE_OPENAI_MODEL_CHAT (or AZURE_OPENAI_DEPLOYMENT_NAME) are set in your environment."
            )
        
        # Extract base endpoint from full URL if needed
        if "/openai/deployments/" in self.endpoint:
            self.endpoint = self.endpoint.split("/openai/deployments/")[0] + "/"
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        logger.info(f"LLM Service initialized with deployment: {self.deployment_name}")
    
    @retry_on_exception(max_retries=3, delay=1.0)
    def generate_description(self, prompt: str) -> Optional[str]:
        """Generate a description using Azure OpenAI."""
        if not self.enabled:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a code documentation assistant. Provide clear, concise descriptions of code elements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            description = response.choices[0].message.content.strip()
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {str(e)}")
            raise
    
    def generate_batch_descriptions(self, prompts: List[Dict[str, str]], batch_size: int = None) -> Dict[str, Optional[str]]:
        """Generate descriptions for multiple prompts in batches."""
        if not self.enabled:
            return {p["id"]: None for p in prompts}
        
        batch_size = batch_size or int(os.getenv("LLM_BATCH_SIZE", "10"))
        results = {}
        
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(prompts) + batch_size - 1)//batch_size}")
            
            for prompt_data in batch:
                prompt_id = prompt_data["id"]
                prompt_text = prompt_data["prompt"]
                
                try:
                    description = self.generate_description(prompt_text)
                    results[prompt_id] = description
                except Exception as e:
                    logger.error(f"Failed to generate description for {prompt_id}: {str(e)}")
                    results[prompt_id] = None
                
                # Add a small delay between requests to avoid rate limiting
                time.sleep(0.1)
        
        return results
    
    def is_enabled(self) -> bool:
        """Check if LLM descriptions are enabled."""
        return self.enabled