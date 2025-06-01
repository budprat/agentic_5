#!/bin/bash

# Check if .env file exists
if [ -f .env ]; then
    # Load environment variables from .env file
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set!"
    echo "Please set it in the .env file or as an environment variable"
    echo "Example: export GOOGLE_API_KEY='your-api-key-here'"
    exit 1
fi

echo "Starting all A2A-MCP services..."

# Function to run a command in a new terminal
run_in_terminal() {
    local title=$1
    local command=$2
    
    # Try different terminal emulators
    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --title="$title" -- bash -c "$command; read -p 'Press enter to close...'"
    elif command -v xterm >/dev/null 2>&1; then
        xterm -title "$title" -e bash -c "$command; read -p 'Press enter to close...'"
    elif command -v konsole >/dev/null 2>&1; then
        konsole --title="$title" -e bash -c "$command; read -p 'Press enter to close...'"
    else
        # Fallback: run in background
        echo "Starting $title in background..."
        eval "$command" &
    fi
}

# Start MCP Server
run_in_terminal "MCP Server" "cd /home/user/a2a/a2a-mcp && uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100"

# Wait a bit for MCP server to start
sleep 3

# Start Orchestrator Agent
run_in_terminal "Orchestrator Agent" "cd /home/user/a2a/a2a-mcp && uv run src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10101"

# Start Planner Agent
run_in_terminal "Planner Agent" "cd /home/user/a2a/a2a-mcp && uv run src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10102"

# Start Air Ticketing Agent
run_in_terminal "Air Ticketing Agent" "cd /home/user/a2a/a2a-mcp && uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103"

# Start Hotel Booking Agent
run_in_terminal "Hotel Booking Agent" "cd /home/user/a2a/a2a-mcp && uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104"

# Start Car Rental Agent
run_in_terminal "Car Rental Agent" "cd /home/user/a2a/a2a-mcp && uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105"

echo "All services started!"
echo "Services running on:"
echo "  - MCP Server: http://localhost:10100"
echo "  - Orchestrator Agent: http://localhost:10101"
echo "  - Planner Agent: http://localhost:10102"
echo "  - Air Ticketing Agent: http://localhost:10103"
echo "  - Hotel Booking Agent: http://localhost:10104"
echo "  - Car Rental Agent: http://localhost:10105"