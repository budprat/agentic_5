#!/bin/bash
# run_nexus_agents.sh - Framework compliant startup for Nexus system

echo "Starting Nexus Transdisciplinary Research Synthesis System..."
echo "Following A2A-MCP Framework patterns..."

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable is not set"
    exit 1
fi

# Start MCP Server (shared across all domains)
echo "Starting MCP Server..."
uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 &
MCP_PID=$!

# Wait for MCP server to be ready
sleep 3

# Start Nexus Domain Agents (Framework Compliant Ports)
echo "Starting Nexus Orchestrator Agent (Port 11001)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/nexus_orchestrator_agent.json --port 11001 &
ORCH_PID=$!

echo "Starting Nexus Planner Agent (Port 11002)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/nexus_planner_agent.json --port 11002 &
PLANNER_PID=$!

# Disciplinary Domain Supervisors (11003-11020)
echo "Starting Life Sciences Supervisor (Port 11003)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/life_sciences_supervisor_agent.json --port 11003 &

echo "Starting Social Sciences Supervisor (Port 11004)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/social_sciences_supervisor_agent.json --port 11004 &

echo "Starting Economics & Policy Supervisor (Port 11005)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/economics_policy_supervisor_agent.json --port 11005 &

echo "Starting Physical Sciences Supervisor (Port 11006)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/physical_sciences_supervisor_agent.json --port 11006 &

echo "Starting Computer Science Supervisor (Port 11007)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/computer_science_supervisor_agent.json --port 11007 &

echo "Starting Psychology Supervisor (Port 11013)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/psychology_supervisor_agent.json --port 11013 &

echo "Starting Cross-Domain Analysis Supervisor (Port 11019)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/cross_domain_analysis_supervisor_agent.json --port 11019 &

echo "Starting Visualization & Synthesis Supervisor (Port 11020)..."
uv run src/a2a_mcp/agents/ --agent-card agent_cards/visualization_synthesis_supervisor_agent.json --port 11020 &

echo "All Nexus agents started successfully!"
echo "Orchestrator: http://localhost:11001"
echo "Planner: http://localhost:11002"
echo "Domain Supervisors: http://localhost:11003-11020"
echo "Use ENABLE_PARALLEL_EXECUTION=true for parallel orchestration"

# Store PIDs for cleanup
echo $MCP_PID > .mcp_pid
echo $ORCH_PID > .nexus_orch_pid
echo $PLANNER_PID > .nexus_planner_pid

echo "All Nexus agents are running. Use 'pkill -f \"nexus\"' to stop all agents."