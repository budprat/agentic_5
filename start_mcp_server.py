#!/usr/bin/env python3
# ABOUTME: Startup script for the Solopreneur MCP server
# ABOUTME: Properly initializes and runs the MCP server on port 10100

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

# Set required environment variables
if not os.getenv('GOOGLE_API_KEY'):
    print("❌ Error: GOOGLE_API_KEY environment variable is required")
    sys.exit(1)

try:
    from src.a2a_mcp.mcp.server import serve
    
    print("🚀 Starting Solopreneur MCP Server...")
    print("   Host: localhost")
    print("   Port: 10100")
    print("   Transport: sse")
    print("   Tools: find_agent, query_places_data, query_travel_data")
    print("          query_solopreneur_metrics, analyze_energy_patterns")
    print("          track_learning_progress, search_relevant_research")
    print("          query_knowledge_graph, monitor_technical_trends")
    print("          optimize_task_schedule, analyze_workflow_patterns")
    
    # Start the MCP server
    serve(host="localhost", port=10100, transport="sse")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Server error: {e}")
    sys.exit(1)