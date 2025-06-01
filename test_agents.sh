#!/bin/bash

echo "=== Testing A2A-MCP Services ==="

# Test MCP Server SSE endpoint
echo -e "\n1. Testing MCP Server SSE connection:"
curl -N http://localhost:10100/sse 2>/dev/null | head -n 5

# Test agent health endpoints (if available)
echo -e "\n2. Testing Agent Endpoints:"
for port in 10101 10102 10103 10104 10105; do
    echo -n "Port $port: "
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/ | grep -q "200\|404"; then
        echo "Responding"
    else
        echo "Not responding"
    fi
done

# Test MCP tools via HTTP (example)
echo -e "\n3. Testing MCP Tool Discovery:"
# This would require proper MCP client implementation

echo -e "\nFor full testing, use the Python client examples."