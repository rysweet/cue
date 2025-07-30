"""MCP tools for context retrieval."""

import logging
from typing import List, Dict, Any, Optional
from neo4j import Driver

from ..processors.graph_traversal import GraphTraversal
from ..processors.context_builder import ContextBuilder
from ..processors.llm_processor import LLMProcessor

logger = logging.getLogger(__name__)


class ContextTools:
    """MCP tools for retrieving context from the graph."""
    
    def __init__(self, driver: Driver):
        """Initialize context tools."""
        self.driver = driver
        self.graph_traversal = GraphTraversal(driver)
        self.context_builder = ContextBuilder()
        self.llm_processor = LLMProcessor()
    
    async def get_context_for_files(self, file_paths: List[str]) -> str:
        """
        Retrieve comprehensive context for a list of files.
        
        Args:
            file_paths: List of file paths to get context for
            
        Returns:
            Markdown-formatted context for the files
        """
        logger.info(f"Getting context for files: {file_paths}")
        
        try:
            # Find matching files in the graph
            file_nodes = self.graph_traversal.find_files(file_paths)
            
            if not file_nodes:
                return f"# Files Not Found\n\nNo files matching these paths were found:\n" + \
                       "\n".join(f"- {path}" for path in file_paths)
            
            # Get context for each file
            file_contexts = []
            for file_node in file_nodes:
                path = file_node.get("path", "")
                context = self.graph_traversal.get_file_context(path)
                if context:
                    file_contexts.append(context)
            
            # Build structured context
            if self.llm_processor.enabled:
                # Use LLM to organize the contexts
                combined_context = []
                for context in file_contexts:
                    organized = self.llm_processor.organize_file_context(context)
                    combined_context.append(organized)
                
                result = "# Context for Files\n\n" + "\n---\n\n".join(combined_context)
            else:
                # Use context builder without LLM
                result = self.context_builder.build_files_context(file_contexts)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting file context: {e}")
            return f"# Error\n\nFailed to retrieve context for files: {str(e)}"
    
    async def get_context_for_symbol(self, symbol_name: str, symbol_type: Optional[str] = None) -> str:
        """
        Retrieve context for a specific symbol.
        
        Args:
            symbol_name: Name of the symbol to find
            symbol_type: Optional type hint (class, function, etc.)
            
        Returns:
            Markdown-formatted context for the symbol
        """
        logger.info(f"Getting context for symbol: {symbol_name} (type: {symbol_type})")
        
        try:
            # Find matching symbols
            symbols = self.graph_traversal.find_symbol(symbol_name, symbol_type)
            
            if not symbols:
                return f"# Symbol Not Found\n\nNo symbol named '{symbol_name}' was found in the graph."
            
            # Get the best match (exact match preferred)
            best_match = symbols[0]
            symbol_id = best_match.get("_id")
            
            # Get comprehensive context
            context = self.graph_traversal.get_symbol_context(symbol_id)
            
            if not context:
                return f"# Symbol Found but No Context\n\nSymbol '{symbol_name}' exists but has no associated context."
            
            # Get context for related symbols if any
            related_contexts = []
            if len(symbols) > 1:
                for symbol in symbols[1:4]:  # Get up to 3 more related symbols
                    related_id = symbol.get("_id")
                    related_context = self.graph_traversal.get_symbol_context(related_id)
                    if related_context:
                        related_contexts.append(related_context)
            
            # Build structured context
            if self.llm_processor.enabled:
                # Use LLM to organize the context
                main_context = self.llm_processor.organize_symbol_context(context)
                
                if related_contexts:
                    related_parts = []
                    for rc in related_contexts:
                        related_parts.append(self.llm_processor.organize_symbol_context(rc))
                    
                    result = main_context + "\n\n---\n\n## Other Matches\n\n" + "\n---\n\n".join(related_parts)
                else:
                    result = main_context
            else:
                # Use context builder without LLM
                result = self.context_builder.build_symbol_context(context, related_contexts)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting symbol context: {e}")
            return f"# Error\n\nFailed to retrieve context for symbol '{symbol_name}': {str(e)}"
    
    def _format_file_list(self, files: List[Dict[str, Any]]) -> str:
        """Format a list of files for display."""
        if not files:
            return "None"
        
        file_paths = [f.get("path", "Unknown") for f in files[:10]]
        result = "\n".join(f"- `{path}`" for path in file_paths)
        
        if len(files) > 10:
            result += f"\n- ... and {len(files) - 10} more files"
        
        return result