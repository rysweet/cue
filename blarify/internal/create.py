from typing import List, Dict, Any, Tuple
from blarify.graph.graph_environment import GraphEnvironment
from blarify.prebuilt.graph_builder import GraphBuilder
from blarify.db_managers.neo4j_manager import Neo4jManager
from blarify.db_managers.falkordb_manager import FalkorDBManager
import json
import logging

import dotenv
import os

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


def build() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    logging.basicConfig(level=logging.DEBUG)
    root_path = os.getenv("ROOT_PATH")
    print(f"Root path: {root_path}")
    environment = os.getenv("ENVIRONMENT")
    diff_identifier = os.getenv("DIFF_IDENTIFIER")
    
    # Provide defaults for required environment variables
    if root_path is None:
        raise ValueError("ROOT_PATH environment variable is required")
    if environment is None:
        raise ValueError("ENVIRONMENT environment variable is required")
    if diff_identifier is None:
        raise ValueError("DIFF_IDENTIFIER environment variable is required")

    graph_environment = GraphEnvironment(environment=environment, diff_identifier=diff_identifier, root_path=root_path)

    graph_builder = GraphBuilder(
        root_path=root_path, names_to_skip=NAMES_TO_SKIP, graph_environment=graph_environment, only_hierarchy=False
    )

    graph = graph_builder.build()

    relationships = graph.get_relationships_as_objects()
    nodes = graph.get_nodes_as_objects()
    
    return relationships, nodes

def save_to_neo4j(relationships: List[Dict[str, Any]], nodes: List[Dict[str, Any]]) -> None:
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
    relationships, nodes = build()
    save_to_neo4j(relationships, nodes)
