import logging
import re
from typing import List, Dict, Optional, TYPE_CHECKING, Any, Set

if TYPE_CHECKING:
    from blarify.graph.graph import Graph
    from blarify.graph.graph_environment import GraphEnvironment
    from blarify.graph.node import Node
    from blarify.graph.relationship import Relationship

from blarify.graph.node.types.node_labels import NodeLabels
from blarify.graph.relationship.relationship_type import RelationshipType
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    """Generates LLM descriptions for code nodes and creates description nodes."""
    
    def __init__(self, llm_service: LLMService, graph_environment: Optional["GraphEnvironment"] = None):
        self.llm_service = llm_service
        self.graph_environment = graph_environment
        self._prompt_templates = self._initialize_prompt_templates()
    
    def _initialize_prompt_templates(self) -> Dict[NodeLabels, str]:
        """Initialize prompt templates for different node types."""
        return {
            NodeLabels.FILE: """
Given the following code file in a {language} project:

File: {file_path}
File Name: {file_name}

Please provide a concise description (2-3 sentences) of what this file contains, its main purpose, and its role in the project.
""",
            
            NodeLabels.FUNCTION: """
Given the following function in a {language} project:

File: {file_path}
Function: {function_name}
Code:
{code_snippet}

Project context: This is part of a codebase analysis tool that creates graph representations of code.

Please provide a concise description (2-3 sentences) of what this function does, its purpose, and any important implementation details.
""",
            
            NodeLabels.CLASS: """
Given the following class in a {language} project:

File: {file_path}
Class: {class_name}
Code:
{code_snippet}

Project context: This is part of a codebase analysis tool that creates graph representations of code.

Please provide a concise description (2-3 sentences) of what this class represents, its responsibilities, and its role in the system.
""",
            
            NodeLabels.METHOD: """
Given the following method in a {language} project:

File: {file_path}
Class: {class_name}
Method: {method_name}
Code:
{code_snippet}

Please provide a concise description (2-3 sentences) of what this method does, its purpose within the class, and any important implementation details.
""",
            
            NodeLabels.MODULE: """
Given the following module in a {language} project:

Module: {module_path}
Module Name: {module_name}

Please provide a concise description (2-3 sentences) of what this module contains, its main purpose, and its role in the project structure.
"""
        }
    
    def generate_descriptions_for_graph(self, graph: "Graph", node_limit: Optional[int] = None) -> Dict[str, "Node"]:
        """Generate descriptions for all eligible nodes in the graph."""
        if not self.llm_service.is_enabled():
            logger.info("LLM descriptions are disabled")
            return {}
        
        eligible_nodes = self._get_eligible_nodes(graph)
        if node_limit:
            eligible_nodes = eligible_nodes[:node_limit]
        
        logger.info(f"Generating descriptions for {len(eligible_nodes)} nodes")
        
        # Prepare prompts
        prompts: List[Dict[str, Any]] = []
        for node in eligible_nodes:
            prompt_data = self._create_prompt_for_node(node, graph)
            if prompt_data:
                prompts.append(prompt_data)
        
        # Generate descriptions in batches
        descriptions = self.llm_service.generate_batch_descriptions(prompts)
        
        # Create description nodes
        description_nodes: Dict[str, "Node"] = {}
        relationships: List["Relationship"] = []
        
        for node in eligible_nodes:
            node_id = node.hashed_id
            if node_id in descriptions and descriptions[node_id]:
                description_text = descriptions[node_id]
                if description_text:  # Ensure it's not None
                    desc_node, rel = self._create_description_node_and_relationship(
                        node, description_text, graph
                    )
                    if desc_node and rel:
                        description_nodes[desc_node.hashed_id] = desc_node
                        relationships.append(rel)
        
        # Add nodes and relationships to graph
        for desc_node in description_nodes.values():
            graph.add_node(desc_node)
        
        graph.add_references_relationships(relationships)
        
        logger.info(f"Created {len(description_nodes)} description nodes")
        return description_nodes
    
    def _get_eligible_nodes(self, graph: "Graph") -> List["Node"]:
        """Get nodes that should have descriptions generated."""
        eligible_labels = {
            NodeLabels.FILE, NodeLabels.FUNCTION, NodeLabels.CLASS,
            NodeLabels.METHOD, NodeLabels.MODULE
        }
        
        eligible_nodes: List["Node"] = []
        for label in eligible_labels:
            nodes = graph.get_nodes_by_label(label)
            eligible_nodes.extend(nodes)
        
        return eligible_nodes
    
    def _create_prompt_for_node(self, node: "Node", graph: "Graph") -> Optional[Dict[str, str]]:
        """Create a prompt for generating a description of a node."""
        template = self._prompt_templates.get(node.label)
        if not template:
            return None
        
        # Extract context based on node type
        context = self._extract_node_context(node, graph)
        if not context:
            return None
        
        try:
            prompt = template.format(**context)
            return {
                "id": node.hashed_id,
                "prompt": prompt
            }
        except KeyError as e:
            logger.warning(f"Missing context key for node {node.id}: {e}")
            return None
    
    def _extract_node_context(self, node: "Node", graph: "Graph") -> Optional[Dict[str, str]]:
        """Extract context information for a node."""
        context = {
            "file_path": node.path,
            "language": self._detect_language(node.extension),
        }
        
        if node.label == NodeLabels.FILE:
            context["file_name"] = node.name
            
        elif node.label in [NodeLabels.FUNCTION, NodeLabels.METHOD]:
            context["function_name"] = node.name
            context["method_name"] = node.name
            # Get code snippet if available
            if hasattr(node, 'code_text') and node.code_text:
                context["code_snippet"] = str(node.code_text)[:1000]  # Limit snippet length
            else:
                context["code_snippet"] = "# Code snippet not available"
            
            # Add class context for methods
            if node.label == NodeLabels.METHOD and node.parent:
                context["class_name"] = node.parent.name
                
        elif node.label == NodeLabels.CLASS:
            context["class_name"] = node.name
            if hasattr(node, 'code_text') and node.code_text:
                context["code_snippet"] = str(node.code_text)[:1000]
            else:
                context["code_snippet"] = "# Code snippet not available"
                
        elif node.label == NodeLabels.MODULE:
            context["module_path"] = node.path
            context["module_name"] = node.name
        
        return context
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript", 
            ".tsx": "TypeScript",
            ".rb": "Ruby",
            ".cs": "C#",
            ".go": "Go",
            ".php": "PHP",
            ".java": "Java",
        }
        return language_map.get(extension, "Unknown")
    
    def _create_description_node_and_relationship(
        self, 
        target_node: "Node", 
        description_text: str, 
        graph: "Graph"
    ) -> tuple[Optional["Node"], Optional["Relationship"]]:
        """Create a description node and its relationship to the target node."""
        try:
            # Import here to avoid circular imports
            from blarify.graph.node.description_node import DescriptionNode
            from blarify.graph.relationship import Relationship
            
            # Create description node
            desc_node = DescriptionNode(
                path=target_node.path,
                name=f"Description of {target_node.name}",
                level=target_node.level,
                description_text=description_text,
                target_node_id=target_node.hashed_id,
                llm_model=self.llm_service.deployment_name,
                parent=target_node.parent,
                graph_environment=self.graph_environment
            )
            
            # Create relationship
            relationship = Relationship(
                start_node=target_node,
                end_node=desc_node,
                rel_type=RelationshipType.HAS_DESCRIPTION
            )
            
            # Extract references from description and create additional relationships
            referenced_nodes = self._extract_referenced_nodes(description_text, graph)
            for ref_node in referenced_nodes:
                ref_rel = Relationship(
                    start_node=desc_node,
                    end_node=ref_node,
                    rel_type=RelationshipType.REFERENCES_IN_DESCRIPTION
                )
                graph.add_references_relationships([ref_rel])
            
            return desc_node, relationship
            
        except Exception as e:
            logger.error(f"Error creating description node for {target_node.id}: {e}")
            return None, None
    
    def _extract_referenced_nodes(self, description: str, graph: "Graph") -> List["Node"]:
        """Extract nodes that are referenced in the description text."""
        referenced_nodes: List["Node"] = []
        
        # Look for function/class/method names in backticks or quotes
        patterns = [
            r'`([a-zA-Z_][a-zA-Z0-9_]*)`',  # Backticks
            r'"([a-zA-Z_][a-zA-Z0-9_]*)"',  # Double quotes
            r"'([a-zA-Z_][a-zA-Z0-9_]*)'",  # Single quotes
        ]
        
        potential_references: Set[str] = set()
        for pattern in patterns:
            matches = re.findall(pattern, description)
            potential_references.update(matches)
        
        # Try to find nodes with these names
        for ref_name in potential_references:
            # Search in common node types
            for label in [NodeLabels.FUNCTION, NodeLabels.CLASS, NodeLabels.METHOD]:
                nodes = graph.get_nodes_by_label(label)
                for node in nodes:
                    if node.name == ref_name:
                        referenced_nodes.append(node)
                        break
        
        return referenced_nodes