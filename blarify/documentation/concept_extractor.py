import json
import logging
from typing import Dict, Any, List, Optional
from blarify.llm_descriptions.llm_service import LLMService

logger = logging.getLogger(__name__)


class ConceptExtractor:
    """
    Extracts concepts, entities, and relationships from documentation using LLM.
    
    This class uses Azure OpenAI to analyze documentation content and extract
    structured information about concepts, entities, relationships, and code references.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the concept extractor.
        
        Args:
            llm_service: Optional LLM service instance. If not provided, creates a new one.
        """
        self.llm_service = llm_service or LLMService()
        
    def extract_from_file(self, filepath: str) -> Dict[str, Any]:
        """
        Extract concepts from a documentation file.
        
        Args:
            filepath: Path to the documentation file
            
        Returns:
            Dictionary containing extracted concepts, entities, relationships, and code references
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.extract_from_content(content, filepath)
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return self._empty_result()
    
    def extract_from_content(self, content: str, source_path: str = "") -> Dict[str, Any]:
        """
        Extract concepts from documentation content using LLM.
        
        Args:
            content: Documentation text content
            source_path: Path to the source file (for context)
            
        Returns:
            Dictionary containing extracted information
        """
        if not content.strip():
            return self._empty_result()
        
        # Truncate content if too long
        max_content_length = 8000  # Leave room for prompt
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n[Content truncated...]"
        
        prompt = self._create_extraction_prompt(content)
        
        try:
            response = self.llm_service.generate_description(prompt=prompt)
            
            # Parse JSON response
            result = self._parse_llm_response(response)
            return result
            
        except Exception as e:
            logger.error(f"Error extracting concepts from {source_path}: {e}")
            return self._empty_result()
    
    def _create_extraction_prompt(self, content: str) -> str:
        """
        Create the prompt for concept extraction.
        
        Args:
            content: Documentation content
            
        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"""Analyze the following documentation and extract key information.

Documentation content:
{content}

Extract the following information and return as JSON:

1. **Concepts**: Key ideas, patterns, architectures, or methodologies discussed
   - Include: design patterns, architectural patterns, algorithms, workflows
   - For each concept, provide name and brief description

2. **Entities**: Named components, services, classes, or modules mentioned
   - Include: class names, service names, module names, API endpoints
   - For each entity, provide name, type (class/service/module/api/etc), and description

3. **Relationships**: How concepts and entities relate to each other
   - Include: "uses", "implements", "extends", "contains", "depends on"
   - For each relationship, provide from, to, and type

4. **Code References**: Explicit mentions of code files, functions, or paths
   - Include: file paths, class names with methods, function names
   - For each reference, provide the text and type (file/class/method/function)

Return ONLY valid JSON in this format:
{{
    "concepts": [
        {{"name": "Concept Name", "description": "Brief description"}}
    ],
    "entities": [
        {{"name": "Entity Name", "type": "class|service|module|api|other", "description": "Brief description"}}
    ],
    "relationships": [
        {{"from": "Entity/Concept A", "to": "Entity/Concept B", "type": "relationship type"}}
    ],
    "code_references": [
        {{"text": "path/to/file.py or ClassName.method", "type": "file|class|method|function"}}
    ]
}}"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into structured data.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed dictionary or empty result if parsing fails
        """
        try:
            # Try to extract JSON from the response
            response = response.strip()
            
            # If response is wrapped in markdown code blocks, extract it
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Parse JSON
            result = json.loads(response.strip())
            
            # Validate structure
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            
            # Ensure all required keys exist
            for key in ["concepts", "entities", "relationships", "code_references"]:
                if key not in result:
                    result[key] = []
                elif not isinstance(result[key], list):
                    result[key] = []
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response[:500]}...")  # Show first 500 chars
            return self._empty_result()
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._empty_result()
    
    def _empty_result(self) -> Dict[str, Any]:
        """
        Return an empty result structure.
        
        Returns:
            Dictionary with empty lists for all keys
        """
        return {
            "concepts": [],
            "entities": [],
            "relationships": [],
            "code_references": []
        }