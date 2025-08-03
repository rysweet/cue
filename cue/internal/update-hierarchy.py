from cue.project_file_explorer import ProjectFilesIterator
from cue.project_graph_updater import ProjectGraphUpdater, UpdatedFile
from cue.db_managers.neo4j_manager import Neo4jManager
from cue.code_references import LspQueryHelper
from cue.graph.graph_environment import GraphEnvironment
from typing import List, Optional

import dotenv
import os

import logging

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

NAMES_TO_SKIP = [
    ".env",
    ".git",
    ".venv",
    ".ruff_cache",
    "__pycache__",
    "poetry.lock",
    "yarn.lock",
    "Pipfile.lock",
    "Gemfile.lock",
    "Guardfile",
    "422.html",
    "package-lock.json",
    "migrations",
    "node_modules",
    "public",
    "build",
    "dist",
    "static",
    "versions",
]

def update(updated_files: List[UpdatedFile], root_uri: str, cueignore_path: Optional[str] = None):
    lsp_query_helper = LspQueryHelper(root_uri=root_uri)
    lsp_query_helper.start()

    project_files_iterator = ProjectFilesIterator(
        root_path=root_uri,
        cueignore_path=cueignore_path,
        names_to_skip=NAMES_TO_SKIP,
    )

    repoId = "test"
    entity_id = "test"
    graph_manager = Neo4jManager(repoId, entity_id)

    delete_updated_files_from_neo4j(updated_files, graph_manager)

    graph_diff_creator = ProjectGraphUpdater(
        updated_files=updated_files,
        root_path=root_uri,
        lsp_query_helper=lsp_query_helper,
        project_files_iterator=project_files_iterator,
        graph_environment=GraphEnvironment("dev", "MAIN", root_uri),
    )

    graph = graph_diff_creator.build_hierarchy_only()

    relationships = graph.get_relationships_as_objects()
    nodes = graph.get_nodes_as_objects()

    print(f"Saving graph with {len(nodes)} nodes and {len(relationships)} relationships")
    graph_manager.save_graph(nodes, relationships)
    graph_manager.close()
    lsp_query_helper.shutdown_exit_close()


def delete_updated_files_from_neo4j(updated_files: List[UpdatedFile], db_manager: Neo4jManager):
    for updated_file in updated_files:
        db_manager.detatch_delete_nodes_with_path(updated_file.path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dotenv.load_dotenv()
    root_path = os.getenv("ROOT_PATH")
    cueignore_path = os.getenv("BLARIGNORE_PATH")
    paths_to_update_str = os.getenv("PATHS_TO_UPDATE")
    
    # Validate required environment variables
    if root_path is None:
        raise ValueError("ROOT_PATH environment variable is required")
    if paths_to_update_str is None:
        raise ValueError("PATHS_TO_UPDATE environment variable is required")
        
    paths_to_update = paths_to_update_str.split(";")



    print("Updating")
    update(
        updated_files=[
            UpdatedFile(
                path=path,
            )
            for path in paths_to_update
        ],
        root_uri=root_path,
    )