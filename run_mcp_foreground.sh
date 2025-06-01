#!/bin/bash
cd /home/user/a2a/a2a-mcp

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting MCP Server in foreground..."
echo "Press Ctrl+C to stop"
echo ""

uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100