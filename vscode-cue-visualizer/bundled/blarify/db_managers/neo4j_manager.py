import os
import time
from typing import Any, List

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase, exceptions, basic_auth
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class Neo4jManager:
    entity_id: str
    repo_id: str
    driver: Driver
    
    def _sanitize_auth_error(self, error_message: str) -> str:
        """
        Sanitize authentication error messages to prevent credential exposure.
        """
        # Remove potentially sensitive information from error messages
        sanitized = error_message
        
        # Remove any potential credential information
        sensitive_patterns = [
            r'password[=:][^\s,}]+',
            r'user[=:][^\s,}]+',
            r'username[=:][^\s,}]+',
            r'auth[=:][^\s,}]+',
            r'token[=:][^\s,}]+'
        ]
        
        import re
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
            
        return sanitized
    
    def _try_basic_auth_connection(self, uri: str, user: str, password: str, max_connections: int) -> bool:
        """
        Attempt connection using Neo4j 5.x basic_auth format.
        Returns True if successful, False otherwise.
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password), max_connection_pool_size=max_connections)
            self._verify_authentication()
            logger.info("Neo4j 5.x basic_auth connection successful")
            return True
        except Exception as e:
            logger.debug(f"Basic auth connection failed: {self._sanitize_auth_error(str(e))}")
            return False
    
    def _try_tuple_auth_connection(self, uri: str, user: str, password: str, max_connections: int) -> bool:
        """
        Attempt connection using Neo4j 4.x tuple auth format.
        Returns True if successful, False otherwise.
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_pool_size=max_connections)
            self._verify_authentication()
            logger.info("Neo4j 4.x tuple auth connection successful")
            return True
        except Exception as e:
            logger.debug(f"Tuple auth connection failed: {self._sanitize_auth_error(str(e))}")
            return False
    
    def _handle_auth_error(self, e: exceptions.AuthError, uri: str, user: str, password: str, max_connections: int) -> bool:
        """
        Handle authentication errors with fallback mechanism.
        Returns True if fallback successful, False otherwise.
        """
        if "missing key" in str(e).lower() and "principal" in str(e).lower():
            logger.error(f"Neo4j authentication failed: {self._sanitize_auth_error(str(e))}")
            logger.info("Attempting fallback authentication method...")
            
            if self._try_tuple_auth_connection(uri, user, password, max_connections):
                return True
            else:
                sanitized_original = self._sanitize_auth_error(str(e))
                raise Exception(f"Neo4j authentication failed with both 5.x and 4.x formats. Original error: {sanitized_original}")
        else:
            logger.error(f"Neo4j authentication error: {self._sanitize_auth_error(str(e))}")
            raise e

    def __init__(
        self,
        repo_id: str = None,
        entity_id: str = None,
        max_connections: int = 50,
        uri: str = None,
        user: str = None,
        password: str = None,
    ):
        uri = uri or os.getenv("NEO4J_URI")
        user = user or os.getenv("NEO4J_USERNAME")
        password = password or os.getenv("NEO4J_PASSWORD")

        retries = 3
        for attempt in range(retries):
            try:
                # Try Neo4j 5.x compatible authentication format first
                if self._try_basic_auth_connection(uri, user, password, max_connections):
                    logger.info(f"Neo4j connection established successfully on attempt {attempt + 1}")
                    break
                else:
                    raise Exception("Basic auth connection failed")
                    
            except exceptions.ServiceUnavailable as e:
                if attempt < retries - 1:
                    logger.warning(f"Neo4j connection attempt {attempt + 1} failed: {e}. Retrying in {2**attempt} seconds...")
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    logger.error(f"Neo4j connection failed after {retries} attempts: {e}")
                    raise e
                    
            except exceptions.AuthError as e:
                if self._handle_auth_error(e, uri, user, password, max_connections):
                    logger.info(f"Neo4j connection established successfully on attempt {attempt + 1} using fallback auth")
                    break
                # If _handle_auth_error returns False, it will raise an exception
                
            except Exception as e:
                logger.error(f"Unexpected error during Neo4j connection attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(2**attempt)
                else:
                    raise e

        self.repo_id = repo_id if repo_id is not None else "default_repo"
        self.entity_id = entity_id if entity_id is not None else "default_user"

    def _verify_authentication(self):
        """
        Verify that authentication is working by testing connectivity.
        This helps detect authentication issues early.
        """
        try:
            with self.driver.session() as session:
                # Simple query to verify authentication and connectivity
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise Exception("Authentication verification failed - unexpected result")
                logger.debug("Neo4j authentication verification successful")
        except Exception as e:
            logger.error(f"Neo4j authentication verification failed: {e}")
            raise e

    def get_server_info(self):
        """
        Get Neo4j server information for diagnostics and version detection.
        """
        try:
            with self.driver.session() as session:
                result = session.run("CALL dbms.components() YIELD name, versions, edition")
                components = []
                for record in result:
                    components.append({
                        "name": record["name"],
                        "versions": record["versions"],
                        "edition": record["edition"]
                    })
                logger.info(f"Neo4j server components: {components}")
                return components
        except Exception as e:
            logger.warning(f"Could not retrieve Neo4j server info: {e}")
            return []

    def health_check(self, test_write: bool = False):
        """
        Perform a comprehensive health check of the Neo4j connection.
        
        Args:
            test_write: If True, perform a write test to verify write capabilities.
                       If False, only test read connectivity. Default: False for performance.
        """
        try:
            # Test basic connectivity
            self._verify_authentication()
            
            # Get server information
            server_info = self.get_server_info()
            
            # Optionally test write capability
            if test_write:
                with self.driver.session() as session:
                    session.run("CREATE (test:HealthCheck {timestamp: $timestamp}) DELETE test", timestamp=int(time.time()))
                logger.info("Neo4j health check passed (including write test)")
            else:
                logger.info("Neo4j health check passed (read-only)")
            
            return {
                "status": "healthy",
                "server_info": server_info,
                "write_tested": test_write,
                "timestamp": int(time.time())
            }
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "write_tested": test_write,
                "timestamp": int(time.time())
            }

    def close(self):
        # Close the connection to the database
        self.driver.close()

    def save_graph(self, nodes: List[Any], edges: List[Any]):
        self.create_nodes(nodes)
        self.create_edges(edges)

    def create_nodes(self, nodeList: List[Any]):
        # Function to create nodes in the Neo4j database
        with self.driver.session() as session:
            session.write_transaction(
                self._create_nodes_txn, nodeList, 100, repoId=self.repo_id, entityId=self.entity_id
            )

    def create_edges(self, edgesList: List[Any]):
        # Function to create edges between nodes in the Neo4j database
        with self.driver.session() as session:
            session.write_transaction(self._create_edges_txn, edgesList, 100, entityId=self.entity_id)

    @staticmethod
    def _create_nodes_txn(tx, nodeList: List[Any], batch_size: int, repoId: str, entityId: str):
        node_creation_query = """
        CALL apoc.periodic.iterate(
            "UNWIND $nodeList AS node RETURN node",
            "CALL apoc.merge.node(
            node.extra_labels + [node.type, 'NODE'],
            apoc.map.merge(node.attributes, {repoId: $repoId, entityId: $entityId}),
            {},
            {}
            )
            YIELD node as n RETURN count(n) as count",
            {batchSize: $batchSize, parallel: false, iterateList: true, params: {nodeList: $nodeList, repoId: $repoId, entityId: $entityId}}
        )
        YIELD batches, total, errorMessages, updateStatistics
        RETURN batches, total, errorMessages, updateStatistics
        """

        result = tx.run(node_creation_query, nodeList=nodeList, batchSize=batch_size, repoId=repoId, entityId=entityId)

        # Fetch the result
        for record in result:
            logger.info(f"Created {record['total']} nodes")
            print(record)

    @staticmethod
    def _create_edges_txn(tx, edgesList: List[Any], batch_size: int, entityId: str):
        # Cypher query using apoc.periodic.iterate for creating edges
        edge_creation_query = """
        CALL apoc.periodic.iterate(
            'WITH $edgesList AS edges UNWIND edges AS edgeObject RETURN edgeObject',
            'MATCH (node1:NODE {node_id: edgeObject.sourceId}) 
            MATCH (node2:NODE {node_id: edgeObject.targetId}) 
            CALL apoc.merge.relationship(
            node1, 
            edgeObject.type, 
            {scopeText: edgeObject.scopeText}, 
            {}, 
            node2, 
            {}
            ) 
            YIELD rel RETURN rel',
            {batchSize:$batchSize, parallel:false, iterateList: true, params:{edgesList: $edgesList, entityId: $entityId}}
        )
        YIELD batches, total, errorMessages, updateStatistics
        RETURN batches, total, errorMessages, updateStatistics
        """
        # Execute the query
        result = tx.run(edge_creation_query, edgesList=edgesList, batchSize=batch_size, entityId=entityId)

        # Fetch the result
        for record in result:
            logger.info(f"Created {record['total']} edges")

    def detatch_delete_nodes_with_path(self, path: str):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n {path: $path})
                DETACH DELETE n
                """,
                path=path,
            )
            return result.data()
