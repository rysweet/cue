from blarify.graph.graph_environment import GraphEnvironment
from blarify.prebuilt.graph_builder import GraphBuilder
from blarify.db_managers.neo4j_manager import Neo4jManager
from blarify.db_managers.falkordb_manager import FalkorDBManager
import json


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
    logging.basicConfig(level=logging.DEBUG)
    root_path = os.getenv("ROOT_PATH")
    environment = os.getenv("ENVIRONMENT")
    diff_identifier = os.getenv("DIFF_IDENTIFIER")

    graph_environment = GraphEnvironment(environment=environment, diff_identifier=diff_identifier, root_path=root_path)

    graph_builder = GraphBuilder(
        root_path=root_path, names_to_skip=NAMES_TO_SKIP, graph_environment=graph_environment
    )

    graph = graph_builder.build()

    relationships = graph.get_relationships_as_objects()
    nodes = graph.get_nodes_as_objects()

    dump_to_json(relationships, "relationships.json")
    dump_to_json(nodes, "nodes.json")

def dump_to_json(to_dump, path):
    with open(path, "w") as f:
        json.dump(to_dump, f)

def load_json_files():
    with open("relationships.json", "r") as f:
        relationships = json.load(f)

    with open("nodes.json", "r") as f:
        nodes = json.load(f)

    return relationships, nodes

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
    relationship, nodes = load_json_files()
    save_to_neo4j(relationship, nodes)
