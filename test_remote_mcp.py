#!/usr/bin/env python3
"""Test script for remote MCP connectivity."""

import asyncio
import json
import logging
from src.a2a_mcp.mcp.remote_mcp_connector import RemoteMCPRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_remote_mcp():
    """Test remote MCP connectivity."""
    print("Testing Remote MCP Connectivity\n")
    print("=" * 50)
    
    # Create registry
    registry = RemoteMCPRegistry()
    
    # List registered servers
    print("\n1. Registered Remote MCP Servers:")
    print("-" * 30)
    for name, server in registry.connector.servers.items():
        print(f"  - {name}: {server.transport} transport")
        if server.description:
            print(f"    Description: {server.description}")
    
    if not registry.connector.servers:
        print("  No remote servers registered.")
        return
    
    # Test connectivity to each server
    print("\n2. Testing Connectivity:")
    print("-" * 30)
    
    for server_name in registry.connector.servers:
        print(f"\n  Testing {server_name}...")
        try:
            async with registry.connector.connect_server(server_name) as session:
                print(f"  ✓ Connected to {server_name}")
                
                # Get available tools
                tools = registry.connector.get_available_tools(server_name)
                if tools.get(server_name):
                    print(f"  ✓ Found {len(tools[server_name])} tools")
                    for tool in tools[server_name][:3]:  # Show first 3 tools
                        if hasattr(tool, 'name'):
                            print(f"    - {tool.name}")
                else:
                    print(f"  ✓ No tools available")
                    
        except Exception as e:
            print(f"  ✗ Failed to connect: {str(e)}")
    
    print("\n3. Testing Cross-Server Workflow:")
    print("-" * 30)
    
    # Example workflow if we have multiple servers
    if len(registry.connector.servers) > 1:
        print("  Multiple servers available - could execute cross-server workflows")
    else:
        print("  Only one server available - cross-server workflows not applicable")
    
    print("\n" + "=" * 50)
    print("Remote MCP Connectivity Test Complete")


if __name__ == "__main__":
    asyncio.run(test_remote_mcp())