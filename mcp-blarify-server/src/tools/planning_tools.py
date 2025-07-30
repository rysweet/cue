"""MCP tools for change planning."""

import logging
from typing import Dict, Any, List
from neo4j import Driver

from ..processors.graph_traversal import GraphTraversal
from ..processors.context_builder import ContextBuilder
from ..processors.llm_processor import LLMProcessor

logger = logging.getLogger(__name__)


class PlanningTools:
    """MCP tools for planning code changes."""
    
    def __init__(self, driver: Driver):
        """Initialize planning tools."""
        self.driver = driver
        self.graph_traversal = GraphTraversal(driver)
        self.context_builder = ContextBuilder()
        self.llm_processor = LLMProcessor()
    
    async def build_plan_for_change(self, change_request: str) -> str:
        """
        Build an implementation plan for a change request.
        
        Args:
            change_request: Description of the desired change
            
        Returns:
            Markdown-formatted implementation plan
        """
        logger.info(f"Building plan for change: {change_request[:100]}...")
        
        try:
            # Extract entities from the change request
            entities = self.llm_processor.extract_entities_from_request(change_request)
            logger.info(f"Extracted entities: {entities}")
            
            if not entities:
                # If no entities extracted, return a basic plan template
                return self._create_basic_plan_template(change_request)
            
            # Analyze impact for each entity
            impact_analysis = self.graph_traversal.analyze_change_impact(entities)
            
            # Look for related patterns/concepts
            patterns = self._find_related_patterns(change_request)
            
            # Build change context
            change_context = self.context_builder.build_change_plan_context(
                change_request,
                impact_analysis,
                patterns
            )
            
            # Generate implementation plan
            if self.llm_processor.enabled:
                plan = self.llm_processor.create_implementation_plan(
                    change_request,
                    impact_analysis
                )
            else:
                plan = self._create_detailed_plan(change_context)
            
            return plan
            
        except Exception as e:
            logger.error(f"Error building change plan: {e}")
            return f"# Error\n\nFailed to build implementation plan: {str(e)}"
    
    def _find_related_patterns(self, change_request: str) -> Dict[str, Any]:
        """Find patterns or concepts related to the change request."""
        try:
            # Extract potential pattern/concept keywords
            keywords = ["pattern", "architecture", "design", "approach", "strategy"]
            
            patterns = {}
            for keyword in keywords:
                if keyword.lower() in change_request.lower():
                    # Search for related concepts
                    pattern_results = self.graph_traversal.find_patterns(keyword)
                    if pattern_results.get("patterns"):
                        patterns[keyword] = pattern_results["patterns"]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error finding patterns: {e}")
            return {}
    
    def _create_basic_plan_template(self, change_request: str) -> str:
        """Create a basic plan template when no entities are found."""
        return f"""# Implementation Plan

## Change Request
{change_request}

## Analysis
Unable to automatically identify specific code entities from the change request. 
Please provide more specific details about:
- Which files or modules need to be modified
- Which classes or functions are involved
- What new components need to be created

## General Implementation Steps

### 1. Requirements Analysis
- Review the change request in detail
- Identify all affected components
- Define acceptance criteria

### 2. Design
- Plan the technical approach
- Identify dependencies
- Design new components if needed

### 3. Implementation
- Create/modify necessary files
- Implement core functionality
- Handle edge cases

### 4. Testing
- Write unit tests
- Update integration tests
- Perform manual testing

### 5. Documentation
- Update code documentation
- Update user documentation
- Document any API changes

## Next Steps
To create a more detailed plan, please provide specific information about the code elements involved in this change.
"""
    
    def _create_detailed_plan(self, context: Dict[str, Any]) -> str:
        """Create a detailed plan from the context."""
        change_request = context.get("change_request", "")
        impact_summary = context.get("impact_summary", {})
        affected_files = context.get("affected_files", [])
        test_files = context.get("test_files", [])
        doc_files = context.get("documentation_files", [])
        
        plan = f"""# Implementation Plan

## Change Request
{change_request}

## Impact Analysis
- **Entities Affected**: {impact_summary.get('entities_affected', 0)}
- **Total Dependencies**: {impact_summary.get('total_dependents', 0)}
- **Files to Modify**: {impact_summary.get('files_affected', 0)}
- **Test Files**: {impact_summary.get('test_files_affected', 0)}

## Implementation Steps

### 1. Prepare Development Environment
- Create feature branch
- Ensure all tests pass before starting
- Review existing code structure

### 2. Modify Existing Files
"""
        
        # Add files to modify
        for i, file_path in enumerate(affected_files[:10], 1):
            plan += f"\n#### {i}. Update `{file_path}`"
            plan += f"\n- Review current implementation"
            plan += f"\n- Apply necessary changes"
            plan += f"\n- Ensure backward compatibility\n"
        
        if len(affected_files) > 10:
            plan += f"\n... and {len(affected_files) - 10} more files\n"
        
        plan += """
### 3. Create New Components (if needed)
- Identify any new files or modules required
- Follow existing project structure and patterns
- Add appropriate documentation

### 4. Update Tests
"""
        
        if test_files:
            plan += "Existing test files to update:\n"
            for test_file in test_files[:5]:
                plan += f"- `{test_file}`\n"
            if len(test_files) > 5:
                plan += f"- ... and {len(test_files) - 5} more test files\n"
        else:
            plan += "- Create new test files as needed\n"
            plan += "- Ensure comprehensive test coverage\n"
        
        plan += """
### 5. Update Documentation
"""
        
        if doc_files:
            plan += "Documentation files to update:\n"
            for doc_file in doc_files[:5]:
                plan += f"- `{doc_file}`\n"
            if len(doc_files) > 5:
                plan += f"- ... and {len(doc_files) - 5} more documentation files\n"
        else:
            plan += "- Update relevant documentation\n"
            plan += "- Add examples if applicable\n"
        
        plan += """
### 6. Validation
- Run full test suite
- Perform integration testing
- Code review

## Dependencies to Consider
"""
        
        # Add specific entities and their dependencies
        entities = context.get("affected_entities", [])
        for entity in entities[:5]:
            plan += f"- **{entity}**: Check all usages and dependencies\n"
        
        if len(entities) > 5:
            plan += f"- ... and {len(entities) - 5} more entities\n"
        
        plan += """
## Risk Assessment
- **Breaking Changes**: Review all public APIs
- **Performance Impact**: Profile critical paths
- **Security**: Review any security implications

## Rollback Plan
- Keep feature branch separate until fully tested
- Document any migration steps
- Prepare rollback instructions if needed
"""
        
        return plan