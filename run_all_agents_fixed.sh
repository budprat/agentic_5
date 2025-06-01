#!/bin/bash

# Change to project directory
cd /home/user/a2a/a2a-mcp

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    set -a  # automatically export all variables
    source .env
    set +a
    echo "GOOGLE_API_KEY is set: ${GOOGLE_API_KEY:0:10}..."
else
    echo "ERROR: .env file not found!"
    exit 1
fi

# Function to run a command in a new terminal
run_in_terminal() {
    local name=$1
    local cmd=$2
    echo "Starting $name..."
    
    # Export environment variables for the subshell
    export GOOGLE_API_KEY
    export GOOGLE_PLACES_API_KEY
    
    # Try gnome-terminal first
    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --title="$name" -- bash -c "export GOOGLE_API_KEY='$GOOGLE_API_KEY'; export GOOGLE_PLACES_API_KEY='$GOOGLE_PLACES_API_KEY'; cd /home/user/a2a/a2a-mcp && $cmd; read -p 'Press enter to close...'"
    else
        # Fallback to running in background with environment
        echo "Running $name in background..."
        bash -c "export GOOGLE_API_KEY='$GOOGLE_API_KEY'; export GOOGLE_PLACES_API_KEY='$GOOGLE_PLACES_API_KEY'; cd /home/user/a2a/a2a-mcp && $cmd" &
    fi
}

echo "Starting all A2A-MCP services with proper environment..."
echo ""

# Start MCP Server
run_in_terminal "MCP Server" "uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100"

# Wait for MCP server to start
sleep 3

# Start agents from src directory
run_in_terminal "Orchestrator" "cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/orchestrator_agent.json --port 10101"
run_in_terminal "Planner" "cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/planner_agent.json --port 10102"
run_in_terminal "Air Ticketing" "cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/air_ticketing_agent.json --port 10103"
run_in_terminal "Hotel Booking" "cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/hotel_booking_agent.json --port 10104"
run_in_terminal "Car Rental" "cd src && uv run python -m a2a_mcp.agents --agent-card ../agent_cards/car_rental_agent.json --port 10105"

echo ""
echo "All services started!"
echo ""
echo "Test with:"
echo "  cd /home/user/a2a/a2a-mcp"
echo "  export GOOGLE_API_KEY='$GOOGLE_API_KEY'"
echo "  uv run python test_single_agent.py"