#!/usr/bin/env python3
"""Test a single agent interaction without needing all services."""

import asyncio
import json
import os
from uuid import uuid4

# Set API key from .env
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.startswith('GOOGLE_API_KEY='):
                os.environ['GOOGLE_API_KEY'] = line.split('=', 1)[1].strip()

async def test_mcp_only():
    """Test just MCP server functionality."""
    from a2a_mcp.mcp import client as mcp_client
    
    print("Testing MCP Server Only")
    print("=" * 50)
    
    try:
        # Connect to MCP
        async with mcp_client.init_session('localhost', 10100, 'sse') as session:
            print("✓ Connected to MCP server")
            
            # 1. List all agents
            print("\n1. Available agents:")
            resources = await mcp_client.find_resource(session, 'resource://agent_cards/list')
            data = json.loads(resources.contents[0].text)
            for card_uri in data['agent_cards']:
                print(f"   - {card_uri}")
            
            # 2. Find agent for specific task
            print("\n2. Finding agent for 'book a flight':")
            result = await mcp_client.find_agent(session, "I need to book a flight")
            agent = json.loads(result.content[0].text)
            print(f"   Found: {agent['name']}")
            print(f"   URL: {agent['url']}")
            print(f"   Skills: {[s['name'] for s in agent.get('skills', [])]}")
            
            # 3. Query travel data
            print("\n3. Querying flight data:")
            result = await session.call_tool(
                name='query_travel_data',
                arguments={
                    'query': "SELECT carrier, flight_number, ticket_class, price FROM flights WHERE from_airport='SFO' AND to_airport='LHR' ORDER BY price LIMIT 5"
                }
            )
            flights = json.loads(result.content[0].text)
            print("   Cheapest flights SFO → LHR:")
            for flight in flights.get('results', []):
                print(f"   - {flight['carrier']} {flight['flight_number']} ({flight['ticket_class']}): ${flight['price']}")
            
            # 4. Query hotel data
            print("\n4. Querying hotel data:")
            result = await session.call_tool(
                name='query_travel_data',
                arguments={
                    'query': "SELECT name, room_type, price_per_night FROM hotels WHERE city='London' ORDER BY price_per_night DESC LIMIT 5"
                }
            )
            hotels = json.loads(result.content[0].text)
            print("   Most expensive hotels in London:")
            for hotel in hotels.get('results', []):
                print(f"   - {hotel['name']} ({hotel['room_type']}): ${hotel['price_per_night']}/night")
            
            print("\n✓ All MCP tests passed!")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_with_mock_agent():
    """Test agent interaction with a mock response."""
    print("\n\nMock Agent Interaction Example")
    print("=" * 50)
    
    # This shows what the interaction would look like
    print("1. Client discovers agent via MCP")
    print("2. Client sends message to agent URL")
    print("3. Agent processes and responds with streaming events")
    print("\nExample flow:")
    print("   → User: 'Book a flight from SFO to London'")
    print("   ← Agent: TaskStatusUpdateEvent (working)")
    print("   ← Agent: 'What dates would you like to travel?'")
    print("   → User: 'June 15-20, 2025'")
    print("   ← Agent: 'What class would you prefer?'")
    print("   → User: 'Business class'")
    print("   ← Agent: TaskArtifactUpdateEvent (flight details)")
    print("   ← Agent: TaskStatusUpdateEvent (completed)")

if __name__ == "__main__":
    print("A2A-MCP Connection Test")
    print("This tests MCP server connectivity without needing all agents running.\n")
    
    asyncio.run(test_mcp_only())
    asyncio.run(test_with_mock_agent())