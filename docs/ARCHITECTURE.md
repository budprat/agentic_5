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
│   ├── MCPToolset               # MCP tool integration
│   └── ObservabilityManager     # Tracing, metrics, logging
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
├── Observability Stack
│   ├── OpenTelemetry           # Distributed tracing
│   ├── Prometheus              # Metrics collection
│   ├── Grafana                 # Visualization dashboards
│   └── Structured Logging      # JSON logs with correlation
│
└── Configuration
    ├── Agent Cards            # JSON agent definitions
    ├── Quality Configs        # Domain quality rules
    ├── Observability Config   # Monitoring settings
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

## Observability Architecture

### Distributed Tracing

The framework uses OpenTelemetry to provide end-to-end visibility:

```
┌─────────────────────────────────────────────────────────┐
│                  Trace Context Flow                      │
├─────────────────────────────────────────────────────────┤
│ Client Request                                          │
│   └─> Orchestrator Span                                │
│       ├─> Planning Phase Span                          │
│       ├─> Task Distribution Span                       │
│       │   ├─> Agent A Execution Span                  │
│       │   │   └─> MCP Tool Call Span                  │
│       │   └─> Agent B Execution Span                  │
│       └─> Result Synthesis Span                       │
└─────────────────────────────────────────────────────────┘
```

### Metrics Collection

Prometheus metrics are collected at multiple levels:

```yaml
# Orchestration Metrics
orchestration_requests_total{domain, status}
orchestration_duration_seconds{domain, strategy}

# Task Metrics
tasks_executed_total{specialist, status}
task_duration_seconds{specialist}

# System Metrics
active_sessions{}
workflow_nodes_active{state}
artifacts_created_total{type, session}

# Performance Metrics
streaming_duration_seconds{type}
artifact_size_bytes{type}
```

### Structured Logging

All logs are emitted as structured JSON with trace correlation:

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "message": "Task execution completed",
  "trace_id": "1234567890abcdef",
  "span_id": "abcdef1234",
  "session_id": "session_123",
  "task_id": "task_456",
  "specialist": "research_agent",
  "duration": 1.234
}
```

### Monitoring Data Flow

```
Agents/Orchestrators
    │
    ├──[Traces]──> OpenTelemetry Collector ──> Jaeger
    ├──[Metrics]─> Prometheus ──> Grafana Dashboards
    └──[Logs]────> Structured Logger ──> Log Aggregator
```

## Communication Patterns

1. **Direct A2A**: Client → Agent A → Agent B → Client
2. **Orchestrated**: Client → Orchestrator → Multiple Agents → Aggregated Response
3. **Tool-Enhanced**: Agent → MCP Tool → External Service → Quality Check → Client
4. **Streaming with Artifacts**: Client → Orchestrator → Real-time Events → Progress/Artifacts → Client

All patterns include automatic trace propagation and metric collection.

## Port Management

- Tier 1 (Orchestrators): 10100-10199
- Tier 2 (Domain Specialists): 10200-10899
- Tier 3 (Service Agents): 10900-10999
- MCP Server: 10099

## Enhanced Master Orchestrator Capabilities

### PHASE 7: Workflow Streaming

Real-time execution visibility with artifact events:

```python
# Streaming event types
- progress: Task execution progress (0-100%)
- artifact: Artifact creation events
- task_update: Individual task status changes
- workflow_state: Workflow graph state updates
- metrics: Real-time performance data
```

### Dynamic WorkflowGraph

State management with pause/resume capabilities:
- Automatic state persistence
- Resumption strategies (continue, restart, skip, rollback)
- Checkpoint creation for recovery
- Workflow visualization data

### Context & History Tracking

Intelligent Q&A based on execution history:
- Session context preservation
- Query pattern analysis
- Domain-specific learnings
- Automatic context clearing on significant changes

## Best Practices

1. Keep agents focused on single responsibilities
2. Use appropriate tiers for agent types
3. Implement proper error handling
4. Validate all inputs and outputs
5. Monitor performance metrics
6. Use environment variables for configuration