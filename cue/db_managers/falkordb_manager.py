import os
from typing import Any, List, Optional
import logging

from dotenv import load_dotenv
from falkordb import FalkorDB

from .db_manager import AbstractDbManager

logger = logging.getLogger(__name__)

load_dotenv()


class FalkorDBManager(AbstractDbManager):
    entity_id: str
    repo_id: str
    db: FalkorDB

    def __init__(
        self,
        repo_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        host = uri or os.getenv("FALKORDB_URI", "localhost")
        port = int(os.getenv("FALKORDB_PORT", "6379"))
        username = user or os.getenv("FALKORDB_USERNAME", "")
        pwd = password or os.getenv("FALKORDB_PASSWORD", "")

        self.db = FalkorDB(host=host, port=port, username=username, password=pwd)

        self.repo_id = repo_id if repo_id is not None else "default_repo"
        self.entity_id = entity_id if entity_id is not None else "default_user"

    def close(self) -> None:
        pass

    def save_graph(self, nodes: List[Any], edges: List[Any]) -> None:
        self.create_nodes(nodes)
        self.create_edges(edges)

    def create_nodes(self, nodeList: List[Any]) -> None:
        graph = self.db.select_graph(self.repo_id)
        cypher_query = """
        UNWIND $nodes AS node
        CREATE (n)
        SET n = node.attributes
        WITH n AS created_node, node.extra_labels AS labels
        UNWIND labels AS label
        SET created_node:label
        RETURN created_node
        """
        graph.query(
            cypher_query,
            params={"nodes": nodeList},
        )

    def create_edges(self, edgesList: List[Any]) -> None:
        graph = self.db.select_graph(self.repo_id)
        cypher_query = """
        UNWIND $edges AS edge
        MATCH (a {node_id: edge.sourceId}), (b {node_id: edge.targetId})
        CREATE (a)-[:`$edge.type` {scopeText: edge.scopeText}]->(b)
        """
        graph.query(
            cypher_query,
            params={"edges": edgesList},
        )

    def detatch_delete_nodes_with_path(self, path: str) -> None:
        graph = self.db.select_graph(self.repo_id)
        cypher_query = "MATCH (n {path: $path}) DETACH DELETE n"
        graph.query(cypher_query, params={"path": path})
