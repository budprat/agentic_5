# A2A-MCP Framework Architecture

## Overview

The A2A-MCP Framework is a production-ready foundation for building multi-agent systems with agent-to-agent communication and Model Context Protocol (MCP) integration.

## Core Architecture Principles

### 1. Three-Tier Agent Hierarchy

```
┌─────────────────────────────┐
│     Tier 1: Orchestrator    │
│    (Master Coordination)    │
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────────┐  ┌──────▼──────┐
│   Tier 2   │  │   Tier 2    │
│  Domain A  │  │  Domain B   │
└───┬────────┘  └──────┬──────┘
    │                  │
┌───▼───┐  ┌────┐  ┌──▼───┐
│Tier 3 │  │T3  │  │Tier 3│
│Service│  │Svc │  │Tool  │
└───────┘  └────┘  └──────┘
```

### 2. Component Architecture

```
A2A-MCP Framework
├── Core Components
│   ├── StandardizedAgentBase     # Base class for all agents
│   ├── A2AProtocolClient        # Agent-to-agent communication
│   ├── QualityFramework         # Quality validation
│   └── MCPToolset               # MCP tool integration
│
├── MCP Server
│   ├── Agent Discovery          # Find available agents
│   ├── Health Monitoring        # Check agent status
│   └── Custom Tools            # Domain-specific tools
│
├── Launch System
│   ├── Environment Setup       # Validates prerequisites
│   ├── Process Management      # Starts/stops agents
│   └── Health Loop            # Monitors system health
│
└── Configuration
    ├── Agent Cards            # JSON agent definitions
    ├── Quality Configs        # Domain quality rules
    └── Environment           # System settings
```

## Key Components

### StandardizedAgentBase

The foundation class that all agents inherit from provides:
- Google ADK integration for LLM capabilities
- MCP toolset for extended functionality
- A2A protocol for inter-agent communication
- Quality validation framework
- Standardized lifecycle management

### A2A Protocol

JSON-RPC based communication with:
- Port-based service discovery
- Retry mechanism with exponential backoff
- Timeout handling
- Error propagation
- Custom port mapping support

### Quality Framework

Domain-agnostic quality validation supporting:
- BUSINESS: Business logic validation
- ACADEMIC: Research quality standards
- SERVICE: Performance metrics
- GENERIC: Basic validation

### MCP Server

Provides system-wide tools for:
- Agent discovery
- Health monitoring
- Custom domain tools

## Communication Patterns

1. **Direct A2A**: Client → Agent A → Agent B → Client
2. **Orchestrated**: Client → Orchestrator → Multiple Agents → Aggregated Response
3. **Tool-Enhanced**: Agent → MCP Tool → External Service → Quality Check → Client

## Port Management

- Tier 1 (Orchestrators): 10100-10199
- Tier 2 (Domain Specialists): 10200-10899
- Tier 3 (Service Agents): 10900-10999
- MCP Server: 10099

## Best Practices

1. Keep agents focused on single responsibilities
2. Use appropriate tiers for agent types
3. Implement proper error handling
4. Validate all inputs and outputs
5. Monitor performance metrics
6. Use environment variables for configuration