#!/usr/bin/env python3
"""
Simple structural tests for Agent Manager sub-agent.

These tests validate that the agent-manager file exists and has proper structure.
"""

import os
import unittest
from pathlib import Path


class TestAgentManagerStructure(unittest.TestCase):
    """Test the Agent Manager sub-agent file structure."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.agent_file = self.project_root / '.claude' / 'agents' / 'agent-manager.md'
    
    def test_agent_manager_file_exists(self):
        """Test that agent-manager.md exists in the correct location."""
        self.assertTrue(self.agent_file.exists(), 
                       f"Agent manager file not found at {self.agent_file}")
    
    def test_agent_manager_has_frontmatter(self):
        """Test that agent-manager.md has proper YAML frontmatter."""
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Check for YAML frontmatter
        self.assertTrue(content.startswith('---\n'), 
                       "Agent file should start with YAML frontmatter")
        
        # Find end of frontmatter
        frontmatter_end = content.find('\n---\n', 4)
        self.assertGreater(frontmatter_end, 0, 
                          "YAML frontmatter should be properly closed")
        
        # Check required fields in frontmatter
        frontmatter = content[4:frontmatter_end]
        required_fields = ['name:', 'description:', 'required_tools:']
        
        for field in required_fields:
            self.assertIn(field, frontmatter, 
                         f"Frontmatter missing required field: {field}")
    
    def test_agent_manager_content_structure(self):
        """Test that agent-manager.md has expected content sections."""
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Check for key sections
        expected_sections = [
            '# Agent Manager',
            '## Overview',
            '## Core Capabilities',
            '## Command Reference',
            '## Implementation Approach'
        ]
        
        for section in expected_sections:
            self.assertIn(section, content, 
                         f"Agent file missing expected section: {section}")
    
    def test_agent_manager_tools_listed(self):
        """Test that required tools are properly listed."""
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Extract frontmatter
        frontmatter_end = content.find('\n---\n', 4)
        frontmatter = content[4:frontmatter_end]
        
        # Check for required_tools
        self.assertIn('required_tools:', frontmatter)
        
        # Common tools that should be included
        expected_tools = ['Read', 'Write', 'Bash', 'Grep']
        tools_line = [line for line in frontmatter.split('\n') 
                      if 'required_tools:' in line]
        
        if tools_line:
            tools_str = tools_line[0]
            for tool in expected_tools:
                self.assertIn(tool, tools_str, 
                             f"Required tool '{tool}' not found in tools list")


if __name__ == '__main__':
    unittest.main()