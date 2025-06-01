#!/usr/bin/env python3
"""Check which A2A-MCP services are running."""

import asyncio
import socket
import sys
sys.path.insert(0, '/home/user/a2a/a2a-mcp/.venv/lib/python3.13/site-packages')

import httpx
from a2a_mcp.mcp import client as mcp_client

async def check_port(host, port):
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()

async def check_http_endpoint(url):
    """Check if HTTP endpoint is responding."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(url)
            return response.status_code < 500
    except:
        return False

async def check_mcp_server(host='localhost', port=10100):
    """Check if MCP server is running and responsive."""
    try:
        async with mcp_client.init_session(host, port, 'sse') as session:
            # Try to list resources
            result = await mcp_client.find_resource(session, 'resource://agent_cards/list')
            return True
    except Exception as e:
        return False

async def main():
    """Check all services."""
    print("Checking A2A-MCP Services Status")
    print("=" * 50)
    
    services = [
        ("MCP Server", "localhost", 10100, "http://localhost:10100/sse"),
        ("Orchestrator Agent", "localhost", 10101, "http://localhost:10101/"),
        ("Planner Agent", "localhost", 10102, "http://localhost:10102/"),
        ("Air Ticketing Agent", "localhost", 10103, "http://localhost:10103/"),
        ("Hotel Booking Agent", "localhost", 10104, "http://localhost:10104/"),
        ("Car Rental Agent", "localhost", 10105, "http://localhost:10105/"),
    ]
    
    all_running = True
    
    for name, host, port, url in services:
        port_open = await check_port(host, port)
        
        if port_open:
            if name == "MCP Server":
                mcp_responsive = await check_mcp_server(host, port)
                status = "✓ Running (MCP responsive)" if mcp_responsive else "⚠ Running (MCP not responsive)"
            else:
                http_ok = await check_http_endpoint(url)
                status = "✓ Running" if http_ok else "⚠ Port open but not responding"
        else:
            status = "✗ Not running"
            all_running = False
        
        print(f"{name:<20} (port {port}): {status}")
    
    print("\n" + "=" * 50)
    
    if not all_running:
        print("\nSome services are not running!")
        print("\nTo start all services, run:")
        print("  ./start_services.sh")
        print("\nOr start them individually:")
        print("  # Terminal 1 - MCP Server:")
        print("  uv run a2a-mcp --run mcp-server --transport sse")
        print("\n  # Terminal 2 - Orchestrator:")
        print("  uv run src/a2a_mcp/agents/ --agent-card agent_cards/orchestrator_agent.json --port 10101")
        print("\n  # Terminal 3 - Planner:")
        print("  uv run src/a2a_mcp/agents/ --agent-card agent_cards/planner_agent.json --port 10102")
        print("\n  # Terminal 4 - Air Ticketing:")
        print("  uv run src/a2a_mcp/agents/ --agent-card agent_cards/air_ticketing_agent.json --port 10103")
        print("\n  # Terminal 5 - Hotel Booking:")
        print("  uv run src/a2a_mcp/agents/ --agent-card agent_cards/hotel_booking_agent.json --port 10104")
        print("\n  # Terminal 6 - Car Rental:")
        print("  uv run src/a2a_mcp/agents/ --agent-card agent_cards/car_rental_agent.json --port 10105")
    else:
        print("\nAll services are running! You can now run the client examples.")
    
    # Check if .env file exists
    import os
    if not os.path.exists('.env'):
        print("\n⚠ Warning: .env file not found!")
        print("Create one with: echo 'GOOGLE_API_KEY=your-key-here' > .env")
    else:
        if os.getenv('GOOGLE_API_KEY'):
            print("\n✓ GOOGLE_API_KEY is set")
        else:
            print("\n⚠ GOOGLE_API_KEY not found in environment")
            print("Make sure it's set in .env file")

if __name__ == "__main__":
    asyncio.run(main())