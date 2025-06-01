#!/bin/bash
cd /home/user/a2a/a2a-mcp

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting Orchestrator Agent on port 10101..."
cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/orchestrator_agent.json --port 10101