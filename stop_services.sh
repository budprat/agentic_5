#!/bin/bash

echo "Stopping all A2A-MCP services..."

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $PID)..."
            kill $PID
            rm "$pid_file"
        else
            echo "$service_name not running (stale PID file)"
            rm "$pid_file"
        fi
    else
        echo "$service_name not running (no PID file)"
    fi
}

# Stop all services
stop_service "mcp-server"
stop_service "orchestrator"
stop_service "planner"
stop_service "air-ticketing"
stop_service "hotel-booking"
stop_service "car-rental"

echo "All services stopped."