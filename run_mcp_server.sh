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

echo "Starting MCP Server with API key configured..."
uv run a2a-mcp --run mcp-server --transport sse --host localhost --port 10100