#!/bin/bash

# Check if .env file exists and load it
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set!"
    echo "Please set it in the .env file or as an environment variable"
    exit 1
fi

echo "Starting all A2A-MCP services..."

# Create logs directory
mkdir -p logs

# Start MCP Server
echo "Starting MCP Server on port 10100..."
nohup uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100 > logs/mcp-server.log 2>&1 &
echo $! > logs/mcp-server.pid

# Wait for MCP server to start
sleep 3

# Start Orchestrator Agent
echo "Starting Orchestrator Agent on port 10101..."
nohup uv run src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10101 > logs/orchestrator.log 2>&1 &
echo $! > logs/orchestrator.pid

# Start Planner Agent
echo "Starting Planner Agent on port 10102..."
nohup uv run src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10102 > logs/planner.log 2>&1 &
echo $! > logs/planner.pid

# Start Air Ticketing Agent
echo "Starting Air Ticketing Agent on port 10103..."
nohup uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103 > logs/air-ticketing.log 2>&1 &
echo $! > logs/air-ticketing.pid

# Start Hotel Booking Agent
echo "Starting Hotel Booking Agent on port 10104..."
nohup uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104 > logs/hotel-booking.log 2>&1 &
echo $! > logs/hotel-booking.pid

# Start Car Rental Agent
echo "Starting Car Rental Agent on port 10105..."
nohup uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105 > logs/car-rental.log 2>&1 &
echo $! > logs/car-rental.pid

echo ""
echo "All services started! Logs are in the 'logs' directory."
echo ""
echo "Services running on:"
echo "  - MCP Server: http://localhost:10100 (log: logs/mcp-server.log)"
echo "  - Orchestrator Agent: http://localhost:10101 (log: logs/orchestrator.log)"
echo "  - Planner Agent: http://localhost:10102 (log: logs/planner.log)"
echo "  - Air Ticketing Agent: http://localhost:10103 (log: logs/air-ticketing.log)"
echo "  - Hotel Booking Agent: http://localhost:10104 (log: logs/hotel-booking.log)"
echo "  - Car Rental Agent: http://localhost:10105 (log: logs/car-rental.log)"
echo ""
echo "To stop all services, run: ./stop_services.sh"
echo "To view logs, run: tail -f logs/*.log"