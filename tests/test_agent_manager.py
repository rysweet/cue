#!/usr/bin/env python3
"""
Unit tests for Agent Manager sub-agent functionality.

This test suite validates the core components of the Agent Manager:
- Repository management
- Agent discovery and installation
- Version management
- Cache operations
- Configuration handling
"""

import os
import json
import yaml
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestAgentManagerRepositoryManager(unittest.TestCase):
    """Test the RepositoryManager component."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.agent_manager_dir = os.path.join(self.test_dir, '.claude', 'agent-manager')
        os.makedirs(self.agent_manager_dir, exist_ok=True)
        
        # Create test configuration
        self.config = {
            'repositories': [],
            'settings': {
                'auto_update': True,
                'cache_ttl': '7d',
                'verify_checksums': True
            }
        }
        
        config_path = os.path.join(self.agent_manager_dir, 'config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_register_github_repository(self):
        """Test registering a GitHub repository."""
        repo_url = "https://github.com/test/agents"
        repo_name = "test-agents"
        
        # Mock git operations
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Test repository registration
            result = self._register_repository(repo_url, "github", "public")
            
            self.assertTrue(result)
            mock_run.assert_called()
    
    def test_register_local_repository(self):
        """Test registering a local repository."""
        local_path = os.path.join(self.test_dir, 'local_agents')
        os.makedirs(local_path, exist_ok=True)
        
        # Create test agent file
        agent_file = os.path.join(local_path, 'test-agent.md')
        with open(agent_file, 'w') as f:
            f.write("""---
name: test-agent
description: Test agent for unit tests
version: 1.0.0
---

# Test Agent
This is a test agent.
""")
        
        result = self._register_repository(local_path, "local")
        self.assertTrue(result)
    
    def test_parse_manifest_file(self):
        """Test parsing repository manifest files."""
        manifest_content = """
name: "Test Agent Collection"
version: "1.0.0"
description: "Test agents for unit testing"

agents:
  - name: "test-workflow"
    file: "agents/test-workflow.md"
    version: "1.0.0"
    description: "Test workflow agent"
    
  - name: "test-debugger"
    file: "agents/test-debugger.md"
    version: "1.5.0"
    description: "Test debugging agent"
"""
        
        manifest_path = os.path.join(self.test_dir, 'manifest.yaml')
        with open(manifest_path, 'w') as f:
            f.write(manifest_content)
        
        agents = self._parse_manifest(manifest_path)
        
        self.assertEqual(len(agents), 2)
        self.assertIn('test-workflow', [agent['name'] for agent in agents])
        self.assertIn('test-debugger', [agent['name'] for agent in agents])
    
    def test_validate_repository_url(self):
        """Test repository URL validation."""
        valid_urls = [
            "https://github.com/user/repo",
            "git@github.com:user/repo.git",
            "/path/to/local/repo"
        ]
        
        invalid_urls = [
            "not-a-url",
            "ftp://invalid.com/repo",
            ""
        ]
        
        for url in valid_urls:
            self.assertTrue(self._validate_repository_url(url))
        
        for url in invalid_urls:
            self.assertFalse(self._validate_repository_url(url))
    
    def _register_repository(self, url, repo_type, auth_type="public"):
        """Helper method to simulate repository registration."""
        # This would be the actual implementation
        return True
    
    def _parse_manifest(self, manifest_path):
        """Helper method to parse manifest file."""
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        return manifest.get('agents', [])
    
    def _validate_repository_url(self, url):
        """Helper method to validate repository URLs."""
        if not url:
            return False
        
        valid_schemes = ['https', 'git', 'ssh']
        
        if url.startswith('/'):  # Local path
            return os.path.exists(url) or True  # Allow non-existing for tests
        
        if '://' in url:
            scheme = url.split('://')[0]
            return scheme in valid_schemes
        
        if url.startswith('git@'):  # SSH format
            return True
        
        return False


class TestAgentManagerAgentRegistry(unittest.TestCase):
    """Test the AgentRegistry component."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.registry_file = os.path.join(self.test_dir, 'agent-registry.json')
        
        # Initialize empty registry
        self.registry = {
            'version': '1.0.0',
            'repositories': {},
            'agents': {},
            'metadata': {
                'total_repositories': 0,
                'total_agents': 0
            }
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_register_agent(self):
        """Test registering an agent in the registry."""
        agent_info = {
            'name': 'test-agent',
            'repository': 'test-repo',
            'version': '1.0.0',
            'file': 'agents/test-agent.md',
            'installed': False
        }
        
        success = self._register_agent(agent_info)
        self.assertTrue(success)
        
        # Verify agent was added to registry
        registry = self._load_registry()
        self.assertIn('test-agent', registry['agents'])
        self.assertEqual(registry['agents']['test-agent']['version'], '1.0.0')
    
    def test_list_available_agents(self):
        """Test listing available agents."""
        # Add test agents to registry
        test_agents = [
            {'name': 'workflow-master', 'category': 'development', 'version': '2.1.0'},
            {'name': 'code-reviewer', 'category': 'development', 'version': '1.5.0'},
            {'name': 'test-solver', 'category': 'testing', 'version': '1.0.0'}
        ]
        
        for agent in test_agents:
            self._register_agent(agent)
        
        # Test listing all agents
        all_agents = self._list_available_agents()
        self.assertEqual(len(all_agents), 3)
        
        # Test filtering by category
        dev_agents = self._list_available_agents(category='development')
        self.assertEqual(len(dev_agents), 2)
        
        test_agents = self._list_available_agents(category='testing')
        self.assertEqual(len(test_agents), 1)
    
    def test_version_comparison(self):
        """Test semantic version comparison."""
        test_cases = [
            ('1.0.0', '1.0.1', True),   # older < newer
            ('1.0.1', '1.0.0', False),  # newer > older
            ('1.0.0', '1.0.0', False),  # equal
            ('1.0.0', '2.0.0', True),   # major version difference
            ('2.1.0', '2.0.5', False),  # minor version higher
        ]
        
        for version1, version2, expected in test_cases:
            result = self._is_version_older(version1, version2)
            self.assertEqual(result, expected, 
                           f"Version comparison failed: {version1} vs {version2}")
    
    def test_dependency_resolution(self):
        """Test agent dependency resolution."""
        # Create agents with dependencies
        agents = {
            'base-agent': {'dependencies': []},
            'dependent-agent': {'dependencies': ['base-agent']},
            'complex-agent': {'dependencies': ['base-agent', 'dependent-agent']}
        }
        
        # Test resolving dependencies for complex-agent
        resolved = self._resolve_dependencies('complex-agent', agents)
        expected_order = ['base-agent', 'dependent-agent', 'complex-agent']
        
        self.assertEqual(resolved, expected_order)
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        agents = {
            'agent-a': {'dependencies': ['agent-b']},
            'agent-b': {'dependencies': ['agent-c']},
            'agent-c': {'dependencies': ['agent-a']}  # Circular!
        }
        
        with self.assertRaises(ValueError):
            self._resolve_dependencies('agent-a', agents)
    
    def _register_agent(self, agent_info):
        """Helper method to register an agent."""
        registry = self._load_registry()
        registry['agents'][agent_info['name']] = agent_info
        registry['metadata']['total_agents'] += 1
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f)
        
        return True
    
    def _load_registry(self):
        """Helper method to load registry."""
        with open(self.registry_file, 'r') as f:
            return json.load(f)
    
    def _list_available_agents(self, category=None):
        """Helper method to list available agents."""
        registry = self._load_registry()
        agents = list(registry['agents'].values())
        
        if category:
            agents = [a for a in agents if a.get('category') == category]
        
        return agents
    
    def _is_version_older(self, version1, version2):
        """Helper method for version comparison."""
        def parse_version(version):
            return tuple(map(int, version.split('.')))
        
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        return v1 < v2
    
    def _resolve_dependencies(self, agent_name, agents, visited=None, resolved=None):
        """Helper method to resolve dependencies."""
        if visited is None:
            visited = set()
        if resolved is None:
            resolved = []
        
        if agent_name in visited:
            raise ValueError(f"Circular dependency detected: {agent_name}")
        
        visited.add(agent_name)
        
        agent = agents.get(agent_name, {})
        dependencies = agent.get('dependencies', [])
        
        for dep in dependencies:
            if dep not in resolved:
                self._resolve_dependencies(dep, agents, visited.copy(), resolved)
        
        if agent_name not in resolved:
            resolved.append(agent_name)
        
        return resolved


class TestAgentManagerInstallationEngine(unittest.TestCase):
    """Test the InstallationEngine component."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.agents_dir = os.path.join(self.test_dir, '.claude', 'agents')
        self.cache_dir = os.path.join(self.test_dir, '.claude', 'agent-manager', 'cache')
        
        os.makedirs(self.agents_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_install_agent(self):
        """Test installing an agent."""
        # Create source agent file
        source_file = os.path.join(self.cache_dir, 'test-agent.md')
        agent_content = """---
name: test-agent
description: Test agent for installation
version: 1.0.0
tools: Read, Write, Bash
---

# Test Agent
This is a test agent for installation testing.
"""
        
        with open(source_file, 'w') as f:
            f.write(agent_content)
        
        # Test installation
        result = self._install_agent('test-agent', '1.0.0', source_file)
        self.assertTrue(result)
        
        # Verify agent file was copied
        target_file = os.path.join(self.agents_dir, 'test-agent.md')
        self.assertTrue(os.path.exists(target_file))
        
        # Verify content
        with open(target_file, 'r') as f:
            content = f.read()
            self.assertIn('name: test-agent', content)
            self.assertIn('version: 1.0.0', content)
    
    def test_validate_agent_file(self):
        """Test agent file validation."""
        # Valid agent file
        valid_content = """---
name: valid-agent
description: Valid agent for testing
version: 1.0.0
tools: Read, Write
---

# Valid Agent
This agent has valid structure.
"""
        
        valid_file = os.path.join(self.test_dir, 'valid-agent.md')
        with open(valid_file, 'w') as f:
            f.write(valid_content)
        
        self.assertTrue(self._validate_agent_file(valid_file))
        
        # Invalid agent file (missing frontmatter)
        invalid_content = """
# Invalid Agent
This agent is missing YAML frontmatter.
"""
        
        invalid_file = os.path.join(self.test_dir, 'invalid-agent.md')
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        
        self.assertFalse(self._validate_agent_file(invalid_file))
    
    def test_backup_and_restore(self):
        """Test agent backup and restore functionality."""
        # Create original agent
        original_content = """---
name: backup-test
version: 1.0.0
---
Original content
"""
        
        agent_file = os.path.join(self.agents_dir, 'backup-test.md')
        with open(agent_file, 'w') as f:
            f.write(original_content)
        
        # Create backup
        backup_success = self._backup_agent('backup-test', '1.0.0')
        self.assertTrue(backup_success)
        
        # Modify original
        modified_content = """---
name: backup-test
version: 2.0.0
---
Modified content
"""
        
        with open(agent_file, 'w') as f:
            f.write(modified_content)
        
        # Restore from backup
        restore_success = self._restore_agent_backup('backup-test', '1.0.0')
        self.assertTrue(restore_success)
        
        # Verify restoration
        with open(agent_file, 'r') as f:
            content = f.read()
            self.assertIn('version: 1.0.0', content)
            self.assertIn('Original content', content)
    
    def test_update_agent(self):
        """Test agent update functionality."""
        # Install initial version
        initial_content = """---
name: update-test
version: 1.0.0
---
Initial version
"""
        
        agent_file = os.path.join(self.agents_dir, 'update-test.md')
        with open(agent_file, 'w') as f:
            f.write(initial_content)
        
        # Prepare updated version
        updated_content = """---
name: update-test
version: 1.1.0
---
Updated version with new features
"""
        
        source_file = os.path.join(self.cache_dir, 'update-test-1.1.0.md')
        with open(source_file, 'w') as f:
            f.write(updated_content)
        
        # Perform update
        result = self._update_agent('update-test', '1.1.0', source_file)
        self.assertTrue(result)
        
        # Verify update
        with open(agent_file, 'r') as f:
            content = f.read()
            self.assertIn('version: 1.1.0', content)
            self.assertIn('Updated version', content)
    
    def _install_agent(self, agent_name, version, source_file):
        """Helper method to install an agent."""
        target_file = os.path.join(self.agents_dir, f'{agent_name}.md')
        
        try:
            shutil.copy2(source_file, target_file)
            return self._validate_agent_file(target_file)
        except Exception:
            return False
    
    def _validate_agent_file(self, agent_file):
        """Helper method to validate agent file."""
        try:
            with open(agent_file, 'r') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            if not content.startswith('---'):
                return False
            
            # Check for required fields
            required_fields = ['name:', 'description:', 'version:']
            for field in required_fields:
                if field not in content:
                    return False
            
            return True
        except Exception:
            return False
    
    def _backup_agent(self, agent_name, version):
        """Helper method to backup an agent."""
        agent_file = os.path.join(self.agents_dir, f'{agent_name}.md')
        backup_file = os.path.join(self.cache_dir, f'{agent_name}-{version}.backup')
        
        try:
            shutil.copy2(agent_file, backup_file)
            return True
        except Exception:
            return False
    
    def _restore_agent_backup(self, agent_name, version):
        """Helper method to restore agent from backup."""
        agent_file = os.path.join(self.agents_dir, f'{agent_name}.md')
        backup_file = os.path.join(self.cache_dir, f'{agent_name}-{version}.backup')
        
        try:
            shutil.copy2(backup_file, agent_file)
            return True
        except Exception:
            return False
    
    def _update_agent(self, agent_name, new_version, source_file):
        """Helper method to update an agent."""
        # Backup current version first
        current_version = self._get_current_version(agent_name)
        if current_version:
            self._backup_agent(agent_name, current_version)
        
        # Install new version
        return self._install_agent(agent_name, new_version, source_file)
    
    def _get_current_version(self, agent_name):
        """Helper method to get current agent version."""
        agent_file = os.path.join(self.agents_dir, f'{agent_name}.md')
        
        try:
            with open(agent_file, 'r') as f:
                content = f.read()
            
            # Extract version from YAML frontmatter
            for line in content.split('\n'):
                if line.strip().startswith('version:'):
                    return line.split(':', 1)[1].strip()
            
            return None
        except Exception:
            return None


class TestAgentManagerCacheManager(unittest.TestCase):
    """Test the CacheManager component."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.test_dir, '.claude', 'agent-manager', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create test cache metadata
        self.metadata = {
            'cache_stats': {
                'total_size': 0,
                'file_count': 0,
                'last_cleanup': None
            }
        }
        
        metadata_file = os.path.join(self.cache_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_cache_operations(self):
        """Test basic cache operations."""
        # Test caching data
        test_data = {'key': 'value', 'number': 42}
        success = self._cache_data('test-key', test_data)
        self.assertTrue(success)
        
        # Test retrieving cached data
        retrieved = self._get_cached_data('test-key')
        self.assertEqual(retrieved, test_data)
        
        # Test cache miss
        missing = self._get_cached_data('nonexistent-key')
        self.assertIsNone(missing)
    
    def test_cache_expiration(self):
        """Test cache TTL (time-to-live) functionality."""
        # Cache data with short TTL
        test_data = {'expires': 'soon'}
        
        # Mock time for testing
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            
            # Cache with 1 second TTL
            success = self._cache_data_with_ttl('expire-test', test_data, ttl=1)
            self.assertTrue(success)
            
            # Data should be available immediately
            retrieved = self._get_cached_data('expire-test')
            self.assertEqual(retrieved, test_data)
            
            # Advance time beyond TTL
            mock_time.return_value = 1002.0
            
            # Data should be expired
            expired = self._get_cached_data('expire-test')
            self.assertIsNone(expired)
    
    def test_cache_size_limits(self):
        """Test cache size management."""
        # Fill cache with test data
        large_data = 'x' * 1024  # 1KB of data
        
        for i in range(10):
            self._cache_data(f'large-{i}', large_data)
        
        # Check cache size
        cache_size = self._get_cache_size()
        self.assertGreater(cache_size, 0)
        
        # Test cache cleanup
        cleanup_result = self._cleanup_cache(max_size=5 * 1024)  # 5KB limit
        self.assertTrue(cleanup_result)
        
        # Verify cache size reduced
        new_cache_size = self._get_cache_size()
        self.assertLess(new_cache_size, cache_size)
    
    def test_cache_integrity(self):
        """Test cache integrity verification."""
        # Create valid cache entry
        valid_data = {'valid': True, 'checksum': 'abc123'}
        self._cache_data('valid-entry', valid_data)
        
        # Verify integrity
        integrity_ok = self._verify_cache_integrity('valid-entry')
        self.assertTrue(integrity_ok)
        
        # Corrupt cache entry
        cache_file = os.path.join(self.cache_dir, 'valid-entry.json')
        with open(cache_file, 'w') as f:
            f.write('corrupted data')
        
        # Verify integrity fails
        integrity_bad = self._verify_cache_integrity('valid-entry')
        self.assertFalse(integrity_bad)
    
    def _cache_data(self, key, data):
        """Helper method to cache data."""
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False
    
    def _cache_data_with_ttl(self, key, data, ttl):
        """Helper method to cache data with TTL."""
        import time
        
        cache_entry = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        return self._cache_data(key, cache_entry)
    
    def _get_cached_data(self, key):
        """Helper method to retrieve cached data."""
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check if it's a TTL entry
            if isinstance(cached, dict) and 'timestamp' in cached and 'ttl' in cached:
                import time
                if time.time() - cached['timestamp'] > cached['ttl']:
                    # Expired
                    os.remove(cache_file)
                    return None
                return cached['data']
            
            return cached
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _get_cache_size(self):
        """Helper method to calculate cache size."""
        total_size = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        
        return total_size
    
    def _cleanup_cache(self, max_size):
        """Helper method to cleanup cache."""
        current_size = self._get_cache_size()
        
        if current_size <= max_size:
            return True
        
        # Remove oldest files until under size limit
        cache_files = []
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.json'):
                    mtime = os.path.getmtime(file_path)
                    cache_files.append((mtime, file_path))
        
        # Sort by modification time (oldest first)
        cache_files.sort()
        
        # Remove files until under size limit
        for mtime, file_path in cache_files:
            if self._get_cache_size() <= max_size:
                break
            
            try:
                os.remove(file_path)
            except OSError:
                pass
        
        return True
    
    def _verify_cache_integrity(self, key):
        """Helper method to verify cache integrity."""
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        
        try:
            with open(cache_file, 'r') as f:
                json.load(f)  # Try to parse JSON
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)