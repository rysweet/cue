import os
import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from blarify.graph.node import (
    DocumentationFileNode, ConceptNode, DocumentedEntityNode, Node
)
from blarify.graph.relationship import Relationship
from blarify.graph.relationship.relationship_type import RelationshipType
from .documentation_parser import DocumentationParser
from .concept_extractor import ConceptExtractor
from .documentation_linker import DocumentationLinker

if TYPE_CHECKING:
    from blarify.graph.graph import Graph
    from blarify.graph.graph_environment import GraphEnvironment
    from blarify.llm_descriptions.llm_service import LLMService

logger = logging.getLogger(__name__)


class DocumentationGraphGenerator:
    """
    Generates documentation nodes and relationships for a project.
    
    This class orchestrates the documentation parsing, concept extraction,
    and linking to code nodes.
    """
    
    def __init__(
        self,
        root_path: str,
        graph_environment: "GraphEnvironment",
        llm_service: Optional["LLMService"] = None,
        documentation_patterns: Optional[List[str]] = None,
        max_llm_calls_per_doc: int = 5
    ):
        """
        Initialize the documentation graph generator.
        
        Args:
            root_path: Root directory of the project
            graph_environment: Graph environment for node creation
            llm_service: Optional LLM service for concept extraction
            documentation_patterns: Optional custom documentation patterns
            max_llm_calls_per_doc: Maximum LLM calls per documentation file
        """
        self.root_path = root_path
        self.graph_environment = graph_environment
        self.documentation_parser = DocumentationParser(
            root_path=root_path,
            documentation_patterns=documentation_patterns
        )
        self.concept_extractor = ConceptExtractor(llm_service=llm_service)
        self.documentation_linker = DocumentationLinker()
        self.max_llm_calls_per_doc = max_llm_calls_per_doc
        
        # Track created nodes
        self._doc_file_nodes = {}
        self._concept_nodes = {}
        self._entity_nodes = {}
    
    def generate_documentation_nodes(self, graph: "Graph") -> None:
        """
        Generate documentation nodes and add them to the graph.
        
        Args:
            graph: The graph to add documentation nodes to
        """
        logger.info("Starting documentation node generation")
        
        # Parse documentation files
        doc_data = self.documentation_parser.parse_documentation_files()
        doc_files = doc_data.get("documentation_files", [])
        
        logger.info(f"Found {len(doc_files)} documentation files")
        
        # Process each documentation file
        llm_calls = 0
        for doc_file in doc_files:
            try:
                # Create documentation file node
                doc_node = self._create_documentation_file_node(doc_file)
                graph.add_node(doc_node)
                self._doc_file_nodes[doc_file["path"]] = doc_node
                
                # Extract concepts if within LLM call limit
                if llm_calls < self.max_llm_calls_per_doc * len(doc_files):
                    extracted = self.concept_extractor.extract_from_content(
                        doc_file["content"],
                        doc_file["path"]
                    )
                    llm_calls += 1
                    
                    # Create concept nodes
                    for concept in extracted.get("concepts", []):
                        concept_node = self._create_concept_node(concept, doc_file["path"])
                        graph.add_node(concept_node)
                        self._concept_nodes[concept_node.name] = concept_node
                        
                        # Create relationship from doc to concept
                        rel = Relationship(
                            start_node=doc_node,
                            end_node=concept_node,
                            rel_type=RelationshipType.CONTAINS_CONCEPT
                        )
                        graph.add_references_relationships([rel])
                    
                    # Create entity nodes
                    for entity in extracted.get("entities", []):
                        entity_node = self._create_entity_node(entity, doc_file["path"])
                        graph.add_node(entity_node)
                        self._entity_nodes[entity_node.name] = entity_node
                        
                        # Create relationship from doc to entity
                        rel = Relationship(
                            start_node=doc_node,
                            end_node=entity_node,
                            rel_type=RelationshipType.DESCRIBES_ENTITY
                        )
                        graph.add_references_relationships([rel])
                    
                    # Store extraction results for linking
                    doc_file["extracted"] = extracted
                
            except Exception as e:
                logger.error(f"Error processing documentation file {doc_file['path']}: {e}")
                continue
        
        # Create cross-links to code after all docs are processed
        self._create_documentation_code_links(graph, doc_files)
        
        logger.info("Documentation node generation completed")
    
    def _create_documentation_file_node(self, doc_file: Dict[str, Any]) -> DocumentationFileNode:
        """Create a documentation file node."""
        path = doc_file["path"]
        name = doc_file["name"]
        relative_path = doc_file["relative_path"]
        
        # Determine doc type from extension
        doc_type = os.path.splitext(name)[1].lower().lstrip('.')
        if not doc_type:
            doc_type = "txt"
        
        return DocumentationFileNode(
            path=f"file://{path}",
            name=name,
            level=0,
            relative_path=relative_path,
            doc_type=doc_type,
            graph_environment=self.graph_environment
        )
    
    def _create_concept_node(self, concept: Dict[str, Any], source_file: str) -> ConceptNode:
        """Create a concept node."""
        return ConceptNode(
            name=concept.get("name", "Unknown Concept"),
            description=concept.get("description", ""),
            source_file=source_file,
            level=1,
            graph_environment=self.graph_environment
        )
    
    def _create_entity_node(self, entity: Dict[str, Any], source_file: str) -> DocumentedEntityNode:
        """Create a documented entity node."""
        return DocumentedEntityNode(
            name=entity.get("name", "Unknown Entity"),
            entity_type=entity.get("type", "unknown"),
            description=entity.get("description", ""),
            source_file=source_file,
            level=1,
            graph_environment=self.graph_environment
        )
    
    def _create_documentation_code_links(self, graph: "Graph", doc_files: List[Dict[str, Any]]) -> None:
        """
        Create links between documentation nodes and code nodes.
        
        Args:
            graph: The graph containing all nodes
            doc_files: List of processed documentation files with extraction results
        """
        logger.info("Creating documentation to code links")
        
        for doc_file in doc_files:
            if "extracted" not in doc_file:
                continue
            
            doc_node = self._doc_file_nodes.get(doc_file["path"])
            if not doc_node:
                continue
            
            extracted = doc_file["extracted"]
            
            # Link entities to code
            for entity in extracted.get("entities", []):
                entity_node = self._entity_nodes.get(entity.get("name"))
                if not entity_node:
                    continue
                
                # Find matching code nodes
                code_matches = self.documentation_linker.find_code_matches(entity, graph)
                for code_node in code_matches[:3]:  # type: Node  # Limit to top 3 matches
                    rel = Relationship(
                        start_node=entity_node,
                        end_node=code_node,
                        rel_type=RelationshipType.DOCUMENTS
                    )
                    graph.add_references_relationships([rel])
            
            # Link code references
            for code_ref in extracted.get("code_references", []):
                code_matches = self.documentation_linker.find_code_matches_by_reference(code_ref, graph)
                for code_node in code_matches[:2]:  # type: Node  # Limit to top 2 matches
                    rel = Relationship(
                        start_node=doc_node,
                        end_node=code_node,
                        rel_type=RelationshipType.DOCUMENTS
                    )
                    graph.add_references_relationships([rel])
            
            # Link concepts to implementing code
            for concept in extracted.get("concepts", []):
                concept_node = self._concept_nodes.get(concept.get("name"))
                if not concept_node:
                    continue
                
                # Find code that might implement the concept
                implementing_nodes = self.documentation_linker.link_concepts_to_code(concept, graph)
                for code_node in implementing_nodes[:2]:  # type: Node  # Limit matches
                    rel = Relationship(
                        start_node=code_node,
                        end_node=concept_node,
                        rel_type=RelationshipType.IMPLEMENTS_CONCEPT
                    )
                    graph.add_references_relationships([rel])
        
        logger.info("Documentation to code linking completed")