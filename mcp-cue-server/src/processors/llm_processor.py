"""LLM processor for organizing and structuring graph data."""

import json
import logging
from typing import Dict, Any, List
from openai import AzureOpenAI

from ..config import Config

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Processes graph data using LLM to create structured output."""
    
    def __init__(self):
        """Initialize the LLM processor."""
        self.enabled = Config.AZURE_OPENAI_API_KEY is not None
        
        if self.enabled:
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            self.deployment_name = Config.AZURE_OPENAI_DEPLOYMENT_NAME
        else:
            logger.warning("LLM processing disabled - no Azure OpenAI API key provided")
            self.client = None
    
    def organize_file_context(self, context: Dict[str, Any]) -> str:
        """Organize file context into structured Markdown."""
        if not context or not context.get("file"):
            return "# File Not Found\n\nThe requested file could not be found in the graph."
        
        file_info = context["file"]
        file_path = file_info.get("path", "Unknown")
        
        # Build markdown without LLM if disabled
        if not self.enabled:
            return self._build_file_context_markdown(context)
        
        # Use LLM to organize the context
        prompt = self._create_file_context_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant. Organize the provided graph data into clear, structured Markdown that helps developers understand the code context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return self._build_file_context_markdown(context)
    
    def organize_symbol_context(self, context: Dict[str, Any]) -> str:
        """Organize symbol context into structured Markdown."""
        if not context or not context.get("symbol"):
            return "# Symbol Not Found\n\nThe requested symbol could not be found in the graph."
        
        # Build markdown without LLM if disabled
        if not self.enabled:
            return self._build_symbol_context_markdown(context)
        
        # Use LLM to organize the context
        prompt = self._create_symbol_context_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant. Organize the provided symbol information into clear, structured Markdown that helps developers understand how the symbol is used."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return self._build_symbol_context_markdown(context)
    
    def create_implementation_plan(self, change_request: str, impact_analysis: Dict[str, Any]) -> str:
        """Create an implementation plan based on change request and impact analysis."""
        if not self.enabled:
            return self._build_basic_implementation_plan(change_request, impact_analysis)
        
        prompt = self._create_implementation_plan_prompt(change_request, impact_analysis)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a software architect. Create detailed implementation plans that consider dependencies, testing, and documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return self._build_basic_implementation_plan(change_request, impact_analysis)
    
    def extract_entities_from_request(self, change_request: str) -> List[str]:
        """Extract entity names from a change request."""
        if not self.enabled:
            # Basic extraction without LLM
            return self._extract_entities_basic(change_request)
        
        prompt = f"""Extract all code entities (classes, functions, modules, files) mentioned in this change request.
Return them as a JSON array of strings.

Change request: {change_request}

Return only the JSON array, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a code parser. Extract entity names from text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # Try to parse JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            entities = json.loads(content.strip())
            return entities if isinstance(entities, list) else []
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return self._extract_entities_basic(change_request)
    
    def _create_file_context_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for file context organization."""
        return f"""Organize this file context into clear Markdown:

File: {context['file'].get('path', 'Unknown')}

Contents (classes/functions): {json.dumps(context.get('contents', []), indent=2)}

Imports: {json.dumps(context.get('imports', []), indent=2)}

Imported by: {json.dumps(context.get('importers', []), indent=2)}

Documentation: {json.dumps(context.get('documentation', []), indent=2)}

Description: {json.dumps(context.get('description', {}), indent=2)}

Create a well-structured Markdown document with:
1. File overview
2. What it contains (classes, functions)
3. Dependencies (what it imports)
4. Usage (what imports it)
5. Related documentation
6. Any available descriptions

Use clear headers and formatting."""
    
    def _create_symbol_context_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for symbol context organization."""
        symbol = context['symbol']
        return f"""Organize this symbol context into clear Markdown:

Symbol: {symbol.get('name', 'Unknown')} (Type: {', '.join(symbol.get('_labels', []))})

File: {json.dumps(context.get('file', {}), indent=2)}

Inheritance: 
- Parents: {json.dumps(context.get('parents', []), indent=2)}
- Children: {json.dumps(context.get('children', []), indent=2)}
- Interfaces: {json.dumps(context.get('interfaces', []), indent=2)}

Members:
- Methods: {json.dumps(context.get('methods', []), indent=2)}
- Attributes: {json.dumps(context.get('attributes', []), indent=2)}

Usage:
- Called by: {json.dumps(context.get('callers', []), indent=2)}
- Calls: {json.dumps(context.get('callees', []), indent=2)}
- Referenced by: {json.dumps(context.get('referencers', []), indent=2)}

Documentation: {json.dumps(context.get('documentation', []), indent=2)}

Description: {json.dumps(context.get('description', {}), indent=2)}

Create a well-structured Markdown document that explains:
1. What the symbol is and where it's defined
2. Its inheritance/implementation hierarchy
3. Its members (for classes)
4. How it's used in the codebase
5. Related documentation"""
    
    def _create_implementation_plan_prompt(self, change_request: str, impact_analysis: Dict[str, Any]) -> str:
        """Create prompt for implementation plan generation."""
        return f"""Create an implementation plan for this change request:

Change Request: {change_request}

Impact Analysis:
{json.dumps(impact_analysis, indent=2)}

Create a detailed implementation plan that includes:
1. Summary of the change
2. Impact analysis (affected components)
3. Step-by-step implementation plan
4. Files to create/modify/delete
5. Required tests
6. Documentation updates
7. Dependencies to consider

Format as clear Markdown with numbered steps and specific file paths."""
    
    def _build_file_context_markdown(self, context: Dict[str, Any]) -> str:
        """Build file context markdown without LLM."""
        file_info = context["file"]
        md = f"# Context for File: {file_info.get('path', 'Unknown')}\n\n"
        
        if desc := context.get("description"):
            md += f"## Overview\n{desc.get('description', 'No description available')}\n\n"
        
        if contents := context.get("contents"):
            md += "## Contains\n"
            for item in contents:
                item_type = item.get("_labels", ["Unknown"])[0]
                md += f"- **{item_type}**: {item.get('name', 'Unknown')}\n"
            md += "\n"
        
        if imports := context.get("imports"):
            md += "## Dependencies\n"
            for imp in imports:
                md += f"- {imp.get('name', imp.get('path', 'Unknown'))}\n"
            md += "\n"
        
        if importers := context.get("importers"):
            md += "## Used By\n"
            for imp in importers:
                md += f"- {imp.get('path', 'Unknown')}\n"
            md += "\n"
        
        return md
    
    def _build_symbol_context_markdown(self, context: Dict[str, Any]) -> str:
        """Build symbol context markdown without LLM."""
        symbol = context["symbol"]
        symbol_type = ", ".join(symbol.get("_labels", ["Unknown"]))
        
        md = f"# Context for Symbol: {symbol.get('name', 'Unknown')}\n\n"
        md += f"**Type**: {symbol_type}\n"
        
        if file_info := context.get("file"):
            md += f"**Location**: {file_info.get('path', 'Unknown')}\n"
        
        if desc := context.get("description"):
            md += f"\n## Description\n{desc.get('description', 'No description available')}\n"
        
        # Add other sections...
        return md
    
    def _build_basic_implementation_plan(self, change_request: str, impact_analysis: Dict[str, Any]) -> str:
        """Build basic implementation plan without LLM."""
        md = "# Implementation Plan\n\n"
        md += f"## Change Request\n{change_request}\n\n"
        md += "## Impact Analysis\n"
        
        for entity, impact in impact_analysis.items():
            md += f"\n### {entity}\n"
            if deps := impact.get("dependents"):
                md += f"- **Dependents**: {len(deps)} items\n"
            if files := impact.get("containing_files"):
                md += f"- **Files**: {', '.join(f.get('path', 'Unknown') for f in files)}\n"
        
        return md
    
    def _extract_entities_basic(self, change_request: str) -> List[str]:
        """Basic entity extraction without LLM."""
        # Simple extraction based on common patterns
        import re
        
        # Look for quoted strings, CamelCase, snake_case
        patterns = [
            r'"([^"]+)"',  # Quoted strings
            r'`([^`]+)`',  # Backtick strings
            r'\b([A-Z][a-zA-Z0-9]+)\b',  # CamelCase
            r'\b([a-z_][a-z0-9_]+)\b'  # snake_case
        ]
        
        entities = set()
        for pattern in patterns:
            matches = re.findall(pattern, change_request)
            entities.update(matches)
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        entities = [e for e in entities if e.lower() not in common_words and len(e) > 2]
        
        return list(entities)[:20]  # Limit to 20 entities