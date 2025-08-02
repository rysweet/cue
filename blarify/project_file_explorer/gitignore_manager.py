import os
from typing import List, Dict
import pathspec
import logging

logger = logging.getLogger(__name__)


class GitignoreManager:
    """
    Manages gitignore patterns from .gitignore files in a project.
    
    This class finds and parses all .gitignore files in a project directory,
    caches the compiled patterns for performance, and provides methods to
    check if paths should be ignored according to gitignore rules.
    """
    
    def __init__(self, root_path: str):
        """
        Initialize the GitignoreManager with a root directory.
        
        Args:
            root_path: The root directory to search for .gitignore files
        """
        self.root_path = os.path.abspath(root_path)
        self._pattern_cache: Dict[str, pathspec.PathSpec] = {}
        self._gitignore_files: List[str] = []
        self._load_gitignore_patterns()
    
    def _load_gitignore_patterns(self) -> None:
        """Find and load all .gitignore files in the project."""
        # Find all .gitignore files
        for dirpath, _, filenames in os.walk(self.root_path):
            if '.gitignore' in filenames:
                gitignore_path = os.path.join(dirpath, '.gitignore')
                self._gitignore_files.append(gitignore_path)
                self._parse_gitignore_file(gitignore_path)
    
    def _parse_gitignore_file(self, gitignore_path: str) -> None:
        """
        Parse a single .gitignore file and cache its patterns.
        
        Args:
            gitignore_path: Path to the .gitignore file
        """
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                # Read lines and filter out comments and empty lines
                lines = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                
                if lines:
                    # Create PathSpec from the patterns
                    spec = pathspec.PathSpec.from_lines('gitwildmatch', lines)
                    # Store relative to the directory containing the .gitignore
                    gitignore_dir = os.path.dirname(gitignore_path)
                    self._pattern_cache[gitignore_dir] = spec
                    logger.debug(f"Loaded {len(lines)} patterns from {gitignore_path}")
        except Exception as e:
            logger.warning(f"Failed to parse gitignore file {gitignore_path}: {e}")
    
    def should_ignore(self, path: str) -> bool:
        """
        Check if a path should be ignored according to gitignore patterns.
        
        This method checks the path against all loaded gitignore patterns,
        respecting the directory hierarchy (patterns in subdirectories only
        apply to files within those subdirectories).
        
        Args:
            path: The path to check (can be absolute or relative to root)
        
        Returns:
            True if the path should be ignored, False otherwise
        """
        # Make path absolute for consistent comparison
        if not os.path.isabs(path):
            path = os.path.join(self.root_path, path)
        
        # Check against each gitignore file's patterns
        for gitignore_dir, spec in self._pattern_cache.items():
            # Only apply patterns if the path is within the gitignore's directory
            if path.startswith(gitignore_dir + os.sep) or path == gitignore_dir:
                # Get the relative path from the gitignore directory
                rel_path = os.path.relpath(path, gitignore_dir)
                
                # Check if the path matches any pattern
                if spec.match_file(rel_path):
                    logger.debug(f"Path {path} ignored by patterns in {gitignore_dir}/.gitignore")
                    return True
        
        return False
    
    def get_gitignore_files(self) -> List[str]:
        """
        Get a list of all .gitignore files found in the project.
        
        Returns:
            List of paths to .gitignore files
        """
        return self._gitignore_files.copy()
    
    def get_all_patterns(self) -> List[str]:
        """
        Get all loaded gitignore patterns for debugging purposes.
        
        Returns:
            List of all patterns from all .gitignore files
        """
        all_patterns = []
        for gitignore_path in self._gitignore_files:
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            all_patterns.append(line)
            except Exception:
                pass
        return all_patterns