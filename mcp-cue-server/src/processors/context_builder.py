"""Context builder for organizing graph data into consumable formats."""

import logging
from typing import Dict, Any, List
from collections import defaultdict

from ..config import Config

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds structured context from graph traversal results."""
    
    def __init__(self):
        """Initialize the context builder."""
        self.max_context_length = Config.MAX_CONTEXT_LENGTH
        self.max_nodes_per_type = Config.MAX_NODES_PER_TYPE
    
    def build_files_context(self, file_contexts: List[Dict[str, Any]]) -> str:
        """Build combined context for multiple files."""
        if not file_contexts:
            return "# No Files Found\n\nNo files matching the specified paths were found in the graph."
        
        sections = []
        
        # Group files by directory for better organization
        files_by_dir = defaultdict(list)
        for context in file_contexts:
            if file_info := context.get("file"):
                path = file_info.get("path", "unknown")
                dir_path = "/".join(path.split("/")[:-1]) or "/"
                files_by_dir[dir_path].append(context)
        
        # Build context for each directory
        for dir_path, contexts in sorted(files_by_dir.items()):
            if dir_path != "/":
                sections.append(f"## Directory: {dir_path}\n")
            
            for context in contexts:
                file_section = self._build_single_file_section(context)
                sections.append(file_section)
        
        full_context = "\n".join(sections)
        
        # Truncate if too long
        if len(full_context) > self.max_context_length:
            full_context = self._truncate_context(full_context)
        
        return full_context
    
    def build_symbol_context(self, symbol_context: Dict[str, Any], related_symbols: List[Dict[str, Any]] = None) -> str:
        """Build context for a symbol with optional related symbols."""
        if not symbol_context or not symbol_context.get("symbol"):
            return "# Symbol Not Found\n\nThe requested symbol could not be found in the graph."
        
        sections = []
        
        # Main symbol context
        main_section = self._build_symbol_section(symbol_context, is_main=True)
        sections.append(main_section)
        
        # Related symbols
        if related_symbols:
            sections.append("\n## Related Symbols\n")
            for related in related_symbols[:5]:  # Limit to 5 related symbols
                related_section = self._build_symbol_section(related, is_main=False)
                sections.append(related_section)
        
        full_context = "\n".join(sections)
        
        # Truncate if too long
        if len(full_context) > self.max_context_length:
            full_context = self._truncate_context(full_context)
        
        return full_context
    
    def build_change_plan_context(self, change_request: str, impact_analysis: Dict[str, Any], patterns: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build context for change planning."""
        context = {
            "change_request": change_request,
            "impact_summary": self._summarize_impact(impact_analysis),
            "affected_files": self._extract_affected_files(impact_analysis),
            "affected_entities": list(impact_analysis.keys()),
            "test_files": self._extract_test_files(impact_analysis),
            "documentation_files": self._extract_documentation_files(impact_analysis),
            "patterns": patterns
        }
        
        return context
    
    def _build_single_file_section(self, context: Dict[str, Any]) -> str:
        """Build markdown section for a single file."""
        file_info = context.get("file", {})
        path = file_info.get("path", "Unknown")
        name = path.split("/")[-1]
        
        section = f"### File: {name}\n"
        section += f"**Path**: `{path}`\n"
        
        # Add description if available
        if desc := context.get("description"):
            section += f"\n**Description**: {desc.get('description', 'No description available')}\n"
        
        # Add contents
        if contents := context.get("contents"):
            section += "\n**Contains**:\n"
            grouped = self._group_by_type(contents)
            for node_type, nodes in grouped.items():
                if nodes:
                    section += f"- {node_type}s: {', '.join(n.get('name', 'Unknown') for n in nodes[:10])}\n"
                    if len(nodes) > 10:
                        section += f"  - ... and {len(nodes) - 10} more\n"
        
        # Add dependencies
        if imports := context.get("imports"):
            section += "\n**Imports**:\n"
            for imp in imports[:10]:
                imp_name = imp.get("name", imp.get("path", "Unknown"))
                section += f"- {imp_name}\n"
            if len(imports) > 10:
                section += f"- ... and {len(imports) - 10} more\n"
        
        # Add usage
        if importers := context.get("importers"):
            section += "\n**Imported by**:\n"
            for imp in importers[:5]:
                section += f"- {imp.get('path', 'Unknown')}\n"
            if len(importers) > 5:
                section += f"- ... and {len(importers) - 5} more\n"
        
        section += "\n"
        return section
    
    def _build_symbol_section(self, context: Dict[str, Any], is_main: bool = True) -> str:
        """Build markdown section for a symbol."""
        symbol = context.get("symbol", {})
        name = symbol.get("name", "Unknown")
        labels = symbol.get("_labels", ["Unknown"])
        
        if is_main:
            section = f"# Symbol: {name}\n\n"
        else:
            section = f"### {name}\n"
        
        section += f"**Type**: {', '.join(labels)}\n"
        
        # Add location
        if file_info := context.get("file"):
            section += f"**Location**: `{file_info.get('path', 'Unknown')}`\n"
        
        # Add description
        if desc := context.get("description"):
            section += f"\n**Description**: {desc.get('description', 'No description available')}\n"
        
        # Add inheritance
        if parents := context.get("parents"):
            section += f"\n**Inherits from**: {', '.join(p.get('name', 'Unknown') for p in parents)}\n"
        
        if children := context.get("children"):
            section += f"**Inherited by**: {', '.join(c.get('name', 'Unknown') for c in children[:5])}"
            if len(children) > 5:
                section += f" ... and {len(children) - 5} more"
            section += "\n"
        
        # Add methods for classes
        if methods := context.get("methods"):
            section += "\n**Methods**:\n"
            for method in methods[:10]:
                section += f"- {method.get('name', 'Unknown')}\n"
            if len(methods) > 10:
                section += f"- ... and {len(methods) - 10} more\n"
        
        # Add usage
        if callers := context.get("callers"):
            section += f"\n**Called by**: {len(callers)} locations\n"
            for caller in callers[:5]:
                caller_name = caller.get("name", "Unknown")
                if caller_file := caller.get("path"):
                    section += f"- {caller_name} in `{caller_file}`\n"
                else:
                    section += f"- {caller_name}\n"
        
        section += "\n"
        return section
    
    def _group_by_type(self, nodes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group nodes by their primary type."""
        grouped = defaultdict(list)
        for node in nodes:
            labels = node.get("_labels", ["Unknown"])
            primary_type = labels[0] if labels else "Unknown"
            grouped[primary_type].append(node)
        return dict(grouped)
    
    def _summarize_impact(self, impact_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the impact analysis."""
        total_dependents = 0
        total_files = set()
        total_tests = set()
        
        for entity, impact in impact_analysis.items():
            total_dependents += len(impact.get("dependents", []))
            for f in impact.get("containing_files", []):
                total_files.add(f.get("path", ""))
            for t in impact.get("test_files", []):
                total_tests.add(t.get("path", ""))
        
        return {
            "entities_affected": len(impact_analysis),
            "total_dependents": total_dependents,
            "files_affected": len(total_files),
            "test_files_affected": len(total_tests)
        }
    
    def _extract_affected_files(self, impact_analysis: Dict[str, Any]) -> List[str]:
        """Extract all affected files from impact analysis."""
        files = set()
        for entity, impact in impact_analysis.items():
            for f in impact.get("containing_files", []):
                files.add(f.get("path", ""))
        return sorted(list(files))
    
    def _extract_test_files(self, impact_analysis: Dict[str, Any]) -> List[str]:
        """Extract all test files from impact analysis."""
        files = set()
        for entity, impact in impact_analysis.items():
            for f in impact.get("test_files", []):
                files.add(f.get("path", ""))
        return sorted(list(files))
    
    def _extract_documentation_files(self, impact_analysis: Dict[str, Any]) -> List[str]:
        """Extract all documentation files from impact analysis."""
        files = set()
        for entity, impact in impact_analysis.items():
            for d in impact.get("documentation", []):
                files.add(d.get("path", ""))
        return sorted(list(files))
    
    def _truncate_context(self, context: str) -> str:
        """Truncate context to maximum length."""
        if len(context) <= self.max_context_length:
            return context
        
        # Truncate and add message
        truncated = context[:self.max_context_length - 100]
        truncated += "\n\n... (context truncated due to length limit)"
        return truncated