#!/bin/bash
# ABOUTME: Stop script for the A2A MCP Framework
# ABOUTME: Gracefully shuts down all agents and the MCP server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Stopping A2A MCP Framework${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to stop a process
stop_process() {
    local pidfile=$1
    local name=$2
    
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        if kill -0 $PID 2>/dev/null; then
            echo -e "Stopping $name (PID: $PID)..."
            kill $PID
            sleep 1
            
            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                echo -e "${YELLOW}Force stopping $name...${NC}"
                kill -9 $PID
            fi
            
            echo -e "${GREEN}✓ $name stopped${NC}"
        else
            echo -e "${YELLOW}$name was not running${NC}"
        fi
        rm -f "$pidfile"
    else
        echo -e "${YELLOW}No PID file found for $name${NC}"
    fi
}

# Stop all agents first
echo -e "${YELLOW}Stopping agents...${NC}"
for pidfile in *.pid; do
    if [ -f "$pidfile" ] && [ "$pidfile" != "mcp_server.pid" ]; then
        agent_name=$(basename "$pidfile" .pid | tr '_' ' ')
        stop_process "$pidfile" "$agent_name"
    fi
done

# Stop MCP server last
echo ""
echo -e "${YELLOW}Stopping MCP server...${NC}"
stop_process "mcp_server.pid" "MCP Server"

# Additional cleanup
echo ""
echo -e "${YELLOW}Additional cleanup...${NC}"

# Kill any remaining processes
if pgrep -f "python.*a2a_mcp" > /dev/null; then
    echo "Cleaning up remaining A2A MCP processes..."
    pkill -f "python.*a2a_mcp" || true
fi

echo -e "${GREEN}✓ All services stopped${NC}"
echo ""
echo -e "${BLUE}A2A MCP Framework shutdown complete${NC}"