#!/bin/bash

echo "Checking and cleaning up A2A-MCP ports..."
echo "========================================="

# Define ports used by the system
PORTS=(10100 10101 10102 10103 10104 10105)
NAMES=("MCP Server" "Orchestrator" "Planner" "Air Ticketing" "Hotel Booking" "Car Rental")

for i in ${!PORTS[@]}; do
    PORT=${PORTS[$i]}
    NAME=${NAMES[$i]}
    
    echo -n "Port $PORT ($NAME): "
    
    # Check if port is in use
    PID=$(lsof -ti :$PORT)
    
    if [ -z "$PID" ]; then
        echo "✓ Free"
    else
        echo "✗ In use by PID $PID"
        read -p "  Kill process? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $PID
            sleep 1
            # Check if process is still running
            if kill -0 $PID 2>/dev/null; then
                echo "  Process still running, forcing kill..."
                kill -9 $PID
            fi
            echo "  Process killed"
        fi
    fi
done

echo ""
echo "Port cleanup complete!"

# Also cleanup any stale pid files
if [ -d "logs" ]; then
    echo ""
    echo "Cleaning up stale PID files..."
    rm -f logs/*.pid
    echo "Done!"
fi