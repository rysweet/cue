from blarify.prebuilt.graph_builder import GraphBuilder
from blarify.db_managers.neo4j_manager import Neo4jManager
from blarify.db_managers.falkordb_manager import FalkorDBManager

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


def build():
    root_path = os.getenv("ROOT_PATH")
    company_id = os.getenv("COMPANY_ID")
    repo_id = os.getenv("REPO_ID")

    graph_builder = GraphBuilder(
        root_path=root_path, names_to_skip=NAMES_TO_SKIP, entity_id=company_id, repo_id=repo_id
    )

    graph = graph_builder.build()

    relationships = graph.get_relationships_as_objects()
    nodes = graph.get_nodes_as_objects()

    dump_to_json(relationships, "relationships.json")
    dump_to_json(nodes, "nodes.json")

def dump_to_json(to_dump, path):
    import json

    with open(path, "w") as f:
        json.dump(to_dump, f)

def save_to_neo4j(relationships, nodes):
    graph_manager = Neo4jManager(repo_id="repo", entity_id="organization")

    print(f"Saving graph with {len(nodes)} nodes and {len(relationships)} relationships")
    graph_manager.save_graph(nodes, relationships)
    graph_manager.close()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    dotenv.load_dotenv()
    build(root_path=root_path)
