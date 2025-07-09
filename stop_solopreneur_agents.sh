#!/bin/bash
# Stop all solopreneur agents

echo "🛑 Stopping Solopreneur Oracle System..."

# Kill all agent processes
if [ -f .agent_pids ]; then
    echo "Stopping agents..."
    while read pid; do
        if kill $pid 2>/dev/null; then
            echo "  ✓ Stopped agent PID: $pid"
        fi
    done < .agent_pids
    rm .agent_pids
fi

# Stop MCP server if we started it
if [ -f .mcp_pid ]; then
    MCP_PID=$(cat .mcp_pid)
    if kill $MCP_PID 2>/dev/null; then
        echo "  ✓ Stopped MCP Server (PID: $MCP_PID)"
    fi
    rm .mcp_pid
fi

echo "✅ All agents stopped"