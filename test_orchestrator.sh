#!/bin/bash

echo "Testing Orchestrator Agent with API Key..."

# Load .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY not set!"
    exit 1
fi

echo "API Key loaded: ${GOOGLE_API_KEY:0:20}..."
echo ""
echo "Starting Orchestrator Agent..."

cd src && GOOGLE_API_KEY="$GOOGLE_API_KEY" uv run python -m a2a_mcp.agents --agent-card ../agent_cards/orchestrator_agent.json --port 10101