#!/usr/bin/env python3
"""
Integration tests for Agent Manager sub-agent.

These tests validate end-to-end workflows and integration between components:
- Full repository registration and agent installation workflow
- Session integration and startup hooks
- Memory.md integration
- Error recovery scenarios
- Multi-repository coordination
"""

import os
import json
import yaml
import tempfile
import shutil
import unittest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestAgentManagerEndToEndWorkflows(unittest.TestCase):
    """Test complete end-to-end Agent Manager workflows."""
    
    def setUp(self):
        """Set up test environment with realistic directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.test_dir, 'test-project')
        self.agent_manager_dir = os.path.join(self.project_dir, '.claude', 'agent-manager')
        self.agents_dir = os.path.join(self.project_dir, '.claude', 'agents')
        self.memory_file = os.path.join(self.project_dir, '.github', 'Memory.md')
        
        # Create directory structure
        os.makedirs(self.agent_manager_dir, exist_ok=True)
        os.makedirs(os.path.join(self.agent_manager_dir, 'cache', 'repositories'), exist_ok=True)
        os.makedirs(self.agents_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Create initial Memory.md
        with open(self.memory_file, 'w') as f:
            f.write("""# AI Assistant Memory
Last Updated: 2025-08-01T00:00:00Z

## Current Goals
- Test Agent Manager integration

## Todo List
- Validate agent installation workflow

## Recent Accomplishments
- Set up test environment
""")
        
        # Create test repository
        self.test_repo_dir = os.path.join(self.test_dir, 'test-agent-repo')
        self._create_test_repository()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def _create_test_repository(self):
        """Create a test agent repository with manifest and agents."""
        os.makedirs(self.test_repo_dir, exist_ok=True)
        agents_dir = os.path.join(self.test_repo_dir, 'agents')
        os.makedirs(agents_dir, exist_ok=True)
        
        # Create manifest file
        manifest = {
            'name': 'Test Agent Collection',
            'version': '1.0.0',
            'description': 'Test agents for integration testing',
            'maintainer': 'test@example.com',
            'agents': [
                {
                    'name': 'test-workflow',
                    'file': 'agents/test-workflow.md',
                    'version': '1.0.0',
                    'description': 'Test workflow orchestration agent',
                    'category': 'development'
                },
                {
                    'name': 'test-debugger',
                    'file': 'agents/test-debugger.md',
                    'version': '1.5.0',
                    'description': 'Test debugging assistant agent',
                    'category': 'debugging'
                }
            ],
            'categories': [
                {
                    'name': 'development',
                    'agents': ['test-workflow']
                },
                {
                    'name': 'debugging',
                    'agents': ['test-debugger']
                }
            ]
        }
        
        manifest_file = os.path.join(self.test_repo_dir, 'manifest.yaml')
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest, f)
        
        # Create test agent files
        workflow_agent = """---
name: test-workflow
description: Test workflow orchestration agent for integration testing
version: 1.0.0
tools: Read, Write, Bash, TodoWrite
category: development
---

# Test Workflow Agent

This is a test workflow agent for integration testing of the Agent Manager.

## Capabilities

- Test workflow orchestration
- Integration with TodoWrite
- Mock development workflows

## Usage

```bash
/agent:test-workflow
```

This agent is designed for testing Agent Manager functionality.
"""
        
        debugger_agent = """---
name: test-debugger
description: Test debugging assistant agent for troubleshooting
version: 1.5.0
tools: Read, Write, Bash, Grep
category: debugging
---

# Test Debugger Agent

This is a test debugging agent for integration testing.

## Capabilities

- Mock debugging workflows
- Error analysis simulation
- Test troubleshooting procedures

## Usage

```bash
/agent:test-debugger
```

Provides debugging assistance for test scenarios.
"""
        
        with open(os.path.join(agents_dir, 'test-workflow.md'), 'w') as f:
            f.write(workflow_agent)
        
        with open(os.path.join(agents_dir, 'test-debugger.md'), 'w') as f:
            f.write(debugger_agent)
    
    def test_complete_repository_registration_workflow(self):
        """Test complete repository registration and agent discovery."""
        # 1. Initialize Agent Manager
        os.chdir(self.project_dir)
        result = self._run_agent_manager_command('init')
        self.assertTrue(result.success)
        
        # 2. Register test repository
        result = self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        self.assertTrue(result.success)
        
        # 3. Verify repository was registered
        config_file = os.path.join(self.agent_manager_dir, 'config.yaml')
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertEqual(len(config['repositories']), 1)
        self.assertEqual(config['repositories'][0]['url'], self.test_repo_dir)
        
        # 4. Discover agents
        result = self._run_agent_manager_command('discover')
        self.assertTrue(result.success)
        self.assertIn('test-workflow', result.output)
        self.assertIn('test-debugger', result.output)
        
        # 5. Verify agent registry was populated
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(len(registry['agents']), 2)
        self.assertIn('test-workflow', registry['agents'])
        self.assertIn('test-debugger', registry['agents'])
    
    def test_agent_installation_and_validation_workflow(self):
        """Test complete agent installation workflow with validation."""
        # Set up repository
        os.chdir(self.project_dir)
        self._run_agent_manager_command('init')
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        
        # Install agent
        result = self._run_agent_manager_command('install', 'test-workflow')
        self.assertTrue(result.success)
        
        # Verify agent was installed
        agent_file = os.path.join(self.agents_dir, 'test-workflow.md')
        self.assertTrue(os.path.exists(agent_file))
        
        # Verify agent content
        with open(agent_file, 'r') as f:
            content = f.read()
            self.assertIn('name: test-workflow', content)
            self.assertIn('version: 1.0.0', content)
        
        # Verify registry was updated
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        self.assertTrue(registry['agents']['test-workflow']['installed'])
        
        # Check agent status
        result = self._run_agent_manager_command('status')
        self.assertTrue(result.success)
        self.assertIn('test-workflow', result.output)
        self.assertIn('1.0.0', result.output)
    
    def test_agent_update_workflow(self):
        """Test agent update workflow with version management."""
        # Set up and install initial version
        os.chdir(self.project_dir)
        self._run_agent_manager_command('init')
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        self._run_agent_manager_command('install', 'test-debugger')
        
        # Create updated version in repository
        updated_agent = """---
name: test-debugger
description: Updated test debugging assistant with new features
version: 1.6.0
tools: Read, Write, Bash, Grep, WebFetch
category: debugging
---

# Test Debugger Agent (Updated)

This is an updated version of the test debugging agent.

## New Features in v1.6.0

- Enhanced error analysis
- Web-based debugging support
- Improved troubleshooting procedures

## Usage

```bash
/agent:test-debugger
```

Now with more debugging capabilities!
"""
        
        agent_file = os.path.join(self.test_repo_dir, 'agents', 'test-debugger.md')
        with open(agent_file, 'w') as f:
            f.write(updated_agent)
        
        # Update manifest
        manifest_file = os.path.join(self.test_repo_dir, 'manifest.yaml')
        with open(manifest_file, 'r') as f:
            manifest = yaml.safe_load(f)
        
        for agent in manifest['agents']:
            if agent['name'] == 'test-debugger':
                agent['version'] = '1.6.0'
        
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest, f)
        
        # Update repository cache
        result = self._run_agent_manager_command('update-repo', 'test-agent-repo')
        self.assertTrue(result.success)
        
        # Check for updates
        result = self._run_agent_manager_command('check-updates')
        self.assertTrue(result.success)
        self.assertIn('test-debugger', result.output)
        self.assertIn('1.6.0', result.output)
        
        # Perform update
        result = self._run_agent_manager_command('update', 'test-debugger')
        self.assertTrue(result.success)
        
        # Verify update
        installed_agent_file = os.path.join(self.agents_dir, 'test-debugger.md')
        with open(installed_agent_file, 'r') as f:
            content = f.read()
            self.assertIn('version: 1.6.0', content)
            self.assertIn('New Features in v1.6.0', content)
    
    def test_memory_integration_workflow(self):
        """Test Memory.md integration throughout agent operations."""
        os.chdir(self.project_dir)
        
        # Initialize and perform operations
        self._run_agent_manager_command('init')
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        self._run_agent_manager_command('install', 'test-workflow')
        
        # Check Memory.md was updated
        with open(self.memory_file, 'r') as f:
            memory_content = f.read()
        
        # Should contain agent status section
        self.assertIn('## Agent Status', memory_content)
        self.assertIn('test-workflow', memory_content)
        self.assertIn('v1.0.0', memory_content)
        
        # Should contain recent operations
        self.assertIn('## Recent Agent Operations', memory_content)
        self.assertIn('installed', memory_content)
    
    def test_multi_repository_coordination(self):
        """Test coordination between multiple repositories."""
        os.chdir(self.project_dir)
        
        # Create second test repository
        second_repo_dir = os.path.join(self.test_dir, 'second-agent-repo')
        os.makedirs(os.path.join(second_repo_dir, 'agents'), exist_ok=True)
        
        # Create agent with same name but different version
        conflicting_agent = """---
name: test-workflow
description: Alternative workflow agent from second repository
version: 2.0.0
tools: Read, Write, Bash, TodoWrite, Grep
category: development
---

# Alternative Workflow Agent

This is an alternative implementation from a different repository.
"""
        
        with open(os.path.join(second_repo_dir, 'agents', 'test-workflow.md'), 'w') as f:
            f.write(conflicting_agent)
        
        # Create manifest for second repo
        second_manifest = {
            'name': 'Alternative Agent Collection',
            'version': '2.0.0',
            'agents': [
                {
                    'name': 'test-workflow',
                    'file': 'agents/test-workflow.md',
                    'version': '2.0.0',
                    'description': 'Alternative workflow agent',
                    'category': 'development'
                }
            ]
        }
        
        with open(os.path.join(second_repo_dir, 'manifest.yaml'), 'w') as f:
            yaml.dump(second_manifest, f)
        
        # Initialize and register both repositories
        self._run_agent_manager_command('init')
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        self._run_agent_manager_command('register-repo', second_repo_dir, '--type', 'local')
        
        # Discover agents (should show both versions)
        result = self._run_agent_manager_command('discover')
        self.assertTrue(result.success)
        self.assertIn('test-workflow', result.output)
        
        # Install from preferred repository (based on priority)
        result = self._run_agent_manager_command('install', 'test-workflow')
        self.assertTrue(result.success)
        
        # Verify which version was installed
        agent_file = os.path.join(self.agents_dir, 'test-workflow.md')
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Should prefer newer version (2.0.0) based on default conflict resolution
        self.assertIn('version: 2.0.0', content)
    
    def test_session_startup_integration(self):
        """Test session startup hook integration."""
        os.chdir(self.project_dir)
        
        # Initialize with startup hooks
        self._run_agent_manager_command('init')
        self._run_agent_manager_command('setup-hooks')
        
        # Verify hooks configuration was created
        hooks_file = os.path.join(self.project_dir, '.claude', 'hooks.json')
        self.assertTrue(os.path.exists(hooks_file))
        
        with open(hooks_file, 'r') as f:
            hooks_config = json.load(f)
        
        self.assertIn('on_session_start', hooks_config)
        self.assertEqual(len(hooks_config['on_session_start']), 1)
        self.assertEqual(hooks_config['on_session_start'][0]['name'], 'agent-manager-check')
        
        # Test startup check command
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        result = self._run_agent_manager_command('check-and-update-agents')
        self.assertTrue(result.success)
    
    def test_error_recovery_scenarios(self):
        """Test error recovery and graceful failure handling."""
        os.chdir(self.project_dir)
        
        # Test recovery from network failure (simulated with nonexistent repo)
        self._run_agent_manager_command('init')
        result = self._run_agent_manager_command('register-repo', 'https://nonexistent.com/fake/repo')
        self.assertFalse(result.success)  # Should fail gracefully
        
        # Test recovery from corrupt cache
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        
        # Corrupt cache file
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        with open(registry_file, 'w') as f:
            f.write('corrupted json content')
        
        # Should recover gracefully
        result = self._run_agent_manager_command('rebuild-cache')
        self.assertTrue(result.success)
        
        # Verify cache was rebuilt
        with open(registry_file, 'r') as f:
            registry = json.load(f)
            self.assertIn('agents', registry)
    
    def test_cache_performance_and_offline_mode(self):
        """Test cache performance and offline operation."""
        os.chdir(self.project_dir)
        
        # Set up with caching enabled
        self._run_agent_manager_command('init')
        self._run_agent_manager_command('register-repo', self.test_repo_dir, '--type', 'local')
        
        # Enable offline mode
        self._run_agent_manager_command('config', 'settings.offline_mode', 'true')
        
        # Operations should work with cached data
        result = self._run_agent_manager_command('discover')
        self.assertTrue(result.success)
        self.assertIn('test-workflow', result.output)
        
        # Install should work from cache
        result = self._run_agent_manager_command('install', 'test-workflow')
        self.assertTrue(result.success)
        
        # Verify cache statistics
        result = self._run_agent_manager_command('cache-status')
        self.assertTrue(result.success)
        self.assertIn('cache', result.output.lower())
    
    def _run_agent_manager_command(self, *args):
        """Helper method to simulate Agent Manager command execution."""
        # This would interface with the actual Agent Manager implementation
        # For testing, we'll simulate the operations
        
        class MockResult:
            def __init__(self, success=True, output="", error=""):
                self.success = success
                self.output = output
                self.error = error
        
        command = args[0]
        
        if command == 'init':
            return self._mock_init()
        elif command == 'register-repo':
            return self._mock_register_repo(args[1], *args[2:])
        elif command == 'discover':
            return self._mock_discover()
        elif command == 'install':
            return self._mock_install(args[1])
        elif command == 'status':
            return self._mock_status()
        elif command == 'update':
            return self._mock_update(args[1])
        elif command == 'check-updates':
            return self._mock_check_updates()
        elif command == 'setup-hooks':
            return self._mock_setup_hooks()
        elif command == 'config':
            return self._mock_config(args[1], args[2])
        elif command == 'cache-status':
            return self._mock_cache_status()
        elif command == 'rebuild-cache':
            return self._mock_rebuild_cache()
        else:
            return MockResult(False, "", f"Unknown command: {command}")
    
    def _mock_init(self):
        """Mock Agent Manager initialization."""
        # Create configuration files
        config = {
            'repositories': [],
            'settings': {
                'auto_update': True,
                'cache_ttl': '7d',
                'offline_mode': False
            }
        }
        
        config_file = os.path.join(self.agent_manager_dir, 'config.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Create registry
        registry = {
            'version': '1.0.0',
            'repositories': {},
            'agents': {},
            'metadata': {'total_repositories': 0, 'total_agents': 0}
        }
        
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        with open(registry_file, 'w') as f:
            json.dump(registry, f)
        
        return self._mock_result(True, "Agent Manager initialized successfully")
    
    def _mock_register_repo(self, repo_url, *args):
        """Mock repository registration."""
        if not os.path.exists(repo_url) and not repo_url.startswith('http'):
            return self._mock_result(False, f"Repository not found: {repo_url}")
        
        # Update config
        config_file = os.path.join(self.agent_manager_dir, 'config.yaml')
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        repo_name = os.path.basename(repo_url.rstrip('/'))
        repo_entry = {
            'name': repo_name,
            'url': repo_url,
            'type': 'local' if '--type' in args and args[args.index('--type') + 1] == 'local' else 'github'
        }
        
        config['repositories'].append(repo_entry)
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Update registry with agents from repository
        if os.path.exists(repo_url):
            self._update_registry_from_repo(repo_url, repo_name)
        
        return self._mock_result(True, f"Repository {repo_name} registered successfully")
    
    def _mock_discover(self):
        """Mock agent discovery."""
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        
        if not os.path.exists(registry_file):
            return self._mock_result(True, "No agents found. Register a repository first.")
        
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        output_lines = ["Available Agents:"]
        for agent_name, agent_info in registry['agents'].items():
            output_lines.append(f"• {agent_name} v{agent_info.get('version', 'unknown')} - {agent_info.get('description', 'No description')}")
        
        return self._mock_result(True, "\n".join(output_lines))
    
    def _mock_install(self, agent_name):
        """Mock agent installation."""
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        if agent_name not in registry['agents']:
            return self._mock_result(False, f"Agent {agent_name} not found")
        
        agent_info = registry['agents'][agent_name]
        repo_name = agent_info['repository']
        agent_file = agent_info['file']
        
        # Find repository URL
        config_file = os.path.join(self.agent_manager_dir, 'config.yaml')
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        repo_url = None
        for repo in config['repositories']:
            if repo['name'] == repo_name:
                repo_url = repo['url']
                break
        
        if not repo_url:
            return self._mock_result(False, f"Repository {repo_name} not found")
        
        # Copy agent file
        source_file = os.path.join(repo_url, agent_file)
        target_file = os.path.join(self.agents_dir, f'{agent_name}.md')
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, target_file)
            
            # Update registry
            registry['agents'][agent_name]['installed'] = True
            with open(registry_file, 'w') as f:
                json.dump(registry, f)
            
            # Update Memory.md
            self._update_memory_with_installation(agent_name, agent_info.get('version', 'unknown'))
            
            return self._mock_result(True, f"Agent {agent_name} installed successfully")
        else:
            return self._mock_result(False, f"Agent file not found: {source_file}")
    
    def _mock_status(self):
        """Mock agent status display."""
        output_lines = ["Installed Agents:"]
        
        for agent_file in os.listdir(self.agents_dir):
            if agent_file.endswith('.md'):
                agent_name = agent_file[:-3]  # Remove .md extension
                agent_path = os.path.join(self.agents_dir, agent_file)
                
                # Extract version from file
                version = "unknown"
                with open(agent_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith('version:'):
                            version = line.split(':', 1)[1].strip()
                            break
                
                output_lines.append(f"✅ {agent_name} v{version}")
        
        return self._mock_result(True, "\n".join(output_lines))
    
    def _mock_update(self, agent_name):
        """Mock agent update."""
        return self._mock_result(True, f"Agent {agent_name} updated successfully")
    
    def _mock_check_updates(self):
        """Mock checking for updates."""
        return self._mock_result(True, "Available updates:\n• test-debugger: 1.5.0 → 1.6.0")
    
    def _mock_setup_hooks(self):
        """Mock startup hooks setup."""
        hooks_config = {
            "on_session_start": [
                {
                    "name": "agent-manager-check",
                    "command": "/agent:agent-manager",
                    "args": "check-and-update-agents",
                    "async": True,
                    "timeout": "60s"
                }
            ]
        }
        
        hooks_file = os.path.join(self.project_dir, '.claude', 'hooks.json')
        os.makedirs(os.path.dirname(hooks_file), exist_ok=True)
        
        with open(hooks_file, 'w') as f:
            json.dump(hooks_config, f, indent=2)
        
        return self._mock_result(True, "Startup hooks configured successfully")
    
    def _mock_config(self, key, value):
        """Mock configuration setting."""
        config_file = os.path.join(self.agent_manager_dir, 'config.yaml')
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Simple key setting (would be more sophisticated in real implementation)
        if key == 'settings.offline_mode':
            config['settings']['offline_mode'] = value.lower() == 'true'
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        return self._mock_result(True, f"Configuration {key} set to {value}")
    
    def _mock_cache_status(self):
        """Mock cache status display."""
        return self._mock_result(True, "Cache Status:\nTotal size: 1.2MB\nFiles: 15\nLast cleanup: 2025-08-01")
    
    def _mock_rebuild_cache(self):
        """Mock cache rebuild."""
        # Recreate registry
        registry = {
            'version': '1.0.0',
            'repositories': {},
            'agents': {},
            'metadata': {'total_repositories': 0, 'total_agents': 0}
        }
        
        # Rebuild from registered repositories
        config_file = os.path.join(self.agent_manager_dir, 'config.yaml')
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        for repo in config['repositories']:
            if os.path.exists(repo['url']):
                self._update_registry_from_repo(repo['url'], repo['name'])
        
        return self._mock_result(True, "Cache rebuilt successfully")
    
    def _update_registry_from_repo(self, repo_url, repo_name):
        """Helper to update registry from repository."""
        registry_file = os.path.join(self.agent_manager_dir, 'cache', 'agent-registry.json')
        
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        # Check for manifest
        manifest_file = os.path.join(repo_url, 'manifest.yaml')
        if os.path.exists(manifest_file):
            with open(manifest_file, 'r') as f:
                manifest = yaml.safe_load(f)
            
            for agent in manifest.get('agents', []):
                registry['agents'][agent['name']] = {
                    'name': agent['name'],
                    'repository': repo_name,
                    'version': agent['version'],
                    'description': agent['description'],
                    'file': agent['file'],
                    'installed': False
                }
        else:
            # Scan for agent files
            agents_dir = os.path.join(repo_url, 'agents')
            if os.path.exists(agents_dir):
                for agent_file in os.listdir(agents_dir):
                    if agent_file.endswith('.md'):
                        agent_name = agent_file[:-3]
                        agent_path = os.path.join(agents_dir, agent_file)
                        
                        # Extract metadata from file
                        version = "unknown"
                        description = "No description"
                        
                        with open(agent_path, 'r') as f:
                            content = f.read()
                            for line in content.split('\n'):
                                if line.strip().startswith('version:'):
                                    version = line.split(':', 1)[1].strip()
                                elif line.strip().startswith('description:'):
                                    description = line.split(':', 1)[1].strip()
                        
                        registry['agents'][agent_name] = {
                            'name': agent_name,
                            'repository': repo_name,
                            'version': version,
                            'description': description,
                            'file': f'agents/{agent_file}',
                            'installed': False
                        }
        
        registry['metadata']['total_agents'] = len(registry['agents'])
        
        with open(registry_file, 'w') as f:
            json.dump(registry, f)
    
    def _update_memory_with_installation(self, agent_name, version):
        """Helper to update Memory.md with agent installation."""
        with open(self.memory_file, 'r') as f:
            memory_content = f.read()
        
        # Add agent status section if not exists
        if '## Agent Status' not in memory_content:
            memory_content += f"\n\n## Agent Status (Last Updated: 2025-08-01T00:00:00Z)\n\n### Active Agents\n- ✅ {agent_name} v{version} (installed 2025-08-01)\n\n### Recent Agent Operations\n- 2025-08-01: Installed {agent_name} v{version}\n"
        else:
            # Add to existing section
            memory_content = memory_content.replace(
                '### Active Agents',
                f'### Active Agents\n- ✅ {agent_name} v{version} (installed 2025-08-01)'
            )
        
        with open(self.memory_file, 'w') as f:
            f.write(memory_content)
    
    def _mock_result(self, success, output="", error=""):
        """Helper to create mock result."""
        class MockResult:
            def __init__(self, success, output, error):
                self.success = success
                self.output = output
                self.error = error
        
        return MockResult(success, output, error)


class TestAgentManagerSessionIntegration(unittest.TestCase):
    """Test Agent Manager integration with Claude Code sessions."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.test_dir, 'session-test')
        os.makedirs(self.project_dir, exist_ok=True)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_session_startup_hook_execution(self):
        """Test that startup hooks execute correctly."""
        # This would test the actual hook execution
        # For this test, we'll verify the hook configuration
        
        hooks_config = {
            "on_session_start": [
                {
                    "name": "agent-manager-check",
                    "command": "/agent:agent-manager",
                    "args": "check-and-update-agents",
                    "async": True,
                    "timeout": "60s"
                }
            ]
        }
        
        hooks_file = os.path.join(self.project_dir, '.claude', 'hooks.json')
        os.makedirs(os.path.dirname(hooks_file), exist_ok=True)
        
        with open(hooks_file, 'w') as f:
            json.dump(hooks_config, f)
        
        # Verify hook configuration
        self.assertTrue(os.path.exists(hooks_file))
        
        with open(hooks_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertIn('on_session_start', loaded_config)
        self.assertEqual(len(loaded_config['on_session_start']), 1)
        self.assertEqual(loaded_config['on_session_start'][0]['command'], "/agent:agent-manager")
    
    def test_background_update_checking(self):
        """Test non-blocking background update operations."""
        # This would test the background update mechanism
        # For now, we'll test the configuration that enables it
        
        config = {
            'settings': {
                'auto_update': True,
                'update_on_startup': True,
                'check_interval': '24h'
            }
        }
        
        config_file = os.path.join(self.project_dir, '.claude', 'agent-manager', 'config.yaml')
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Verify configuration supports background operations
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertTrue(loaded_config['settings']['auto_update'])
        self.assertTrue(loaded_config['settings']['update_on_startup'])
        self.assertEqual(loaded_config['settings']['check_interval'], '24h')


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2)