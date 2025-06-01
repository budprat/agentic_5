#!/usr/bin/env python3
"""Interactive client for A2A-MCP system."""

import asyncio
import json
import os
from uuid import uuid4
from typing import Optional
import sys

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
                                   context_id: Optional[str] = None, 
                                   stream_output: bool = True) -> list:
        """Send a message to an agent and collect responses."""
        if not context_id:
            context_id = uuid4().hex
        
        responses = []
        
        async with httpx.AsyncClient(timeout=60.0) as http_client:
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
            
            print(f"\n→ Sending to {agent_card.name}: {message}")
            print("← Receiving responses...\n")
            
            async for chunk in a2a_client.send_message_streaming(request):
                if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                    result = chunk.root.result
                    response_data = {
                        'type': type(result).__name__,
                        'data': result
                    }
                    responses.append(response_data)
                    
                    if stream_output:
                        # Display different types of responses
                        if hasattr(result, 'status'):
                            if hasattr(result.status, 'state'):
                                print(f"  Status: {result.status.state}")
                            if hasattr(result.status, 'message'):
                                if hasattr(result.status.message, 'parts'):
                                    for part in result.status.message.parts:
                                        if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                            print(f"  Message: {part.root.text}")
                        elif hasattr(result, 'artifact'):
                            print(f"  Artifact: {result.artifact.name}")
                        else:
                            print(f"  {type(result).__name__}")
        
        return responses


async def interactive_menu():
    """Interactive menu for A2A-MCP client."""
    client = A2AMCPClient()
    context_id = uuid4().hex  # Maintain context across interactions
    
    print("A2A-MCP Interactive Client")
    print("=" * 50)
    print("\nMake sure all services are running (use ./status.sh to check)")
    print("=" * 50)
    
    while True:
        print("\n\nOptions:")
        print("1. List all agents")
        print("2. Find agent for a task")
        print("3. Send message to orchestrator")
        print("4. Send message to specific agent")
        print("5. Query travel database (SQL)")
        print("6. Query travel database (Natural language)")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        try:
            if choice == '1':
                # List all agents
                print("\nFetching all agents...")
                agents = await client.get_all_agents()
                print("\nAvailable Agents:")
                for i, agent in enumerate(agents, 1):
                    print(f"{i}. {agent['name']} - {agent['description']}")
                    print(f"   URL: {agent['url']}")
                    if 'skills' in agent:
                        skills = [s['name'] for s in agent['skills']]
                        print(f"   Skills: {', '.join(skills)}")
                    print()
            
            elif choice == '2':
                # Find agent for task
                query = input("\nWhat task do you need help with? ").strip()
                if query:
                    print(f"\nSearching for agent to handle: '{query}'")
                    agent = await client.discover_agent(query)
                    print(f"\nFound: {agent.name}")
                    print(f"Description: {agent.description}")
                    print(f"URL: {agent.url}")
            
            elif choice == '3':
                # Send to orchestrator
                message = input("\nEnter your message for the orchestrator: ").strip()
                if message:
                    # Get orchestrator from agent list
                    agents = await client.get_all_agents()
                    orchestrator_data = next((a for a in agents if 'orchestrator' in a['name'].lower()), None)
                    if orchestrator_data:
                        orchestrator = AgentCard(**orchestrator_data)
                        print("\nNote: This will trigger the full workflow (Planner → Task Agents → Summary)")
                        await client.send_message_to_agent(orchestrator, message, context_id)
                    else:
                        print("Error: Orchestrator agent not found")
            
            elif choice == '4':
                # Send to specific agent
                agents = await client.get_all_agents()
                print("\nAvailable Agents:")
                for i, agent in enumerate(agents, 1):
                    print(f"{i}. {agent['name']}")
                
                agent_choice = input("\nSelect agent number: ").strip()
                try:
                    agent_idx = int(agent_choice) - 1
                    if 0 <= agent_idx < len(agents):
                        selected_agent = agents[agent_idx]
                        agent_card = AgentCard(**selected_agent)
                        
                        message = input(f"\nEnter message for {selected_agent['name']}: ").strip()
                        if message:
                            await client.send_message_to_agent(agent_card, message, context_id)
                    else:
                        print("Invalid agent number")
                except ValueError:
                    print("Invalid input")
            
            elif choice == '5':
                # SQL query
                print("\nExample queries:")
                print("- SELECT * FROM flights WHERE from_airport='SFO' LIMIT 5")
                print("- SELECT * FROM hotels WHERE city='London' ORDER BY price_per_night")
                print("- SELECT * FROM rental_cars WHERE type_of_car='SUV'")
                
                query = input("\nEnter SQL query: ").strip()
                if query:
                    result = await client.query_travel_data(query)
                    print(f"\nResults ({len(result.get('results', []))} rows):")
                    for row in result.get('results', [])[:10]:  # Show first 10
                        print(f"  {row}")
                    if len(result.get('results', [])) > 10:
                        print(f"  ... and {len(result.get('results', [])) - 10} more rows")
            
            elif choice == '6':
                # Natural language query
                query = input("\nWhat would you like to know about travel options? ").strip()
                if query:
                    # Find appropriate agent
                    agent = await client.discover_agent(query)
                    print(f"\nUsing {agent.name} to answer your question...")
                    await client.send_message_to_agent(agent, query, context_id)
            
            elif choice == '7':
                print("\nGoodbye!")
                break
            
            else:
                print("Invalid option. Please select 1-7.")
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            continue
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point."""
    # Set up environment
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check for command line usage
    if len(sys.argv) > 1:
        # Direct command mode
        command = sys.argv[1].lower()
        client = A2AMCPClient()
        
        if command == "agents":
            # List all agents
            agents = await client.get_all_agents()
            for agent in agents:
                print(f"{agent['name']} - {agent['url']}")
        
        elif command == "find" and len(sys.argv) > 2:
            # Find agent for task
            query = " ".join(sys.argv[2:])
            agent = await client.discover_agent(query)
            print(f"Found: {agent.name} at {agent.url}")
        
        elif command == "ask" and len(sys.argv) > 2:
            # Ask orchestrator
            message = " ".join(sys.argv[2:])
            agents = await client.get_all_agents()
            orchestrator_data = next((a for a in agents if 'orchestrator' in a['name'].lower()), None)
            if orchestrator_data:
                orchestrator = AgentCard(**orchestrator_data)
                await client.send_message_to_agent(orchestrator, message)
            else:
                print("Error: Orchestrator agent not found")
        
        elif command == "sql" and len(sys.argv) > 2:
            # SQL query
            query = " ".join(sys.argv[2:])
            result = await client.query_travel_data(query)
            for row in result.get('results', []):
                print(row)
        
        else:
            print("Usage:")
            print("  python interactive_client.py              # Interactive mode")
            print("  python interactive_client.py agents       # List all agents")
            print("  python interactive_client.py find <task>  # Find agent for task")
            print("  python interactive_client.py ask <query>  # Ask orchestrator")
            print("  python interactive_client.py sql <query>  # SQL query")
    else:
        # Interactive mode
        await interactive_menu()


if __name__ == "__main__":
    asyncio.run(main())