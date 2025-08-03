from cue.code_references.lsp_helper import LspQueryHelper
from cue.graph.graph import Graph
from cue.graph.graph_environment import GraphEnvironment
from cue.project_file_explorer.project_files_iterator import ProjectFilesIterator
from cue.project_graph_creator import ProjectGraphCreator
from typing import Optional, List


class GraphBuilder:
    def __init__(
        self,
        root_path: str,
        extensions_to_skip: Optional[List[str]] = None,
        names_to_skip: Optional[List[str]] = None,
        only_hierarchy: bool = False,
        graph_environment: Optional[GraphEnvironment] = None,
        enable_llm_descriptions: Optional[bool] = None,
        enable_filesystem_nodes: Optional[bool] = None,
        use_gitignore: bool = True,
        cueignore_path: Optional[str] = None,
        enable_documentation_nodes: Optional[bool] = None,
        documentation_patterns: Optional[List[str]] = None,
        max_llm_calls_per_doc: int = 5,
    ):
        """
        A class responsible for constructing a graph representation of a project's codebase.

        Args:
            root_path: Root directory path of the project to analyze
            extensions_to_skip: File extensions to exclude from analysis (e.g., ['.md', '.txt'])
            names_to_skip: Filenames/directory names to exclude from analysis (e.g., ['venv', 'tests'])
            only_hierarchy: If True, only build the code hierarchy without references
            graph_environment: Custom graph environment configuration
            enable_llm_descriptions: If True, generate LLM descriptions for code nodes
            enable_filesystem_nodes: If True, generate filesystem nodes and relationships
            use_gitignore: If True, automatically exclude files matching .gitignore patterns (default: True)
            cueignore_path: Path to .cueignore file (if not provided, looks for .cueignore in root)
            enable_documentation_nodes: If True, parse documentation and create knowledge graph
            documentation_patterns: Custom patterns for documentation files (e.g., ['*.md', '*.rst'])
            max_llm_calls_per_doc: Maximum LLM calls per documentation file (default: 5)

        Example:
            builder = GraphBuilder(
                    "/path/to/project",
                    extensions_to_skip=[".json"],
                    names_to_skip=["__pycache__"]
                )
            project_graph = builder.build()

        """

        self.graph_environment = graph_environment or GraphEnvironment("cue", "repo", root_path)

        self.root_path = root_path
        self.extensions_to_skip = extensions_to_skip or []
        self.names_to_skip = names_to_skip or []

        self.only_hierarchy = only_hierarchy
        self.enable_llm_descriptions = enable_llm_descriptions
        self.enable_filesystem_nodes = enable_filesystem_nodes
        self.use_gitignore = use_gitignore
        self.cueignore_path = cueignore_path
        self.enable_documentation_nodes = enable_documentation_nodes
        self.documentation_patterns = documentation_patterns
        self.max_llm_calls_per_doc = max_llm_calls_per_doc

    def build(self) -> Graph:
        lsp_query_helper = self._get_started_lsp_query_helper()
        project_files_iterator = self._get_project_files_iterator()

        graph_creator = ProjectGraphCreator(self.root_path, lsp_query_helper, project_files_iterator, 
                                            graph_environment=self.graph_environment,
                                            enable_llm_descriptions=self.enable_llm_descriptions,
                                            enable_filesystem_nodes=self.enable_filesystem_nodes,
                                            enable_documentation_nodes=self.enable_documentation_nodes,
                                            documentation_patterns=self.documentation_patterns,
                                            max_llm_calls_per_doc=self.max_llm_calls_per_doc)

        if self.only_hierarchy:
            graph = graph_creator.build_hierarchy_only()
        else:
            graph = graph_creator.build()

        lsp_query_helper.shutdown_exit_close()

        return graph

    def _get_project_files_iterator(self):
        return ProjectFilesIterator(
            root_path=self.root_path, 
            extensions_to_skip=self.extensions_to_skip, 
            names_to_skip=self.names_to_skip,
            use_gitignore=self.use_gitignore,
            cueignore_path=self.cueignore_path
        )

    def _get_started_lsp_query_helper(self):
        lsp_query_helper = LspQueryHelper(root_uri=self.root_path)
        lsp_query_helper.start()
        return lsp_query_helper
