import os
from typing import List, Iterator, Optional
from .folder import Folder
from .file import File
from .gitignore_manager import GitignoreManager
import pathspec


class ProjectFilesIterator:
    root_path: str
    paths_to_skip: List[str]
    names_to_skip: List[str]
    extensions_to_skip: List[str]
    max_file_size_mb: int

    def __init__(
        self,
        root_path: str,
        paths_to_skip: Optional[List[str]] = None,
        names_to_skip: Optional[List[str]] = None,
        extensions_to_skip: Optional[List[str]] = None,
        blarignore_path: Optional[str] = None,
        max_file_size_mb: int = 0.8,
        use_gitignore: bool = True,
    ):
        self.paths_to_skip = paths_to_skip or []
        self.root_path = root_path
        self.names_to_skip = names_to_skip or []
        self.extensions_to_skip = extensions_to_skip or []
        self.max_file_size_mb = max_file_size_mb
        self.use_gitignore = use_gitignore
        
        # Initialize gitignore manager if enabled
        self.gitignore_manager: Optional[GitignoreManager] = None
        if self.use_gitignore:
            self.gitignore_manager = GitignoreManager(root_path)
        
        # Initialize blarignore patterns
        self.blarignore_spec: Optional[pathspec.PathSpec] = None
        blarignore_patterns: List[str] = []
        
        # Load .blarignore if path provided
        if blarignore_path:
            self.names_to_skip.extend(self.get_ignore_files(blarignore_path))
            blarignore_patterns.extend(self.get_ignore_files(blarignore_path))
        # Otherwise, try to load .blarignore from root
        elif os.path.exists(os.path.join(root_path, ".blarignore")):
            default_blarignore = os.path.join(root_path, ".blarignore")
            self.names_to_skip.extend(self.get_ignore_files(default_blarignore))
            blarignore_patterns.extend(self.get_ignore_files(default_blarignore))
        
        # Create pathspec for blarignore patterns if any exist
        if blarignore_patterns:
            self.blarignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', blarignore_patterns)

    def get_ignore_files(self, gitignore_path: str) -> List[str]:
        with open(gitignore_path, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]

    def __iter__(self) -> Iterator[Folder]:
        for current_path, dirs, files in os.walk(self.root_path, topdown=True):
            dirs[:] = self._get_filtered_dirs(current_path, dirs)
            level = self.get_path_level_relative_to_root(current_path)
            files = self._get_filtered_files(current_path, files, level + 1)
            folders = self.empty_folders_from_dirs(current_path, dirs, level + 1)
            name = (
                self.get_base_name(current_path)
                if not current_path.endswith("/")
                else self.get_base_name(current_path.rstrip("/"))
            )

            if not self._should_skip(current_path):
                yield Folder(
                    name=name,
                    path=current_path,
                    files=files,
                    folders=folders,
                    level=level,
                )

    def _get_filtered_dirs(self, root: str, dirs: List[str]) -> List[Folder]:
        dirs = [dir for dir in dirs if not self._should_skip_directory(os.path.join(root, dir))]
        return dirs

    def get_path_level_relative_to_root(self, path: str) -> int:
        level = path.count(os.sep) - self.root_path.count(os.sep)
        return level

    def _get_filtered_files(self, root: str, files: List[str], level: int) -> List[File]:
        files = [file for file in files if not self._should_skip(os.path.join(root, file))]

        return [File(name=file, root_path=root, level=level) for file in files]

    def empty_folders_from_dirs(self, root: str, dirs: List[str], level: int) -> List[Folder]:
        return [
            Folder(
                name=dir,
                path=os.path.join(root, dir),
                files=[],
                folders=[],
                level=level,
            )
            for dir in dirs
        ]

    def _should_skip_directory(self, path: str) -> bool:
        """
        Check if a directory should be skipped during traversal.
        
        This is different from _should_skip for files because we need to
        consider whether the directory might contain files that should NOT
        be ignored (due to negation patterns).
        """
        # For gitignore, we need to check if the directory itself is ignored
        # but we can't skip it if it might contain negated patterns
        if self.use_gitignore and self.gitignore_manager:
            # For now, let's not skip directories based on gitignore
            # The pathspec library should handle this correctly when checking individual files
            pass
        
        # Check blarignore patterns - similar consideration
        if self.blarignore_spec:
            # Don't skip directories based on blarignore patterns alone
            pass
        
        # Apply other skip rules (these are safe to apply to directories)
        is_basename_in_names_to_skip = os.path.basename(path) in self.names_to_skip
        is_path_in_paths_to_skip = any(path.startswith(path_to_skip) for path_to_skip in self.paths_to_skip)
        is_extension_to_skip = any(path.endswith(extension) for extension in self.extensions_to_skip)
        
        return is_basename_in_names_to_skip or is_path_in_paths_to_skip or is_extension_to_skip
    
    def _should_skip(self, path: str) -> bool:
        # First check gitignore patterns if enabled
        if self.use_gitignore and self.gitignore_manager:
            if self.gitignore_manager.should_ignore(path):
                return True
        
        # Check blarignore patterns
        if self.blarignore_spec:
            rel_path = os.path.relpath(path, self.root_path)
            if self.blarignore_spec.match_file(rel_path):
                return True
        
        # Then check other skip patterns
        is_basename_in_names_to_skip = os.path.basename(path) in self.names_to_skip

        is_path_in_paths_to_skip = any(path.startswith(path_to_skip) for path_to_skip in self.paths_to_skip)

        # Only check file size if it's a file (not a directory)
        is_file_size_too_big = False
        if os.path.isfile(path):
            is_file_size_too_big = os.path.getsize(path) > self._mb_to_bytes(self.max_file_size_mb)

        is_extension_to_skip = any(path.endswith(extension) for extension in self.extensions_to_skip)

        return is_basename_in_names_to_skip or is_path_in_paths_to_skip or is_file_size_too_big or is_extension_to_skip

    def _mb_to_bytes(self, mb: int) -> int:
        return 1024 * 1024 * mb

    def get_base_name(self, current_path: str) -> str:
        return os.path.basename(current_path)
