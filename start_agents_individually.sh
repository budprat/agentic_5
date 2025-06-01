#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting A2A-MCP Agents Individually"
echo "===================================="
echo ""
echo "Run each of these commands in a separate terminal:"
echo ""

echo "1. MCP Server (Terminal 1):"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100"
echo ""

echo "2. Orchestrator Agent (Terminal 2):"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run python -m a2a_mcp.agents --agent-card agent_cards/orchestrator_agent.json --port 10101"
echo ""

echo "3. Planner Agent (Terminal 3):"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run python -m a2a_mcp.agents --agent-card agent_cards/planner_agent.json --port 10102"
echo ""

echo "4. Air Ticketing Agent (Terminal 4):"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run python -m a2a_mcp.agents --agent-card agent_cards/air_ticketing_agent.json --port 10103"
echo ""

echo "5. Hotel Booking Agent (Terminal 5):"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run python -m a2a_mcp.agents --agent-card agent_cards/hotel_booking_agent.json --port 10104"
echo ""

echo "6. Car Rental Agent (Terminal 6):"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run python -m a2a_mcp.agents --agent-card agent_cards/car_rental_agent.json --port 10105"
echo ""

echo "After all services are running, test with:"
echo "   cd /home/user/a2a/a2a-mcp"
echo "   uv run python test_single_agent.py"