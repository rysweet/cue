We have forked a program called Blarify that uses tree-sitter and language server protocol servers to create a graph of a codebase AST and its bindings to symbols. This is a powerful tool for understanding code structure and relationships.  Analyze this code base and remember its structure so that you can make plans about the new features we will add. 

We are going to add a new feature to this code - for every node created in the graph, we will also add a related node (connected by an edge) that describes the node's purpose or functionality. This will help users quickly understand the role of each code element. We will use Azure OpenAI's GPT-4.1 to generate these descriptions.

We will need to parse the Azure OpenAI settings from a .env file (use dotenv lib) and use AzureOpenAI from the openai package to interact with the API. The descriptions will be stored in the graph database alongside the code elements.

You will need to come up with a prompt that you feed to the LLM to ask it to summarize the code element. The prompt should be clear and concise, providing enough context for the LLM to generate a meaningful description - eg since you will have access to the project code overall you may be able to provide additional context that you derive from the project README, APIdoc, etc. 

You will also need to create edges between other nodes of code objects that might be referenced in the LLM description. 

You will need to use neo4j in a docker container to store the graph data. Ensure you have the Neo4j Python driver installed and configured to connect to the Neo4j instance. We also want the neo4j APOC plugin (https://neo4j.com/labs/apoc/) and the neo4j vector search support (https://neo4j.com/developer/genai-ecosystem/vector-search/) installed in the Neo4j instance to support advanced graph operations and vector similarity search. 

You will need to build up tests for this feature and may need to bootstrap testing for the project in general. The tests should manage their dependencies (eg neo4j) and should do so idempotently, not touching the dev database or volumes. 

Think carefully about the best way to add this LLM description generation feature. If additional extensibility is required to make it clean, then investigate that. Once you have a good plan, please create an issue in the issues database to descibe the feature and record your plan, step by step. 

Once the issue is created, then you may please create a bew branch for the issue and switch to it, and then proceed to divide the work into clear steps and allocate it as needed to implement by yourself or dedicated subagents as needed. 