"""
Tests for project file exploration functionality.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from blarify.project_file_explorer.file import File
from blarify.project_file_explorer.folder import Folder
from blarify.project_file_explorer.project_files_iterator import ProjectFilesIterator
from blarify.project_file_explorer.project_files_stats import ProjectFileStats


class TestFile(unittest.TestCase):
    """Test File class functionality."""
    
    def test_file_creation(self):
        """Test creating a File instance."""
        file = File(
            path="/test/main.py",
            name="main.py",
            extension=".py",
            level=2
        )
        
        self.assertEqual(file.path, "/test/main.py")
        self.assertEqual(file.name, "main.py")
        self.assertEqual(file.extension, ".py")
        self.assertEqual(file.level, 2)
        
    def test_file_str_representation(self):
        """Test string representation of File."""
        file = File(
            path="/test/src/utils.py",
            name="utils.py",
            extension=".py",
            level=3
        )
        
        str_repr = str(file)
        self.assertIn("utils.py", str_repr)
        self.assertIn("/test/src/utils.py", str_repr)
        
    def test_file_equality(self):
        """Test File equality comparison."""
        file1 = File("/test/main.py", "main.py", ".py", 2)
        file2 = File("/test/main.py", "main.py", ".py", 2)
        file3 = File("/test/other.py", "other.py", ".py", 2)
        
        self.assertEqual(file1, file2)
        self.assertNotEqual(file1, file3)


class TestFolder(unittest.TestCase):
    """Test Folder class functionality."""
    
    def test_folder_creation(self):
        """Test creating a Folder instance."""
        folder = Folder(
            path="/test/src",
            name="src",
            level=1
        )
        
        self.assertEqual(folder.path, "/test/src")
        self.assertEqual(folder.name, "src")
        self.assertEqual(folder.level, 1)
        self.assertEqual(folder.files, [])
        self.assertEqual(folder.folders, [])
        
    def test_add_file_to_folder(self):
        """Test adding files to a folder."""
        folder = Folder("/test/src", "src", 1)
        file1 = File("/test/src/main.py", "main.py", ".py", 2)
        file2 = File("/test/src/utils.py", "utils.py", ".py", 2)
        
        folder.add_file(file1)
        folder.add_file(file2)
        
        self.assertEqual(len(folder.files), 2)
        self.assertIn(file1, folder.files)
        self.assertIn(file2, folder.files)
        
    def test_add_subfolder(self):
        """Test adding subfolders to a folder."""
        parent = Folder("/test", "test", 0)
        child1 = Folder("/test/src", "src", 1)
        child2 = Folder("/test/tests", "tests", 1)
        
        parent.add_folder(child1)
        parent.add_folder(child2)
        
        self.assertEqual(len(parent.folders), 2)
        self.assertIn(child1, parent.folders)
        self.assertIn(child2, parent.folders)
        
    def test_folder_traversal(self):
        """Test traversing folder structure."""
        # Create structure
        root = Folder("/test", "test", 0)
        src = Folder("/test/src", "src", 1)
        utils = Folder("/test/src/utils", "utils", 2)
        
        root.add_folder(src)
        src.add_folder(utils)
        
        # Add files
        main_file = File("/test/main.py", "main.py", ".py", 1)
        util_file = File("/test/src/utils/helper.py", "helper.py", ".py", 3)
        
        root.add_file(main_file)
        utils.add_file(util_file)
        
        # Test traversal
        self.assertEqual(len(root.files), 1)
        self.assertEqual(len(root.folders), 1)
        self.assertEqual(len(src.folders), 1)
        self.assertEqual(len(utils.files), 1)


class TestProjectFilesIterator(unittest.TestCase):
    """Test project files iteration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def create_test_structure(self):
        """Create test file structure."""
        # Create directories
        (Path(self.temp_dir) / "src").mkdir()
        (Path(self.temp_dir) / "tests").mkdir()
        (Path(self.temp_dir) / "__pycache__").mkdir()
        
        # Create files
        files = {
            "README.md": "# Test Project",
            "setup.py": "setup()",
            "src/main.py": "def main(): pass",
            "src/utils.py": "def util(): pass",
            "tests/test_main.py": "def test(): pass",
            "__pycache__/cache.pyc": "compiled",
            ".gitignore": "*.pyc"
        }
        
        for path, content in files.items():
            file_path = Path(self.temp_dir) / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
    def test_iterate_all_files(self):
        """Test iterating through all project files."""
        self.create_test_structure()
        
        iterator = ProjectFilesIterator(
            root_path=self.temp_dir,
            extensions_to_skip=[],
            folders_to_skip=[]
        )
        
        files = list(iterator)
        file_names = [f.name for f in files]
        
        # Should include all files
        self.assertIn("README.md", file_names)
        self.assertIn("setup.py", file_names)
        self.assertIn("main.py", file_names)
        self.assertIn("utils.py", file_names)
        self.assertIn("test_main.py", file_names)
        
    def test_skip_extensions(self):
        """Test skipping files by extension."""
        self.create_test_structure()
        
        iterator = ProjectFilesIterator(
            root_path=self.temp_dir,
            extensions_to_skip=[".pyc", ".pyo"],
            folders_to_skip=[]
        )
        
        files = list(iterator)
        file_names = [f.name for f in files]
        
        # Should not include .pyc files
        self.assertNotIn("cache.pyc", file_names)
        # Should include other files
        self.assertIn("main.py", file_names)
        
    def test_skip_folders(self):
        """Test skipping folders by name."""
        self.create_test_structure()
        
        iterator = ProjectFilesIterator(
            root_path=self.temp_dir,
            extensions_to_skip=[],
            folders_to_skip=["__pycache__", "tests"]
        )
        
        files = list(iterator)
        file_paths = [f.path for f in files]
        
        # Should not include files from skipped folders
        pycache_files = [p for p in file_paths if "__pycache__" in p]
        test_files = [p for p in file_paths if "tests" in p]
        
        self.assertEqual(len(pycache_files), 0)
        self.assertEqual(len(test_files), 0)
        
        # Should include files from other folders
        self.assertTrue(any("main.py" in p for p in file_paths))
        
    def test_file_levels(self):
        """Test that file levels are calculated correctly."""
        self.create_test_structure()
        
        iterator = ProjectFilesIterator(
            root_path=self.temp_dir,
            extensions_to_skip=[],
            folders_to_skip=[]
        )
        
        files = list(iterator)
        
        # Find files at different levels
        readme = next(f for f in files if f.name == "README.md")
        main = next(f for f in files if f.name == "main.py")
        
        # README is at root level (0 or 1 depending on implementation)
        # main.py is one level deeper
        self.assertLess(readme.level, main.level)
        
    def test_empty_directory(self):
        """Test iterating empty directory."""
        iterator = ProjectFilesIterator(
            root_path=self.temp_dir,
            extensions_to_skip=[],
            folders_to_skip=[]
        )
        
        files = list(iterator)
        
        self.assertEqual(len(files), 0)
        
    def test_single_file(self):
        """Test directory with single file."""
        single_file = Path(self.temp_dir) / "only.txt"
        single_file.write_text("only file")
        
        iterator = ProjectFilesIterator(
            root_path=self.temp_dir,
            extensions_to_skip=[],
            folders_to_skip=[]
        )
        
        files = list(iterator)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "only.txt")


class TestProjectFileStats(unittest.TestCase):
    """Test project files statistics."""
    
    def test_stats_initialization(self):
        """Test creating ProjectFileStats instance."""
        stats = ProjectFileStats()
        
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.files_by_extension, {})
        self.assertEqual(stats.total_lines, 0)
        
    def test_add_file_stats(self):
        """Test adding file statistics."""
        stats = ProjectFileStats()
        
        # Add Python file
        stats.add_file(".py", 100)
        stats.add_file(".py", 150)
        
        # Add JavaScript file
        stats.add_file(".js", 200)
        
        self.assertEqual(stats.total_files, 3)
        self.assertEqual(stats.total_lines, 450)
        self.assertEqual(stats.files_by_extension[".py"], 2)
        self.assertEqual(stats.files_by_extension[".js"], 1)
        
    def test_get_summary(self):
        """Test getting statistics summary."""
        stats = ProjectFileStats()
        
        stats.add_file(".py", 100)
        stats.add_file(".py", 150)
        stats.add_file(".js", 200)
        stats.add_file(".md", 50)
        
        summary = stats.get_summary()
        
        self.assertIn("total_files", summary)
        self.assertIn("total_lines", summary)
        self.assertIn("files_by_extension", summary)
        
        self.assertEqual(summary["total_files"], 4)
        self.assertEqual(summary["total_lines"], 500)
        self.assertEqual(summary["files_by_extension"][".py"], 2)
        
    def test_most_common_extension(self):
        """Test finding most common file extension."""
        stats = ProjectFileStats()
        
        stats.add_file(".py", 100)
        stats.add_file(".py", 150)
        stats.add_file(".py", 200)
        stats.add_file(".js", 100)
        stats.add_file(".md", 50)
        
        # .py should be most common with 3 files
        most_common = max(stats.files_by_extension.items(), key=lambda x: x[1])
        
        self.assertEqual(most_common[0], ".py")
        self.assertEqual(most_common[1], 3)


if __name__ == '__main__':
    unittest.main()