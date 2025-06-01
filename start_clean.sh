#!/bin/bash

echo "Starting A2A-MCP Services (Clean)"
echo "================================="

cd /home/user/a2a/a2a-mcp

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "ERROR: .env file not found!"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY not set!"
    exit 1
fi

echo "API Key loaded: ${GOOGLE_API_KEY:0:20}..."

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "a2a-mcp\|a2a_mcp" || true
sleep 3

# Create logs directory
mkdir -p logs

# Start MCP Server
echo "Starting MCP Server..."
nohup uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 > logs/mcp-server.log 2>&1 &
MCP_PID=$!
echo "MCP Server started (PID: $MCP_PID)"
sleep 5

# Check if MCP server is responding
if ! curl -s http://localhost:10100/sse >/dev/null 2>&1; then
    echo "ERROR: MCP Server not responding"
    exit 1
fi

# Start Orchestrator
echo "Starting Orchestrator Agent..."
cd src && nohup uv run python -m a2a_mcp.agents --agent-card ../agent_cards/orchestrator_agent.json --port 10101 > ../logs/orchestrator.log 2>&1 &
ORCH_PID=$!
echo "Orchestrator started (PID: $ORCH_PID)"
cd ..
sleep 3

# Check if orchestrator is responding
if ! curl -s http://localhost:10101/ >/dev/null 2>&1; then
    echo "WARNING: Orchestrator may not be fully ready yet"
fi

echo ""
echo "Essential services started!"
echo "- MCP Server: http://localhost:10100 (PID: $MCP_PID)"
echo "- Orchestrator: http://localhost:10101 (PID: $ORCH_PID)"
echo ""
echo "Start other agents as needed:"
echo "  ./run_agent.sh planner 10102"
echo "  ./run_agent.sh air_ticketing 10103"
echo "  ./run_agent.sh hotel_booking 10104" 
echo "  ./run_agent.sh car_rental 10105"
echo ""
echo "Test with:"
echo "  uv run python chat.py"