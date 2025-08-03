import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DocumentationParser:
    """
    Main orchestrator for parsing documentation files and creating documentation nodes.
    
    This class identifies documentation files in a project, extracts concepts and entities
    using LLM, and prepares the data for graph node creation.
    """
    
    DEFAULT_DOC_EXTENSIONS = ['.md', '.markdown', '.rst', '.txt', '.adoc']
    DEFAULT_DOC_NAMES = ['README*', 'CHANGELOG*', 'LICENSE*', 'CONTRIBUTING*', 'AUTHORS*']
    DEFAULT_DOC_DIRS = ['docs', 'documentation', 'doc']
    
    def __init__(
        self,
        root_path: str,
        documentation_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        Initialize the documentation parser.
        
        Args:
            root_path: Root directory of the project
            documentation_patterns: Custom patterns for documentation files
            exclude_patterns: Patterns to exclude from documentation parsing
        """
        self.root_path = os.path.abspath(root_path)
        self.documentation_patterns = documentation_patterns or self.DEFAULT_DOC_EXTENSIONS
        self.exclude_patterns = exclude_patterns or []
        
    def find_documentation_files(self) -> List[str]:
        """
        Find all documentation files in the project.
        
        Returns:
            List of absolute paths to documentation files
        """
        doc_files: List[str] = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden directories and common non-doc directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.venv']]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if file matches documentation patterns
                if self._is_documentation_file(file, file_path):
                    doc_files.append(file_path)
                    
        logger.info(f"Found {len(doc_files)} documentation files")
        return doc_files
    
    def _is_documentation_file(self, filename: str, filepath: str) -> bool:
        """
        Check if a file is a documentation file based on patterns.
        
        Args:
            filename: Name of the file
            filepath: Full path to the file
            
        Returns:
            True if the file is a documentation file
        """
        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if pattern in filepath:
                return False
        
        # Check documentation patterns (can be extensions or glob patterns)
        for pattern in self.documentation_patterns:
            # If pattern starts with *, treat as extension
            if pattern.startswith('*'):
                if filename.lower().endswith(pattern[1:]):
                    return True
            # Otherwise check if filename matches the pattern
            elif pattern.lower() in filename.lower():
                return True
        
        # Check special documentation filenames
        filename_upper = filename.upper()
        for doc_name_pattern in self.DEFAULT_DOC_NAMES:
            # Remove wildcard for comparison
            base_pattern = doc_name_pattern.replace('*', '')
            if filename_upper.startswith(base_pattern):
                return True
        
        return False
    
    def parse_documentation_files(self) -> Dict[str, Any]:
        """
        Parse all documentation files and extract information.
        
        Returns:
            Dictionary containing parsed documentation data
        """
        doc_files = self.find_documentation_files()
        result: Dict[str, Any] = {
            "documentation_files": [],
            "concepts": [],
            "entities": [],
            "relationships": [],
            "code_references": []
        }
        
        for doc_file in doc_files:
            try:
                logger.debug(f"Parsing documentation file: {doc_file}")
                
                # Read file content
                content = self._read_file(doc_file)
                
                # Create documentation file entry
                doc_entry = {
                    "path": doc_file,
                    "name": os.path.basename(doc_file),
                    "relative_path": os.path.relpath(doc_file, self.root_path),
                    "content": content
                }
                result["documentation_files"].append(doc_entry)
                
            except Exception as e:
                logger.error(f"Error parsing documentation file {doc_file}: {e}")
                continue
        
        return result
    
    def _read_file(self, filepath: str) -> str:
        """
        Read content from a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            File content as string
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()