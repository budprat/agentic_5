#!/usr/bin/env python3
# ABOUTME: Script to start the MCP server on port 10100 with SSE transport
# ABOUTME: Loads environment and calls the serve function directly

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Now import and start the server
from a2a_mcp.mcp.server import serve

if __name__ == "__main__":
    print("Starting MCP server on port 10100 with SSE transport...")
    serve(host='localhost', port=10100, transport='sse')