# Solopreneur Oracle - Domain Implementation Example

This directory contains a complete implementation of the A2A-MCP framework customized for the solopreneur/developer productivity domain. This serves as the **gold standard example** of how to implement a domain-specific agent ecosystem.

## Architecture Overview

This implementation demonstrates the **3-Tier Agent Architecture**:

- **Tier 1**: Master Oracle (port 10901) - High-level orchestration
- **Tier 2**: 6 Domain Specialists (ports 10902-10907) - Technical, Knowledge, Personal, Learning, Integration, AWIE
- **Tier 3**: 70 Intelligence Modules (ports 10910-10979) - Specialized micro-services

## Key Components

### `agent_registry.py`
- Complete registry of 76 specialized agents
- Demonstrates systematic port allocation (10910-10979)
- Shows how to organize agents by categories and capabilities
- **Pattern**: Use this as template for any domain's agent registry

### `base_solopreneur_agent.py`
- Framework V2.0 compliant base class extending `StandardizedAgentBase`
- Shows proper domain-specific agent initialization
- **Pattern**: Copy this structure for your domain's base agent

### `__main__.py`
- Standalone domain launcher with testing capabilities
- Environment validation and health checks
- **Pattern**: Template for domain-specific launchers

## Port Organization Pattern

```
10910-10919: Technical Intelligence (AI research, architecture, security)
10920-10929: Knowledge Systems (Neo4j, vector DB, pattern recognition)
10930-10939: Personal Systems (circadian, focus, energy, stress)
10940-10949: Learning Systems (skill gaps, spaced repetition, progress)
10950-10959: Integration Layer (cross-domain, workflows, quality)
10960-10979: AWIE Revolutionary Intelligence (autonomous workflow)
```

## How to Adapt for Your Domain

1. **Replace Domain Logic**: Change "solopreneur" terminology to your domain
2. **Customize Agent Registry**: Define your domain's agent hierarchy
3. **Modify Port Ranges**: Allocate ports systematically for your categories
4. **Update Instructions**: Replace productivity-focused instructions with domain-specific ones
5. **Adapt Tools**: Modify MCP tools for your domain's data sources

## Advanced Features

### AWIE (Autonomous Workflow Intelligence Engine)
This implementation includes revolutionary AWIE patterns:
- Context-driven orchestration
- Flow state protection
- Predictive task generation
- Autonomous workflow optimization

### Domain-Specific Validation
- Business rule enforcement
- Quality metrics specific to developer productivity
- Performance optimization patterns

## Integration with Core Framework

This example shows how to properly integrate with the A2A-MCP core:
- Extends `StandardizedAgentBase`
- Uses unified MCP tools architecture
- Follows A2A protocol specifications
- Implements proper health checking and monitoring

Use this implementation as your reference when creating domain-specific agent ecosystems.