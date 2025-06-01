#!/usr/bin/env python3
"""Comprehensive client examples for A2A-MCP system."""

import asyncio
import json
from uuid import uuid4
from typing import Optional

import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard, MessageSendParams, SendStreamingMessageRequest


class A2AMCPClient:
    """Client for interacting with A2A-MCP system."""
    
    def __init__(self, mcp_host='localhost', mcp_port=10100):
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        self.mcp_url = f'http://{mcp_host}:{mcp_port}/sse'
    
    async def discover_agent(self, query: str) -> Optional[AgentCard]:
        """Discover an agent via MCP based on query."""
        from a2a_mcp.mcp import client
        
        async with client.init_session(self.mcp_host, self.mcp_port, 'sse') as session:
            result = await client.find_agent(session, query)
            agent_data = json.loads(result.content[0].text)
            return AgentCard(**agent_data)
    
    async def get_all_agents(self) -> list:
        """Get list of all available agents."""
        from a2a_mcp.mcp import client
        
        async with client.init_session(self.mcp_host, self.mcp_port, 'sse') as session:
            resources = await client.find_resource(session, 'resource://agent_cards/list')
            data = json.loads(resources.contents[0].text)
            
            agents = []
            for card_uri in data['agent_cards']:
                card_data = await client.find_resource(session, card_uri)
                card_json = json.loads(card_data.contents[0].text)
                agents.append(card_json['agent_card'][0])
            
            return agents
    
    async def query_travel_data(self, sql_query: str) -> dict:
        """Query travel database via MCP."""
        from a2a_mcp.mcp import client
        
        async with client.init_session(self.mcp_host, self.mcp_port, 'sse') as session:
            result = await session.call_tool(
                name='query_travel_data',
                arguments={'query': sql_query}
            )
            return json.loads(result.content[0].text)
    
    async def send_message_to_agent(self, agent_card: AgentCard, message: str, 
                                   context_id: Optional[str] = None) -> list:
        """Send a message to an agent and collect responses."""
        if not context_id:
            context_id = uuid4().hex
        
        responses = []
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            a2a_client = A2AClient(http_client, agent_card)
            
            request = SendStreamingMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(
                    message={
                        'role': 'user',
                        'parts': [{'kind': 'text', 'text': message}],
                        'messageId': uuid4().hex,
                        'taskId': uuid4().hex,
                        'contextId': context_id,
                    }
                )
            )
            
            async for chunk in a2a_client.send_message_streaming(request):
                if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                    result = chunk.root.result
                    responses.append({
                        'type': type(result).__name__,
                        'data': str(result)[:200] + '...' if len(str(result)) > 200 else str(result)
                    })
        
        return responses


async def example_1_discover_and_query():
    """Example 1: Discover agents and query data."""
    print("=== Example 1: Agent Discovery and Data Query ===\n")
    
    client = A2AMCPClient()
    
    # Discover agent for flight booking
    print("1. Discovering agent for flight booking...")
    agent = await client.discover_agent("I need to book a flight to London")
    print(f"   Found: {agent.name} at {agent.url}")
    
    # Get all available agents
    print("\n2. Getting all available agents...")
    all_agents = await client.get_all_agents()
    for agent_data in all_agents:
        print(f"   - {agent_data['name']}: {agent_data['description']}")
    
    # Query travel data
    print("\n3. Querying available flights...")
    flights = await client.query_travel_data(
        "SELECT carrier, flight_number, ticket_class, price FROM flights WHERE from_airport='SFO' AND to_airport='LHR'"
    )
    print("   Available flights:")
    for flight in flights.get('results', [])[:5]:
        print(f"   - {flight['carrier']} {flight['flight_number']} ({flight['ticket_class']}): ${flight['price']}")


async def example_2_plan_trip():
    """Example 2: Use orchestrator to plan a trip."""
    print("\n=== Example 2: Trip Planning with Orchestrator ===\n")
    
    client = A2AMCPClient()
    
    # Get orchestrator agent
    orchestrator = AgentCard(
        name="Orchestrator Agent",
        url="http://localhost:10101/",
        description="Orchestrates task execution"
    )
    
    print("Sending trip request to orchestrator...")
    print("(This will trigger the full workflow: Planner → Task Agents → Summary)")
    
    # Note: This is a simplified example. In reality, you'd need to handle
    # the streaming responses and potential user input requests
    responses = await client.send_message_to_agent(
        orchestrator,
        "Plan a business trip from San Francisco to London for June 15-20, 2025. Budget is $5000."
    )
    
    print("\nResponse flow:")
    for i, response in enumerate(responses[:10]):  # Show first 10 responses
        print(f"{i+1}. {response['type']}: {response['data']}")
    
    if len(responses) > 10:
        print(f"... and {len(responses) - 10} more responses")


async def example_3_direct_agent_interaction():
    """Example 3: Direct interaction with specific agents."""
    print("\n=== Example 3: Direct Agent Interaction ===\n")
    
    client = A2AMCPClient()
    
    # Discover hotel booking agent
    print("1. Finding hotel booking agent...")
    hotel_agent = await client.discover_agent("I need to book a hotel")
    print(f"   Found: {hotel_agent.name}")
    
    # Send direct query to hotel agent
    print("\n2. Querying hotel agent directly...")
    responses = await client.send_message_to_agent(
        hotel_agent,
        "I need a suite in London for June 15-20"
    )
    
    print("   Agent responses:")
    for response in responses[:5]:
        print(f"   - {response['type']}")


async def example_4_mcp_tools():
    """Example 4: Using MCP tools directly."""
    print("\n=== Example 4: Direct MCP Tool Usage ===\n")
    
    from a2a_mcp.mcp import client as mcp_client
    
    async with mcp_client.init_session('localhost', 10100, 'sse') as session:
        # List available tools
        print("Available MCP tools:")
        # Note: MCP doesn't have a list_tools method in this implementation,
        # but we know these are available:
        tools = ['find_agent', 'query_travel_data', 'query_places_data']
        for tool in tools:
            print(f"  - {tool}")
        
        # Example: Find cheapest flights
        print("\n1. Finding cheapest flights SFO to LHR...")
        result = await session.call_tool(
            name='query_travel_data',
            arguments={
                'query': """
                    SELECT carrier, flight_number, ticket_class, price 
                    FROM flights 
                    WHERE from_airport='SFO' AND to_airport='LHR' 
                    ORDER BY price ASC 
                    LIMIT 3
                """
            }
        )
        data = json.loads(result.content[0].text)
        for flight in data.get('results', []):
            print(f"   - {flight['carrier']} {flight['flight_number']}: ${flight['price']}")
        
        # Example: Find luxury hotels
        print("\n2. Finding luxury hotels in London...")
        result = await session.call_tool(
            name='query_travel_data',
            arguments={
                'query': """
                    SELECT name, room_type, price_per_night 
                    FROM hotels 
                    WHERE city='London' AND hotel_type='HOTEL' 
                    ORDER BY price_per_night DESC 
                    LIMIT 3
                """
            }
        )
        data = json.loads(result.content[0].text)
        for hotel in data.get('results', []):
            print(f"   - {hotel['name']} ({hotel['room_type']}): ${hotel['price_per_night']}/night")


async def main():
    """Run all examples."""
    print("A2A-MCP Client Examples")
    print("=" * 50)
    print("\nMake sure all services are running:")
    print("- MCP Server on port 10100")
    print("- Orchestrator on port 10101") 
    print("- All other agents on ports 10102-10105")
    print("=" * 50)
    
    try:
        # Run examples
        await example_1_discover_and_query()
        await example_4_mcp_tools()
        await example_3_direct_agent_interaction()
        
        # Example 2 is commented out as it requires all agents to be running
        # and may take a long time to complete
        # await example_2_plan_trip()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())