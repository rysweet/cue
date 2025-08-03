"""Set up a test cue graph in Neo4j for integration testing."""

import logging
from neo4j import GraphDatabase
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGraphSetup:
    """Sets up a test graph that mimics cue output."""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="testpassword"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared database")
    
    def create_test_graph(self):
        """Create a test graph with various node types and relationships."""
        with self.driver.session() as session:
            # Create folder structure
            session.run("""
                CREATE (root:FOLDER {path: 'file:///project', name: 'project'})
                CREATE (src:FOLDER {path: 'file:///project/src', name: 'src'})
                CREATE (services:FOLDER {path: 'file:///project/src/services', name: 'services'})
                CREATE (controllers:FOLDER {path: 'file:///project/src/controllers', name: 'controllers'})
                CREATE (models:FOLDER {path: 'file:///project/src/models', name: 'models'})
                CREATE (tests:FOLDER {path: 'file:///project/tests', name: 'tests'})
                CREATE (docs:FOLDER {path: 'file:///project/docs', name: 'docs'})
                
                CREATE (root)-[:CONTAINS]->(src)
                CREATE (root)-[:CONTAINS]->(tests)
                CREATE (root)-[:CONTAINS]->(docs)
                CREATE (src)-[:CONTAINS]->(services)
                CREATE (src)-[:CONTAINS]->(controllers)
                CREATE (src)-[:CONTAINS]->(models)
            """)
            logger.info("Created folder structure")
            
            # Create files and code nodes
            session.run("""
                // User model file
                CREATE (user_model_file:FILE {
                    path: 'file:///project/src/models/user.py',
                    name: 'user.py',
                    extension: '.py'
                })
                CREATE (user_class:CLASS {
                    name: 'User',
                    path: 'file:///project/src/models/user.py',
                    line: 10
                })
                CREATE (user_init:METHOD:FUNCTION {
                    name: '__init__',
                    path: 'file:///project/src/models/user.py',
                    line: 15
                })
                CREATE (user_validate:METHOD:FUNCTION {
                    name: 'validate',
                    path: 'file:///project/src/models/user.py',
                    line: 25
                })
                
                CREATE (user_model_file)-[:CONTAINS]->(user_class)
                CREATE (user_class)-[:HAS_METHOD]->(user_init)
                CREATE (user_class)-[:HAS_METHOD]->(user_validate)
                
                // User service file
                CREATE (user_service_file:FILE {
                    path: 'file:///project/src/services/user_service.py',
                    name: 'user_service.py',
                    extension: '.py'
                })
                CREATE (base_service:CLASS {
                    name: 'BaseService',
                    path: 'file:///project/src/services/base.py',
                    line: 5
                })
                CREATE (user_service:CLASS {
                    name: 'UserService',
                    path: 'file:///project/src/services/user_service.py',
                    line: 20
                })
                CREATE (create_user:METHOD:FUNCTION {
                    name: 'create_user',
                    path: 'file:///project/src/services/user_service.py',
                    line: 30
                })
                CREATE (get_user:METHOD:FUNCTION {
                    name: 'get_user',
                    path: 'file:///project/src/services/user_service.py',
                    line: 45
                })
                CREATE (update_user:METHOD:FUNCTION {
                    name: 'update_user',
                    path: 'file:///project/src/services/user_service.py',
                    line: 60
                })
                
                CREATE (user_service_file)-[:CONTAINS]->(user_service)
                CREATE (user_service)-[:INHERITS_FROM]->(base_service)
                CREATE (user_service)-[:HAS_METHOD]->(create_user)
                CREATE (user_service)-[:HAS_METHOD]->(get_user)
                CREATE (user_service)-[:HAS_METHOD]->(update_user)
                
                // Auth service file
                CREATE (auth_service_file:FILE {
                    path: 'file:///project/src/services/auth_service.py',
                    name: 'auth_service.py',
                    extension: '.py'
                })
                CREATE (auth_service:CLASS {
                    name: 'AuthService',
                    path: 'file:///project/src/services/auth_service.py',
                    line: 15
                })
                CREATE (login:METHOD:FUNCTION {
                    name: 'login',
                    path: 'file:///project/src/services/auth_service.py',
                    line: 25
                })
                CREATE (verify_token:METHOD:FUNCTION {
                    name: 'verify_token',
                    path: 'file:///project/src/services/auth_service.py',
                    line: 40
                })
                
                CREATE (auth_service_file)-[:CONTAINS]->(auth_service)
                CREATE (auth_service)-[:HAS_METHOD]->(login)
                CREATE (auth_service)-[:HAS_METHOD]->(verify_token)
                
                // User controller file
                CREATE (user_controller_file:FILE {
                    path: 'file:///project/src/controllers/user_controller.py',
                    name: 'user_controller.py',
                    extension: '.py'
                })
                CREATE (user_controller:CLASS {
                    name: 'UserController',
                    path: 'file:///project/src/controllers/user_controller.py',
                    line: 10
                })
                CREATE (handle_create:METHOD:FUNCTION {
                    name: 'handle_create',
                    path: 'file:///project/src/controllers/user_controller.py',
                    line: 20
                })
                CREATE (handle_get:METHOD:FUNCTION {
                    name: 'handle_get',
                    path: 'file:///project/src/controllers/user_controller.py',
                    line: 35
                })
                
                CREATE (user_controller_file)-[:CONTAINS]->(user_controller)
                CREATE (user_controller)-[:HAS_METHOD]->(handle_create)
                CREATE (user_controller)-[:HAS_METHOD]->(handle_get)
            """)
            logger.info("Created code nodes")
            
            # Create relationships between code elements
            session.run("""
                MATCH (us:CLASS {name: 'UserService'})
                MATCH (uc:CLASS {name: 'User'})
                MATCH (ctrl:CLASS {name: 'UserController'})
                MATCH (auth:CLASS {name: 'AuthService'})
                
                // UserService uses User model
                CREATE (us)-[:USES]->(uc)
                
                // UserController uses UserService
                CREATE (ctrl)-[:USES]->(us)
                
                // AuthService uses UserService
                CREATE (auth)-[:USES]->(us)
                
                // Method calls
                MATCH (create:FUNCTION {name: 'create_user'})
                MATCH (validate:FUNCTION {name: 'validate'})
                CREATE (create)-[:CALLS]->(validate)
                
                MATCH (login:FUNCTION {name: 'login'})
                MATCH (get:FUNCTION {name: 'get_user'})
                CREATE (login)-[:CALLS]->(get)
                
                MATCH (handle:FUNCTION {name: 'handle_create'})
                CREATE (handle)-[:CALLS]->(create)
            """)
            logger.info("Created code relationships")
            
            # Create import relationships
            session.run("""
                MATCH (usf:FILE {name: 'user_service.py'})
                MATCH (umf:FILE {name: 'user.py'})
                CREATE (usf)-[:IMPORTS]->(umf)
                
                MATCH (asf:FILE {name: 'auth_service.py'})
                CREATE (asf)-[:IMPORTS]->(usf)
                
                MATCH (ucf:FILE {name: 'user_controller.py'})
                CREATE (ucf)-[:IMPORTS]->(usf)
            """)
            logger.info("Created import relationships")
            
            # Create LLM description nodes
            session.run("""
                MATCH (us:CLASS {name: 'UserService'})
                CREATE (us_desc:DESCRIPTION {
                    description: 'Core service for user management operations. Handles CRUD operations for users with validation and security checks.',
                    node_id: id(us)
                })
                CREATE (us_desc)-[:DESCRIBES]->(us)
                
                MATCH (auth:CLASS {name: 'AuthService'})
                CREATE (auth_desc:DESCRIPTION {
                    description: 'Authentication service handling user login, token generation, and session management.',
                    node_id: id(auth)
                })
                CREATE (auth_desc)-[:DESCRIBES]->(auth)
            """)
            logger.info("Created LLM descriptions")
            
            # Create documentation nodes
            session.run("""
                CREATE (readme:DOCUMENTATION_FILE {
                    path: 'file:///project/README.md',
                    name: 'README.md',
                    doc_type: 'md'
                })
                CREATE (api_doc:DOCUMENTATION_FILE {
                    path: 'file:///project/docs/api.md',
                    name: 'api.md',
                    doc_type: 'md'
                })
                
                // Documentation concepts
                CREATE (auth_concept:CONCEPT {
                    name: 'JWT Authentication',
                    description: 'JSON Web Token based authentication system'
                })
                CREATE (rest_concept:CONCEPT {
                    name: 'REST API',
                    description: 'RESTful API design patterns'
                })
                
                CREATE (readme)-[:CONTAINS_CONCEPT]->(auth_concept)
                CREATE (api_doc)-[:CONTAINS_CONCEPT]->(rest_concept)
                
                // Link documentation to code
                MATCH (auth:CLASS {name: 'AuthService'})
                CREATE (auth_concept)-[:DOCUMENTS]->(auth)
                
                MATCH (ctrl:CLASS {name: 'UserController'})
                CREATE (rest_concept)-[:DOCUMENTS]->(ctrl)
            """)
            logger.info("Created documentation nodes")
            
            # Create filesystem nodes
            session.run("""
                CREATE (fs_src:FILESYSTEM_DIRECTORY {
                    path: '/project/src',
                    name: 'src',
                    size: 4096
                })
                CREATE (fs_services:FILESYSTEM_DIRECTORY {
                    path: '/project/src/services',
                    name: 'services',
                    size: 4096
                })
                CREATE (fs_user_service:FILESYSTEM_FILE {
                    path: '/project/src/services/user_service.py',
                    name: 'user_service.py',
                    size: 2048,
                    extension: 'py'
                })
                
                CREATE (fs_src)-[:HAS_CHILD]->(fs_services)
                CREATE (fs_services)-[:HAS_CHILD]->(fs_user_service)
                
                // Link filesystem to code
                MATCH (usf:FILE {name: 'user_service.py'})
                CREATE (fs_user_service)-[:REPRESENTS]->(usf)
            """)
            logger.info("Created filesystem nodes")
            
            # Create test files
            session.run("""
                CREATE (test_file:FILE {
                    path: 'file:///project/tests/test_user_service.py',
                    name: 'test_user_service.py',
                    extension: '.py'
                })
                
                MATCH (us:CLASS {name: 'UserService'})
                CREATE (test_file)-[:TESTS]->(us)
            """)
            logger.info("Created test relationships")
            
            # Add file relationships to folders
            session.run("""
                MATCH (models:FOLDER {name: 'models'})
                MATCH (umf:FILE {name: 'user.py'})
                CREATE (models)-[:CONTAINS]->(umf)
                
                MATCH (services:FOLDER {name: 'services'})
                MATCH (usf:FILE {name: 'user_service.py'})
                MATCH (asf:FILE {name: 'auth_service.py'})
                CREATE (services)-[:CONTAINS]->(usf)
                CREATE (services)-[:CONTAINS]->(asf)
                
                MATCH (controllers:FOLDER {name: 'controllers'})
                MATCH (ucf:FILE {name: 'user_controller.py'})
                CREATE (controllers)-[:CONTAINS]->(ucf)
                
                MATCH (tests:FOLDER {name: 'tests'})
                MATCH (tf:FILE {name: 'test_user_service.py'})
                CREATE (tests)-[:CONTAINS]->(tf)
                
                MATCH (docs:FOLDER {name: 'docs'})
                MATCH (readme:DOCUMENTATION_FILE {name: 'README.md'})
                MATCH (api:DOCUMENTATION_FILE {name: 'api.md'})
                CREATE (docs)-[:CONTAINS]->(readme)
                CREATE (docs)-[:CONTAINS]->(api)
            """)
            logger.info("Created folder relationships")
    
    def verify_graph(self):
        """Verify the graph was created correctly."""
        with self.driver.session() as session:
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n) as labels, count(n) as count
                ORDER BY count DESC
            """)
            
            print("\nNode counts by label:")
            for record in result:
                print(f"  {record['labels']}: {record['count']}")
            
            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            
            print("\nRelationship counts by type:")
            for record in result:
                print(f"  {record['type']}: {record['count']}")
            
            # Sample queries
            print("\nSample query - UserService context:")
            result = session.run("""
                MATCH (us:CLASS {name: 'UserService'})
                OPTIONAL MATCH (us)-[:HAS_METHOD]->(m)
                OPTIONAL MATCH (us)-[:INHERITS_FROM]->(parent)
                OPTIONAL MATCH (us)<-[:USES]-(caller)
                RETURN us.name as name,
                       collect(DISTINCT m.name) as methods,
                       parent.name as inherits_from,
                       collect(DISTINCT caller.name) as used_by
            """)
            
            for record in result:
                print(f"  Name: {record['name']}")
                print(f"  Methods: {record['methods']}")
                print(f"  Inherits from: {record['inherits_from']}")
                print(f"  Used by: {record['used_by']}")


def main():
    """Set up the test graph."""
    # Wait for Neo4j to be ready
    print("Waiting for Neo4j to start...")
    time.sleep(5)
    
    setup = TestGraphSetup()
    try:
        setup.clear_database()
        setup.create_test_graph()
        setup.verify_graph()
        print("\nTest graph created successfully!")
    finally:
        setup.close()


if __name__ == "__main__":
    main()