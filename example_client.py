#!/usr/bin/env python3
"""Example client to interact with A2A-MCP services."""

import asyncio
import json
from uuid import uuid4

import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard, MessageSendParams, SendStreamingMessageRequest


async def test_mcp_agent_discovery():
    """Test finding agents via MCP server."""
    from a2a_mcp.mcp import client
    
    print("=== Testing MCP Agent Discovery ===")
    
    # Connect to MCP server
    async with client.init_session('localhost', 10100, 'sse') as session:
        # Find agent for booking flights
        result = await client.find_agent(session, "I need to book a flight to London")
        agent_card = json.loads(result.content[0].text)
        print(f"Found agent: {agent_card['name']}")
        print(f"URL: {agent_card['url']}")
        
        # Get list of all agents
        resources = await client.find_resource(session, 'resource://agent_cards/list')
        data = json.loads(resources.contents[0].text)
        print(f"\nAvailable agents: {data['agent_cards']}")


async def test_orchestrator_agent():
    """Test sending a request to the orchestrator agent."""
    print("\n=== Testing Orchestrator Agent ===")
    
    # Create agent card for orchestrator
    agent_card = AgentCard(
        name="Orchestrator Agent",
        url="http://localhost:10101/",
        description="Orchestrates task execution"
    )
    
    async with httpx.AsyncClient() as http_client:
        client = A2AClient(http_client, agent_card)
        
        # Create a request
        request = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': 'Plan a trip to London from San Francisco'}],
                    'messageId': uuid4().hex,
                    'taskId': uuid4().hex,
                    'contextId': uuid4().hex,
                }
            )
        )
        
        # Send message and stream responses
        print("Sending request to orchestrator...")
        async for chunk in client.send_message_streaming(request):
            # Process streaming responses
            if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                result = chunk.root.result
                print(f"Received: {type(result).__name__}")
                
                # Handle different response types
                if hasattr(result, 'status'):
                    print(f"Status: {result.status}")
                if hasattr(result, 'artifact'):
                    print(f"Artifact: {result.artifact.name}")


async def test_direct_agent_interaction():
    """Test interacting directly with a specific agent."""
    print("\n=== Testing Direct Agent Interaction ===")
    
    # First, discover the planner agent via MCP
    from a2a_mcp.mcp import client
    
    async with client.init_session('localhost', 10100, 'sse') as session:
        # Get planner agent card
        resources = await client.find_resource(session, 'resource://agent_cards/planner_agent')
        data = json.loads(resources.contents[0].text)
        planner_card_data = data['agent_card'][0]
        
    # Create agent card from discovered data
    planner_card = AgentCard(**planner_card_data)
    
    # Connect directly to planner
    async with httpx.AsyncClient() as http_client:
        a2a_client = A2AClient(http_client, planner_card)
        
        request = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': 'I want to travel to Paris'}],
                    'messageId': uuid4().hex,
                    'taskId': uuid4().hex,
                    'contextId': uuid4().hex,
                }
            )
        )
        
        print(f"Sending request to {planner_card.name}...")
        async for chunk in a2a_client.send_message_streaming(request):
            # Process responses
            if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                print(f"Response: {chunk.root.result}")


async def test_mcp_tools():
    """Test using MCP server tools directly."""
    from a2a_mcp.mcp import client
    
    print("\n=== Testing MCP Tools ===")
    
    async with client.init_session('localhost', 10100, 'sse') as session:
        # Test query_travel_data tool
        print("Testing query_travel_data tool...")
        try:
            result = await session.call_tool(
                name='query_travel_data',
                arguments={
                    'query': "SELECT * FROM flights WHERE from_airport='SFO' LIMIT 5"
                }
            )
            print(f"Raw result: {result}")
            if result.content and len(result.content) > 0:
                text = result.content[0].text
                print(f"Result text: {text}")
                if text:
                    data = json.loads(text)
                    print(f"Found {len(data.get('results', []))} flights")
                    for flight in data.get('results', [])[:3]:
                        print(f"  - {flight}")
            else:
                print("No content in result")
        except Exception as e:
            print(f"Error with query_travel_data: {e}")
        
        # Test find_agent tool
        print("\nTesting find_agent tool...")
        try:
            result = await session.call_tool(
                name='find_agent',
                arguments={'query': 'I need to book a hotel'}
            )
            if result.content and len(result.content) > 0:
                agent_data = json.loads(result.content[0].text)
                print(f"Found agent: {agent_data.get('name', 'Unknown')}")
        except Exception as e:
            print(f"Error with find_agent: {e}")
        
        # Test query_places_data tool
        if False:  # Set to True if you have GOOGLE_PLACES_API_KEY
            places = await session.call_tool(
                name='query_places_data',
                arguments={'query': 'hotels in London'}
            )
            print(f"Places result: {places.content[0].text}")


async def main():
    """Run all tests."""
    try:
        # Make sure servers are running
        print("Make sure all servers are running:")
        print("- MCP Server on port 10100")
        print("- Orchestrator on port 10101")
        print("- Planner on port 10102")
        print("- Travel agents on ports 10103-10105\n")
        
        await test_mcp_agent_discovery()
        # await test_orchestrator_agent()  # Uncomment to test orchestrator
        # await test_direct_agent_interaction()  # Uncomment to test direct interaction
        await test_mcp_tools()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())