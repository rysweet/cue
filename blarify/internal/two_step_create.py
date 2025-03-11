from blarify.code_references.lsp_helper import LspQueryHelper
from blarify.graph.graph_environment import GraphEnvironment
from blarify.prebuilt.graph_builder import GraphBuilder
from blarify.db_managers.neo4j_manager import Neo4jManager
from blarify.db_managers.falkordb_manager import FalkorDBManager
import json


import dotenv
import os

from blarify.project_file_explorer.project_files_iterator import ProjectFilesIterator
from blarify.project_graph_creator import ProjectGraphCreator

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


def build():
    root_path = os.getenv("ROOT_PATH")
    
    lsp_query_helper = LspQueryHelper(root_uri=root_path)

    lsp_query_helper.start()

    project_files_iterator = ProjectFilesIterator(
        root_path=root_path, names_to_skip=NAMES_TO_SKIP
    )

    graph_creator = ProjectGraphCreator(root_path, lsp_query_helper, project_files_iterator)
    
    # Create the hierarchy
    graph = graph_creator.build_hierarchy_only()
    
    relationships = graph.get_relationships_as_objects()
    nodes = graph.get_nodes_as_objects()
    save_to_neo4j(relationships, nodes)
    
    # Create the relationships
    graph_creator.build_graph_relationships()
    relationships = graph.get_relationships_as_objects()
    save_to_neo4j(relationships, [])
    
    lsp_query_helper.shutdown_exit_close()

def save_to_neo4j(relationships, nodes):
    company_id = os.getenv("COMPANY_ID")
    repo_id = os.getenv("REPO_ID")

    graph_manager = Neo4jManager(repo_id=repo_id, entity_id=company_id)

    print(f"Saving graph with {len(nodes)} nodes and {len(relationships)} relationships")
    graph_manager.save_graph(nodes, relationships)
    graph_manager.close()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    dotenv.load_dotenv()
    build()
