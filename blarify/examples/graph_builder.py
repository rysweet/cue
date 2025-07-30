from blarify.prebuilt.graph_builder import GraphBuilder
from blarify.db_managers.neo4j_manager import Neo4jManager
from blarify.db_managers.falkordb_manager import FalkorDBManager

import dotenv
import os


def build(root_path: str = None, enable_llm_descriptions: bool = None):
    graph_builder = GraphBuilder(
        root_path=root_path,
        extensions_to_skip=[".json"],
        names_to_skip=["__pycache__", ".venv", ".git", ".env", "node_modules"],
        enable_llm_descriptions=enable_llm_descriptions
    )
    graph = graph_builder.build()

    relationships = graph.get_relationships_as_objects()
    nodes = graph.get_nodes_as_objects()
    
    # Log statistics about LLM descriptions if enabled
    if enable_llm_descriptions:
        description_nodes = [n for n in nodes if n.get('type') == 'DESCRIPTION']
        print(f"Generated {len(description_nodes)} LLM descriptions")

    save_to_neo4j(relationships, nodes)

def save_to_neo4j(relationships, nodes):
    graph_manager = Neo4jManager(repo_id="repo", entity_id="organization")

    print(f"Saving graph with {len(nodes)} nodes and {len(relationships)} relationships")
    graph_manager.save_graph(nodes, relationships)
    graph_manager.close()


def save_to_falkordb(relationships, nodes):
    graph_manager = FalkorDBManager(repo_id="repo", entity_id="organization")

    print(f"Saving graph with {len(nodes)} nodes and {len(relationships)} relationships")
    graph_manager.save_graph(nodes, relationships)
    graph_manager.close()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    dotenv.load_dotenv()
    root_path = os.getenv("ROOT_PATH")
    enable_llm = os.getenv("ENABLE_LLM_DESCRIPTIONS", "false").lower() == "true"
    
    build(root_path=root_path, enable_llm_descriptions=enable_llm)
