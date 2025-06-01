#!/bin/bash

echo "Testing Planner Agent..."

# Load .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "ERROR: .env file not found!"
    exit 1
fi

# Check if API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY not set!"
    exit 1
fi

echo "API Key loaded: ${GOOGLE_API_KEY:0:20}..."
echo "Current directory: $(pwd)"
echo ""

# Check if agent card exists
if [ ! -f "agent_cards/planner_agent.json" ]; then
    echo "ERROR: agent_cards/planner_agent.json not found!"
    exit 1
fi

echo "Agent card found. Contents:"
cat agent_cards/planner_agent.json | head -5
echo "..."
echo ""

echo "Starting Planner Agent on port 10102..."
echo "Command: cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/planner_agent.json --port 10102"
echo ""

# Run with explicit environment
cd src && GOOGLE_API_KEY="$GOOGLE_API_KEY" uv run python -m a2a_mcp.agents --agent-card ../agent_cards/planner_agent.json --port 10102