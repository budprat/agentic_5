#!/bin/bash

echo "A2A-MCP Services Status"
echo "======================="
echo ""

# Define services
declare -A services=(
    ["10100"]="MCP Server"
    ["10101"]="Orchestrator Agent"
    ["10102"]="Planner Agent"
    ["10103"]="Air Ticketing Agent"
    ["10104"]="Hotel Booking Agent"
    ["10105"]="Car Rental Agent"
)

# Check each service
for port in 10100 10101 10102 10103 10104 10105; do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$PID" ]; then
        STATUS="✓ Running (PID: $PID)"
    else
        STATUS="✗ Not running"
    fi
    printf "%-20s (port %d): %s\n" "${services[$port]}" "$port" "$STATUS"
done

echo ""
echo "Quick Commands:"
echo "---------------"
echo "Start all:     ./run_all_agents_fixed.sh"
echo "Start one:     ./run_agent.sh <name> <port>"
echo "Clean ports:   ./cleanup_ports.sh"
echo "View logs:     tail -f logs/*.log"
echo ""
echo "Example to start planner:"
echo "  ./run_agent.sh planner 10102"