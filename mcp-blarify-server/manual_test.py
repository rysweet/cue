"""Manual test script to demonstrate MCP server functionality."""

import asyncio
import os
import json
from src.server import BlarifyMCPServer


async def test_mcp_server():
    """Test the MCP server with real Neo4j data."""
    print("MCP Blarify Server - Manual Test")
    print("=" * 60)
    
    # Configure environment
    os.environ.update({
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "testpassword",
        "NEO4J_DATABASE": "neo4j"
    })
    
    # Create server
    server = BlarifyMCPServer()
    
    try:
        # Connect to Neo4j
        print("\n1. Connecting to Neo4j...")
        await server._connect_to_neo4j()
        print("✓ Connected successfully")
        
        # List available tools
        print("\n2. Available tools:")
        tools = await server.server.list_tools()
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test getContextForFiles
        print("\n3. Testing getContextForFiles")
        print("-" * 40)
        result = await server.server.call_tool(
            "getContextForFiles",
            {"file_paths": ["user_service.py", "auth_service.py"]}
        )
        print("Request: Get context for user_service.py and auth_service.py")
        print("Response:")
        print(result[0].text[:1000] + "..." if len(result[0].text) > 1000 else result[0].text)
        
        # Test getContextForSymbol
        print("\n4. Testing getContextForSymbol")
        print("-" * 40)
        result = await server.server.call_tool(
            "getContextForSymbol",
            {"symbol_name": "UserService", "symbol_type": "class"}
        )
        print("Request: Get context for UserService class")
        print("Response:")
        print(result[0].text[:1000] + "..." if len(result[0].text) > 1000 else result[0].text)
        
        # Test buildPlanForChange
        print("\n5. Testing buildPlanForChange")
        print("-" * 40)
        result = await server.server.call_tool(
            "buildPlanForChange",
            {"change_request": "Add email verification to user registration process"}
        )
        print("Request: Build plan for adding email verification")
        print("Response:")
        print(result[0].text[:1500] + "..." if len(result[0].text) > 1500 else result[0].text)
        
        # Test with non-existent file
        print("\n6. Testing error handling")
        print("-" * 40)
        result = await server.server.call_tool(
            "getContextForFiles",
            {"file_paths": ["non_existent_file.py"]}
        )
        print("Request: Get context for non-existent file")
        print("Response:")
        print(result[0].text)
        
        # Test fuzzy symbol search
        print("\n7. Testing fuzzy symbol search")
        print("-" * 40)
        result = await server.server.call_tool(
            "getContextForSymbol",
            {"symbol_name": "user"}  # Partial match
        )
        print("Request: Get context for 'user' (partial match)")
        print("Response:")
        print(result[0].text[:800] + "..." if len(result[0].text) > 800 else result[0].text)
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if server.driver:
            server.driver.close()
            print("\n✓ Closed Neo4j connection")


async def test_direct_queries():
    """Test direct graph queries to verify data."""
    from neo4j import GraphDatabase
    
    print("\n\nDirect Graph Queries")
    print("=" * 60)
    
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    
    try:
        with driver.session() as session:
            # Query 1: Find all classes
            print("\n1. All classes in the graph:")
            result = session.run("MATCH (c:CLASS) RETURN c.name as name ORDER BY name")
            for record in result:
                print(f"   - {record['name']}")
            
            # Query 2: UserService details
            print("\n2. UserService details:")
            result = session.run("""
                MATCH (us:CLASS {name: 'UserService'})
                OPTIONAL MATCH (us)-[:HAS_METHOD]->(m)
                OPTIONAL MATCH (us)-[:INHERITS_FROM]->(parent)
                OPTIONAL MATCH (us)<-[:USES]-(caller)
                OPTIONAL MATCH (desc)-[:DESCRIBES]->(us)
                RETURN us.name as name,
                       collect(DISTINCT m.name) as methods,
                       parent.name as parent,
                       collect(DISTINCT caller.name) as callers,
                       desc.description as description
            """)
            
            for record in result:
                print(f"   Name: {record['name']}")
                print(f"   Parent: {record['parent']}")
                print(f"   Methods: {', '.join(record['methods'])}")
                print(f"   Called by: {', '.join(record['callers'])}")
                print(f"   Description: {record['description']}")
            
            # Query 3: File dependencies
            print("\n3. File import relationships:")
            result = session.run("""
                MATCH (f1:FILE)-[:IMPORTS]->(f2:FILE)
                RETURN f1.name as importer, f2.name as imported
                ORDER BY importer
            """)
            
            for record in result:
                print(f"   {record['importer']} → {record['imported']}")
            
    finally:
        driver.close()


async def main():
    """Run all tests."""
    await test_mcp_server()
    await test_direct_queries()


if __name__ == "__main__":
    print("Starting manual test...")
    print("Make sure Neo4j is running (docker-compose up -d)")
    print("Make sure test data is loaded (python tests/setup_test_graph.py)")
    input("Press Enter to continue...")
    
    asyncio.run(main())