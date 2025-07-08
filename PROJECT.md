# A2A-MCP Project Information

This file provides project-specific guidance for the A2A-MCP multi-agent system.

## Project Overview

A2A-MCP is a multi-agent system demonstrating agent-to-agent communication using the Model Context Protocol (MCP). It implements a travel agency system where specialized agents collaborate to handle flights, hotels, and car rentals.

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
# Start all services (requires GOOGLE_API_KEY environment variable)
./run_all_agents.sh

# Or start individual services:
# MCP Server (must be started first)
uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100

# Orchestrator Agent
uv run src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10001

# Planner Agent  
uv run src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10002

# Task Agents
uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10003
uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10004
uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10005
```

### Testing
```bash
# Test all agents
./test_agents.sh

# Initialize demo database
python init_database.py

# Run client example
python simple_client.py
```

## Architecture

### Core Components
1. **MCP Server** (`src/a2a_mcp/mcp/server.py`): Registry for agent discovery, provides tools via MCP
2. **Base Agent** (`src/a2a_mcp/common/base_agent.py`): Common functionality for all agents
3. **Agent Implementations** (`src/a2a_mcp/agents/`):
   - `orchestrator_agent.py`: Manages workflow and coordinates other agents (sequential execution)
   - `parallel_orchestrator_agent.py`: Enhanced orchestrator with parallel task execution
   - `langgraph_planner_agent.py`: Uses LangGraph to break down requests into structured plans
   - `adk_travel_agent.py`: Unified travel agent implementation using Google ADK

### Unified Travel Agent Architecture
The system uses a **single TravelAgent class** that powers all travel booking services:
- **Air Ticketing Agent** (port 10103): Uses `TravelAgent` with flight-specific prompts
- **Hotel Booking Agent** (port 10104): Uses `TravelAgent` with hotel-specific prompts  
- **Car Rental Agent** (port 10105): Uses `TravelAgent` with car rental-specific prompts

Each service is specialized through:
- **Agent Cards**: JSON configurations defining capabilities and metadata
- **Prompt Instructions**: Service-specific chain-of-thought decision trees
- **Port Assignment**: Separate ports for service isolation

### Communication Flow
1. Client sends request to Orchestrator Agent (port 10101)
2. Orchestrator forwards to Planner Agent (port 10102) for task decomposition
3. Planner returns structured plan with task assignments using chain-of-thought reasoning
4. Orchestrator uses MCP Server for agent discovery and creates execution graph
5. Tasks distributed to TravelAgent instances (ports 10103-10105) via A2A protocol
6. Each TravelAgent queries database via MCP tools and returns structured results
7. Orchestrator aggregates results and generates comprehensive summary

### Key Protocols
- **A2A Protocol**: Agent-to-agent communication using `a2a-sdk`
- **MCP**: Model Context Protocol for tool discovery and execution
- **Agent Cards**: JSON configurations in `agent_cards/` defining agent capabilities

### Database
- SQLite database (`travel_agency.db`) with tables: flights, hotels, car_rentals
- Initialized via `init_database.py` with demo data

## Important Notes
- All agents must register with MCP server on startup
- Agents communicate via HTTP using the A2A protocol
- Google API key required for both Planner and TravelAgent instances (use Gemini)
- Logs are written to `logs/` directory
- Each agent runs on a separate port (10101-10105)
- ParallelOrchestratorAgent provides significant performance improvements through concurrent execution
- TravelAgent instances use Google ADK with MCP tool integration for database access

## NotionAI MCP Server Rules
IMPORTANT: When working with Notion through the NotionAI MCP server:
- **WRITE ONLY TO THE "AI" PAGE** (ID: 21e0f849-e0a2-80c3-8b72-ccb0a1b61ab9)
- All other Notion pages are READ-ONLY for reference and data gathering
- See `notion_mcp_rules.md` for detailed usage guidelines
- Available pages list in `notion_pages_complete_list.md` (90+ pages organized by category)

## Development Rules
- **NEVER bypass errors by creating simpler demos or test files**. Always fix the actual issues in the existing code.
- When encountering errors during testing, ALWAYS fix the root cause rather than creating workarounds or simplified versions.
- Do not create "simple" or "basic" versions of tests when the full tests fail - fix the actual problems.
- **NEVER use mock data or placeholder data** when real data sources fail. Fix the actual integration issues instead of returning fake data.
- If an API or service is not working, fix the connection/authentication/timeout issues rather than bypassing with mock responses.
- **NEVER create alternative "simple" scripts when tests fail**. Instead, focus on solving the actual issues, debugging the root cause, and implementing proper fixes.
- When tests encounter errors, investigate and resolve them properly rather than creating shortcuts or workarounds.