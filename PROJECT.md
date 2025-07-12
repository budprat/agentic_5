# A2A-MCP Project Information

This file provides project-specific guidance for the A2A-MCP multi-agent system.

## Project Overview

A2A-MCP is a multi-agent system demonstrating agent-to-agent communication using the Model Context Protocol (MCP). It provides a flexible framework where specialized agents collaborate to handle complex business workflows through coordinated task execution.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies (handled by uv automatically)
```

### Running Services
```bash
# Start all services (requires API keys for your chosen LLM provider)
./start.sh

# Or start individual services:
# MCP Server (must be started first)
uv run src/a2a_mcp/mcp/ --transport sse --host localhost --port 10100

# Orchestrator Agent
uv run src/a2a_mcp/agents/ --agent-card agent_cards/tier1/master_orchestrator.json --port 10001

# Domain Specialist Agent  
uv run src/a2a_mcp/agents/ --agent-card agent_cards/tier2/domain_specialist.json --port 10002

# Service Agents
uv run src/a2a_mcp/agents/ --agent-card agent_cards/tier3/service_agent.json --port 10003
```

### Testing
```bash
# Test all agents
./run_tests.sh

# Run client example
python examples/simple_client.py
```

## Architecture

### Core Components
1. **MCP Server** (`src/a2a_mcp/mcp/server.py`): Registry for agent discovery, provides tools via MCP
2. **Base Agent** (`src/a2a_mcp/common/base_agent.py`): Common functionality for all agents
3. **Agent Implementations** (`src/a2a_mcp/agents/`):
   - **Tier 1** - Master Orchestrator: Manages workflows and coordinates other agents
   - **Tier 2** - Domain Specialists: Handle specialized business logic and analysis
   - **Tier 3** - Service Agents: Execute specific tasks and tool integrations

### Tiered Agent Architecture
The system uses a **hierarchical agent architecture** for scalable business workflows:
- **Tier 1 (Master Orchestrator)**: High-level workflow coordination and planning
- **Tier 2 (Domain Specialists)**: Business domain expertise and complex reasoning  
- **Tier 3 (Service Agents)**: Direct tool integration and atomic operations

Each tier is specialized through:
- **Agent Cards**: JSON configurations defining capabilities and metadata
- **Instruction Templates**: Domain-specific processing patterns
- **Port Assignment**: Separate ports for service isolation

### Communication Flow
1. Client sends request to Master Orchestrator (Tier 1)
2. Orchestrator analyzes request and identifies required domain specialists
3. Domain Specialists (Tier 2) receive tasks and break them down into service operations
4. Orchestrator uses MCP Server for agent discovery and creates execution graph
5. Tasks distributed to Service Agents (Tier 3) via A2A protocol
6. Each Service Agent executes tools via MCP and returns structured results
7. Domain Specialists aggregate and process results for business logic
8. Master Orchestrator synthesizes final response and returns to client

### Key Protocols
- **A2A Protocol**: Agent-to-agent communication using `a2a-sdk`
- **MCP**: Model Context Protocol for tool discovery and execution
- **Agent Cards**: JSON configurations in `agent_cards/` defining agent capabilities

### Data Layer
- Configurable data sources via MCP tool integration
- Support for databases, APIs, file systems, and cloud services
- Example implementations included for common business data patterns

## Important Notes
- All agents must register with MCP server on startup
- Agents communicate via HTTP using the A2A protocol
- API keys required for your chosen LLM provider (Google Gemini, OpenAI, etc.)
- Logs are written to `logs/` directory
- Each agent runs on a separate port for isolation
- Parallel orchestration provides significant performance improvements
- Service agents use MCP tool integration for external system access

## MCP Integration Examples
The framework includes example integrations with various MCP servers:
- **Database MCP**: SQL database access and querying
- **File System MCP**: File operations and document processing
- **API MCP**: REST API integrations and webhook handling
- **Cloud Services MCP**: AWS, GCP, Azure service integrations

## Development Rules
- **NEVER bypass errors by creating simpler demos or test files**. Always fix the actual issues in the existing code.
- When encountering errors during testing, ALWAYS fix the root cause rather than creating workarounds or simplified versions.
- Do not create "simple" or "basic" versions of tests when the full tests fail - fix the actual problems.
- **NEVER use mock data or placeholder data** when real data sources fail. Fix the actual integration issues instead of returning fake data.
- If an API or service is not working, fix the connection/authentication/timeout issues rather than bypassing with mock responses.
- **NEVER create alternative "simple" scripts when tests fail**. Instead, focus on solving the actual issues, debugging the root cause, and implementing proper fixes.
- When tests encounter errors, investigate and resolve them properly rather than creating shortcuts or workarounds.

## Customization Guide
This framework is designed to be adapted for any business domain. See `DOMAIN_CUSTOMIZATION_GUIDE.md` for detailed instructions on:
- Adapting agent cards for your domain
- Implementing domain-specific business logic
- Integrating with your existing systems
- Configuring MCP tools for your data sources