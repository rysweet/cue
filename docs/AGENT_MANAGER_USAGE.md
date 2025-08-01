# Agent Manager Usage Guide

The Agent Manager sub-agent provides comprehensive management of external Claude Code agents from centralized repositories. This guide covers installation, configuration, and daily usage.

## Quick Start

### 1. Initialize Agent Manager
```bash
/agent:agent-manager init
```

This command:
- Creates necessary directory structure
- Sets up configuration files
- Configures startup hooks
- Prompts for initial repository registration

### 2. Register Your First Repository
```bash
# Public repository
/agent:agent-manager register-repo https://github.com/claude-community/agents

# Private repository with token
/agent:agent-manager register-repo https://github.com/company/private-agents --auth token

# Local development repository
/agent:agent-manager register-repo /path/to/local/agents --type local
```

### 3. Discover Available Agents
```bash
# List all available agents
/agent:agent-manager discover

# Search by category
/agent:agent-manager discover --category development

# Search by keywords
/agent:agent-manager search testing
```

### 4. Install Agents
```bash
# Install latest version
/agent:agent-manager install advanced-debugger

# Install specific version
/agent:agent-manager install workflow-master@2.1.0

# Install all agents in a category
/agent:agent-manager install --category development
```

## Repository Management

### Registering Repositories

#### GitHub Repositories
```bash
# Public repository
/agent:agent-manager register-repo https://github.com/username/repo

# Private repository with personal access token
export GITHUB_TOKEN="your_token_here"
/agent:agent-manager register-repo https://github.com/company/private-repo --auth token

# Repository with SSH access
/agent:agent-manager register-repo git@github.com:company/repo.git --auth ssh
```

#### Local Repositories
```bash
# Local directory
/agent:agent-manager register-repo /home/user/my-agents --type local

# Network share
/agent:agent-manager register-repo /mnt/shared/team-agents --type local
```

### Repository Configuration

Repositories can be configured with priorities and update settings:

```yaml
# .claude/agent-manager/config.yaml
repositories:
  - name: "primary-agents"
    url: "https://github.com/company/agents"
    type: "github"
    priority: 1        # Higher priority = preferred for conflicts
    auto_update: true  # Update automatically
    
  - name: "community-agents"
    url: "https://github.com/community/agents"
    type: "github"
    priority: 2
    auto_update: false # Manual updates only
```

### Managing Repositories

```bash
# List registered repositories
/agent:agent-manager list-repos

# Show detailed repository information
/agent:agent-manager list-repos --detailed

# Update specific repository
/agent:agent-manager update-repo primary-agents

# Update all repositories
/agent:agent-manager update-repos

# Remove repository
/agent:agent-manager remove-repo community-agents
```

## Agent Discovery and Installation

### Browsing Available Agents

```bash
# List all available agents
/agent:agent-manager discover

# Filter by category
/agent:agent-manager discover --category testing
/agent:agent-manager discover --category debugging
/agent:agent-manager discover --category development

# Search by name or description
/agent:agent-manager search "performance"
/agent:agent-manager search "database"
```

### Installing Agents

#### Individual Agent Installation
```bash
# Install latest version
/agent:agent-manager install code-optimizer

# Install specific version
/agent:agent-manager install code-optimizer@1.5.2

# Install with dependency resolution
/agent:agent-manager install advanced-tester --resolve-deps
```

#### Bulk Installation
```bash
# Install all agents in category
/agent:agent-manager install --category development

# Install multiple specific agents
/agent:agent-manager install workflow-master code-reviewer test-optimizer

# Install from configuration
/agent:agent-manager install --from-config
```

### Installation Options

#### Dependency Resolution
The Agent Manager automatically resolves dependencies:

```bash
# Install with automatic dependency resolution (default)
/agent:agent-manager install complex-agent

# Install without dependencies (advanced users)
/agent:agent-manager install complex-agent --no-deps

# Show what would be installed
/agent:agent-manager install complex-agent --dry-run
```

#### Version Selection
```bash
# Install latest stable version (default)
/agent:agent-manager install agent-name

# Install latest version including pre-releases
/agent:agent-manager install agent-name@latest

# Install specific version
/agent:agent-manager install agent-name@2.1.0

# Install version range
/agent:agent-manager install agent-name@">=2.0.0,<3.0.0"
```

## Agent Management

### Checking Agent Status

```bash
# Show all installed agents
/agent:agent-manager status

# Show detailed agent information
/agent:agent-manager info workflow-master

# Check for available updates
/agent:agent-manager check-updates

# Show agent usage statistics
/agent:agent-manager stats
```

### Updating Agents

#### Individual Updates
```bash
# Update specific agent
/agent:agent-manager update workflow-master

# Update to specific version
/agent:agent-manager update workflow-master@2.2.0

# Preview update without installing
/agent:agent-manager update workflow-master --dry-run
```

#### Bulk Updates
```bash
# Update all agents
/agent:agent-manager update-all

# Update agents in specific category
/agent:agent-manager update --category development

# Update with confirmation prompts
/agent:agent-manager update-all --interactive
```

#### Automatic Updates
Configure automatic updates in preferences:

```yaml
# .claude/agent-manager/preferences.yaml
update:
  update_schedule: "daily"    # daily, weekly, manual
  update_categories:
    - "development"
    - "testing"
  exclude_from_updates:
    - "workflow-master"  # Pin specific agents
```

### Version Management and Rollbacks

```bash
# Show version history
/agent:agent-manager history workflow-master

# Rollback to previous version
/agent:agent-manager rollback workflow-master

# Rollback to specific version
/agent:agent-manager rollback workflow-master@2.0.0

# List available versions
/agent:agent-manager versions workflow-master
```

### Uninstalling Agents

```bash
# Uninstall specific agent
/agent:agent-manager uninstall test-agent

# Uninstall with cleanup
/agent:agent-manager uninstall test-agent --clean

# Uninstall multiple agents
/agent:agent-manager uninstall agent1 agent2 agent3

# Uninstall all agents in category
/agent:agent-manager uninstall --category experimental
```

## Configuration Management

### Global Configuration

Edit `.claude/agent-manager/config.yaml`:

```yaml
settings:
  # Update behavior
  auto_update: true
  check_interval: "24h"      # How often to check for updates
  update_on_startup: true    # Check updates at session start
  
  # Cache settings
  cache_ttl: "7d"           # How long to keep cached data
  max_cache_size: "100MB"   # Maximum cache size
  offline_mode: false       # Enable offline-only mode
  
  # Security settings
  verify_checksums: true    # Verify downloaded file integrity
  allow_unsigned: false     # Allow unsigned agents
  scan_agents: true         # Basic security scanning
  
  # Logging
  log_level: "info"         # debug, info, warn, error
  log_retention: "30d"      # How long to keep logs
```

### User Preferences

Edit `.claude/agent-manager/preferences.yaml`:

```yaml
installation:
  # Pin specific agents to versions
  preferred_versions:
    workflow-master: "2.1.0"
    code-reviewer: "latest"
    
  # Categories to auto-install
  auto_install_categories:
    - "development"
    - "testing"
    
  # Agents to never install
  excluded_agents:
    - "experimental-feature"
    - "deprecated-tool"
    
  # How to resolve version conflicts
  conflict_resolution:
    strategy: "prefer_newer"  # prefer_newer, prefer_older, prompt

update:
  # When to check for updates
  update_schedule: "daily"   # daily, weekly, manual
  
  # Which categories to auto-update
  update_categories:
    - "development"
  
  # Agents to exclude from auto-updates
  exclude_from_updates:
    - "workflow-master"     # Pinned version
```

### Environment Variables

The Agent Manager respects these environment variables:

```bash
# GitHub authentication
export GITHUB_TOKEN="your_personal_access_token"

# Alternative Git credentials
export GIT_USERNAME="your_username"
export GIT_PASSWORD="your_password"

# Proxy settings
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"

# Custom cache directory
export AGENT_MANAGER_CACHE="/custom/cache/path"
```

## Session Integration

### Automatic Startup

The Agent Manager automatically runs at session start if hooks are configured:

```json
{
  "on_session_start": [
    {
      "name": "agent-manager-check",
      "command": "/agent:agent-manager",
      "args": "check-and-update-agents",
      "async": true,
      "timeout": "60s"
    }
  ]
}
```

### Manual Session Commands

```bash
# Force startup check
/agent:agent-manager check-and-update-agents --force

# Setup startup hooks
/agent:agent-manager setup-hooks

# Disable automatic checks
/agent:agent-manager config settings.update_on_startup false
```

## Cache Management

### Cache Operations

```bash
# Show cache status
/agent:agent-manager cache-status

# Clean old cache files
/agent:agent-manager cleanup-cache

# Rebuild entire cache
/agent:agent-manager rebuild-cache

# Show cache statistics
/agent:agent-manager cache-stats
```

### Cache Configuration

```yaml
# Cache settings in config.yaml
settings:
  cache_ttl: "7d"           # Cache expiration time
  max_cache_size: "100MB"   # Maximum cache size
  cache_compression: true   # Compress cached files
  cache_cleanup_interval: "daily"  # Automatic cleanup frequency
```

### Offline Mode

```bash
# Enable offline mode
/agent:agent-manager config settings.offline_mode true

# Disable offline mode
/agent:agent-manager config settings.offline_mode false

# Check offline capabilities
/agent:agent-manager offline-status
```

## Troubleshooting

### Common Issues

#### Network Connectivity
```bash
# Test repository connectivity
/agent:agent-manager test-connection primary-agents

# Work offline with cached agents
/agent:agent-manager config settings.offline_mode true

# Retry failed operations
/agent:agent-manager retry-failed
```

#### Authentication Problems
```bash
# Verify authentication
/agent:agent-manager test-auth github-repo

# Update credentials
export GITHUB_TOKEN="new_token"
/agent:agent-manager update-repo github-repo

# Switch to SSH authentication
/agent:agent-manager register-repo git@github.com:user/repo.git --auth ssh
```

#### Version Conflicts
```bash
# Show conflict details
/agent:agent-manager conflicts

# Resolve conflicts interactively
/agent:agent-manager resolve-conflicts --interactive

# Force resolution with preference
/agent:agent-manager resolve-conflicts --prefer-newer
```

#### Cache Issues
```bash
# Clear corrupted cache
/agent:agent-manager cleanup-cache --force

# Rebuild cache from scratch
/agent:agent-manager rebuild-cache

# Verify cache integrity
/agent:agent-manager verify-cache
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Enable debug logging
/agent:agent-manager config log_level debug

# Show recent operations
/agent:agent-manager log --tail 50

# Export diagnostic information
/agent:agent-manager diagnostic > agent-manager-debug.txt
```

### Recovery Operations

```bash
# Reset to defaults
/agent:agent-manager reset --confirm

# Backup current configuration
/agent:agent-manager backup config.backup

# Restore from backup
/agent:agent-manager restore config.backup

# Verify installation integrity
/agent:agent-manager verify --all
```

## Advanced Usage

### Custom Repository Structures

For repositories without manifest files:

```bash
# Force scan for agents
/agent:agent-manager scan-repo custom-repo --force

# Register with custom agent path
/agent:agent-manager register-repo /path/to/repo --agent-path "custom/agents/"
```

### Integration with CI/CD

```bash
# Install agents in CI environment
/agent:agent-manager install --from-config --non-interactive

# Update agents in deployment pipeline
/agent:agent-manager update-all --dry-run --output json

# Verify agent integrity in production
/agent:agent-manager verify --critical-only
```

### Scripting and Automation

```bash
# Export installed agents list
/agent:agent-manager list --format json > installed-agents.json

# Install from exported list
/agent:agent-manager install --from-file installed-agents.json

# Batch operations
for agent in workflow-master code-reviewer test-solver; do
  /agent:agent-manager install "$agent"
done
```

## Best Practices

### Repository Management
1. **Use priorities**: Set higher priorities for trusted repositories
2. **Pin critical agents**: Use version pinning for production-critical agents
3. **Regular updates**: Update repositories regularly but test agent updates
4. **Backup configs**: Keep backups of working configurations

### Version Management
1. **Test updates**: Use `--dry-run` to preview updates
2. **Gradual rollout**: Update non-critical agents first
3. **Rollback preparation**: Keep previous versions for quick rollback
4. **Version documentation**: Document why specific versions are pinned

### Security
1. **Verify sources**: Only use trusted repositories
2. **Enable scanning**: Keep agent scanning enabled
3. **Review changes**: Check agent changes before updating
4. **Access control**: Use minimal required permissions for authentication

### Performance
1. **Cache management**: Regular cache cleanup prevents bloat
2. **Selective updates**: Don't auto-update all categories
3. **Network efficiency**: Use offline mode when appropriate
4. **Monitor resources**: Check cache size and memory usage

This comprehensive usage guide covers all aspects of the Agent Manager. For additional help, use:

```bash
/agent:agent-manager help <command>
```