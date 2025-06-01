#!/bin/bash

# Usage: ./run_agent.sh <agent_name> <port>
# Example: ./run_agent.sh planner 10102

AGENT_NAME=$1
PORT=$2

if [ -z "$AGENT_NAME" ] || [ -z "$PORT" ]; then
    echo "Usage: $0 <agent_name> <port>"
    echo ""
    echo "Available agents:"
    echo "  orchestrator  10101"
    echo "  planner       10102"
    echo "  air_ticketing 10103"
    echo "  hotel_booking 10104"
    echo "  car_rental    10105"
    exit 1
fi

# Map agent names to card files
case $AGENT_NAME in
    orchestrator)
        CARD="orchestrator_agent.json"
        ;;
    planner)
        CARD="planner_agent.json"
        ;;
    air_ticketing)
        CARD="air_ticketing_agent.json"
        ;;
    hotel_booking)
        CARD="hotel_booking_agent.json"
        ;;
    car_rental)
        CARD="car_rental_agent.json"
        ;;
    *)
        echo "Unknown agent: $AGENT_NAME"
        exit 1
        ;;
esac

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

echo "Starting $AGENT_NAME agent on port $PORT..."
echo "API Key: ${GOOGLE_API_KEY:0:20}..."
echo ""

# Run the agent
cd src && GOOGLE_API_KEY="$GOOGLE_API_KEY" uv run python -m a2a_mcp.agents --agent-card ../agent_cards/$CARD --port $PORT