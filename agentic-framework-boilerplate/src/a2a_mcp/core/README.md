# Core Modules

This directory contains the core abstractions and protocols for the A2A MCP framework.

## Modules

### agent.py
Base abstract classes for agents in the framework:
- `Agent`: Abstract base class defining the agent interface
- `AgentCapability`: Enumeration of standard agent capabilities

### protocol.py
A2A (Agent-to-Agent) protocol implementation:
- `A2AMessage`: Message structure for agent communication
- `A2AProtocol`: Protocol handler for routing messages between agents
- `MessageType`, `MessageStatus`, `ProtocolVersion`: Protocol enumerations
- `MessageValidator`: Validates protocol compliance

### quality.py
Quality assurance and validation framework:
- `QualityFramework`: Main quality validation system
- `QualityMetric`: Individual quality measurements
- `QualityReport`: Comprehensive quality assessment results
- `ValidationRule`: Rules for data validation
- `QualityLevel`, `MetricType`: Quality-related enumerations

## Usage

These core modules provide the foundational abstractions that concrete implementations build upon. They define:

1. **Agent Interface**: How agents should be structured and what methods they must implement
2. **Communication Protocol**: How agents communicate with each other
3. **Quality Standards**: How to measure and ensure quality of agent outputs

The actual implementations of these abstractions can be found in the `common/` directory.