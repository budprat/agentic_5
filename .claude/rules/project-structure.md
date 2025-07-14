---
description: A2A MCP Framework project structure and important files reference
globs: **/*
alwaysApply: true
---
# A2A MCP Framework Project Structure

This rule documents the directory structure and important files in the A2A MCP Framework project. Always refer to this when navigating the codebase or adding new components.

## Project Overview

The A2A MCP Framework is a Python-based multi-agent orchestration system with Vertex AI Memory Bank integration and MCP (Model Context Protocol) support.

## Core Directory Structure

### Root Documentation Files
- **CLAUDE.md** - SuperClaude configuration and behavioral rules
- **README.md** - Main project documentation
- **QUICKSTART.md** - Quick start guide for new users
- **PROJECT.md** - Detailed project overview
- **FRAMEWORK_COMPONENTS_AND_ORCHESTRATION_GUIDE.md** - Architecture reference

### Source Code (`src/a2a_mcp/`)

#### Main Modules:
1. **agents/** - Agent implementations
   - `example_travel_domain/` - Travel domain examples
   - Contains orchestrator and specialist agents

2. **common/** - Shared utilities and base classes
   - `base_agent.py` - Base agent class all agents inherit from
   - `standardized_agent_base.py` - Standardized agent implementation
   - `a2a_protocol.py` - A2A protocol definitions
   - `agent_executor.py` - Agent execution engine
   - `config_manager.py` - Configuration management
   - `workflow.py` - Workflow management
   - `enhanced_workflow.py` - Enhanced workflow patterns
   - `parallel_workflow.py` - Parallel execution patterns

3. **memory/** - Memory service implementations
   - `base.py` - Base memory service classes (Session, Event, BaseMemoryService)
   - `vertex_ai_memory_bank.py` - Vertex AI Memory Bank integration
   - `memory_integration.py` - Helper for session management
   - `prompts/` - Memory-aware prompt templates

4. **mcp/** - MCP server/client implementations
   - `server.py` - MCP server implementation
   - `client.py` - MCP client implementation
   - `remote_mcp_connector.py` - Remote MCP connections

5. **core/** - Core framework components
   - `agent.py` - Core agent definitions
   - `protocol.py` - Protocol specifications
   - `quality.py` - Quality framework

### Configuration (`configs/`)
- **framework.yaml** - Main framework configuration
- **observability.yaml** - Monitoring and metrics config
- **system_config.yaml** - System-level settings
- **memory_config_schema.md** - Memory configuration documentation

### Agent Cards (`agent_cards/`)
Organized by tiers:
- **tier1/** - Orchestrator agents (master, domain-specific)
- **tier2/** - Domain specialist agents
- **tier3/** - Service agents
- Root level contains example agents and templates

### Examples (`examples/`)
- **memory_enabled_agent.py** - Complete memory integration example
- **travel/** - Travel domain examples with ADK integration
- **finance/** - Financial domain examples
- **workflow_demos/** - Workflow pattern demonstrations
- **domains/solopreneur_oracle/** - Domain-specific implementations

### Claude Configuration (`.claude/`)
- **rules/** - Project-specific rules
  - `claude-rules.md` - How to create/edit rules
  - `self-improve.md` - Rule improvement guidelines
  - `project-structure.md` - This file
- **SESSION.md** - Session tracking (updated after code changes)
- **PRD.md**, **PLAN.md**, **SPECS.md** - Project specifications
- **commands/** - Command definitions and patterns
- **shared/** - Shared SuperClaude configurations

### ADK Crash Course (`agent-development-kit-crash-course/`)
12 progressive examples teaching agent development:
1. Basic agent
2. Tool-using agent
3. LiteLLM integration
4. Structured outputs
5. Sessions and state
6. Persistent storage
7. Multi-agent systems
8. Stateful multi-agent
9. Callbacks
10. Sequential workflows
11. Parallel workflows
12. Loop-based agents

### Documentation (`docs/`)
- **ARCHITECTURE.md** - System architecture
- **DEVELOPER_GUIDE.md** - Developer reference
- **DOMAIN_CUSTOMIZATION_GUIDE.md** - Domain customization
- **INTEGRATION_PATTERNS.md** - Integration best practices
- **OBSERVABILITY_DEPLOYMENT.md** - Monitoring setup

### Tests (`tests/`)
- Unit tests for all core components
- **test_a2a_protocol.py** - Protocol tests
- **test_agents.py** - Agent functionality tests
- **test_quality_framework.py** - Quality assurance tests

### Launch Scripts
- **launch/launch_system.py** - System launcher
- **scripts/generate_agent.py** - Agent generation utility
- Shell scripts: `install.sh`, `start.sh`, `stop.sh`, `run_tests.sh`

## Important Files Reference

### Configuration Files
- `pyproject.toml` - Python project configuration
- `requirements.txt` - Dependencies
- `uv.lock` - UV package manager lock

### Entry Points
- `src/a2a_mcp/mcp/__main__.py` - MCP server entry
- `src/a2a_mcp/agents/__main__.py` - Agent runner entry

### Key Base Classes
- `src/a2a_mcp/common/base_agent.py` - All agents inherit from BaseAgent
- `src/a2a_mcp/memory/base.py` - Memory service interfaces
- `src/a2a_mcp/core/protocol.py` - Protocol definitions

## Adding New Components

### New Agent
1. Create in appropriate tier under `agent_cards/`
2. Implement in `src/a2a_mcp/agents/` or domain folder
3. Inherit from `BaseAgent` or `StandardizedAgentBase`
4. Add tests in `tests/`

### New Rule
1. Create in `.claude/rules/` following naming convention
2. Use kebab-case filename with .md extension
3. Include metadata header (description, globs, alwaysApply)

### New Memory Provider
1. Implement in `src/a2a_mcp/memory/`
2. Inherit from `BaseMemoryService`
3. Update `framework.yaml` with provider config

### New Domain
1. Create folder in `examples/domains/`
2. Add domain-specific agents
3. Create orchestrator for domain
4. Document in domain README

## Best Practices

1. **Always check existing patterns** - Look for similar implementations before creating new ones
2. **Follow tier hierarchy** - Orchestrators → Specialists → Services
3. **Use standardized base classes** - Don't reinvent core functionality
4. **Document configuration** - Add new configs to schema documentation
5. **Test thoroughly** - Add unit tests for new components
6. **Update SESSION.md** - Track changes during development sessions