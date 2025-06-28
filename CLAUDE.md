# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
   - `orchestrator.py`: Manages workflow and coordinates other agents
   - `planner.py`: Uses LangGraph to break down requests into structured plans
   - `air_ticketing.py`, `hotel_booking.py`, `car_rental.py`: Task-specific agents

### Communication Flow
1. Client sends request to Orchestrator Agent
2. Orchestrator forwards to Planner Agent for task decomposition
3. Planner returns structured plan with task assignments
4. Orchestrator executes plan by calling appropriate task agents
5. Task agents query databases and return results
6. Orchestrator aggregates results and returns to client

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
- Google API key required for Planner Agent (uses Gemini)
- Logs are written to `logs/` directory
- Each agent runs on a separate port (10001-10005)

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