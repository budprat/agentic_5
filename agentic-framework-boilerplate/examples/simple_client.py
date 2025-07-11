#!/usr/bin/env python3
# ABOUTME: Simple example client demonstrating how to interact with A2A MCP agents
# ABOUTME: Shows basic request/response patterns and agent communication

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional


class A2AClient:
    """Simple client for interacting with A2A MCP agents."""
    
    def __init__(self, base_url: str = "http://localhost:10100"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def send_message(self, agent_id: str, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message to an agent and get response.
        
        Args:
            agent_id: ID of the target agent
            message: Message content to send
            metadata: Optional metadata for the request
            
        Returns:
            Agent response as dictionary
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async with statement.")
        
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "agent_id": agent_id,
                "message": {
                    "role": "user",
                    "content": message
                },
                "metadata": metadata or {}
            }
        }
        
        try:
            async with self.session.post(self.base_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                else:
                    error_text = await response.text()
                    raise Exception(f"Request failed ({response.status}): {error_text}")
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
    
    async def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get information about a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent information including capabilities
        """
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "agent/info",
            "params": {
                "agent_id": agent_id
            }
        }
        
        async with self.session.post(self.base_url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("result", {})
            else:
                raise Exception(f"Failed to get agent info: {response.status}")
    
    async def list_agents(self) -> list:
        """List all available agents in the system.
        
        Returns:
            List of agent information dictionaries
        """
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "system/list_agents",
            "params": {}
        }
        
        async with self.session.post(self.base_url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("result", {}).get("agents", [])
            else:
                raise Exception(f"Failed to list agents: {response.status}")


async def example_usage():
    """Example of how to use the A2A client."""
    
    # Create client instance
    async with A2AClient() as client:
        print("🚀 A2A MCP Client Example")
        print("=" * 50)
        
        try:
            # List available agents
            print("\n📋 Listing available agents...")
            agents = await client.list_agents()
            
            if not agents:
                print("No agents found. Make sure the system is running.")
                return
            
            print(f"Found {len(agents)} agents:")
            for agent in agents:
                print(f"  - {agent['name']} ({agent['agent_id']})")
                print(f"    Capabilities: {', '.join(agent.get('capabilities', []))}")
            
            # Send a message to the first agent
            if agents:
                first_agent = agents[0]
                print(f"\n💬 Sending message to {first_agent['name']}...")
                
                response = await client.send_message(
                    agent_id=first_agent['agent_id'],
                    message="Hello! Can you tell me about your capabilities?",
                    metadata={"request_type": "capability_inquiry"}
                )
                
                print(f"\n📨 Response from {first_agent['name']}:")
                print(json.dumps(response, indent=2))
                
            # Example of getting specific agent info
            print("\n🔍 Getting detailed info about master oracle...")
            try:
                oracle_info = await client.get_agent_info("master_oracle")
                print(json.dumps(oracle_info, indent=2))
            except Exception as e:
                print(f"Could not get oracle info: {e}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def interactive_chat():
    """Interactive chat mode with agents."""
    
    async with A2AClient() as client:
        print("🤖 A2A MCP Interactive Chat")
        print("=" * 50)
        print("Type 'exit' to quit, 'list' to see agents, or 'switch <agent_id>' to change agent")
        print()
        
        # Get initial agent list
        agents = await client.list_agents()
        if not agents:
            print("No agents available. Exiting.")
            return
        
        # Start with first agent
        current_agent = agents[0]
        print(f"💬 Chatting with: {current_agent['name']}")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input(f"You > ").strip()
                
                if user_input.lower() == 'exit':
                    print("Goodbye! 👋")
                    break
                
                elif user_input.lower() == 'list':
                    print("\nAvailable agents:")
                    for agent in agents:
                        marker = "→" if agent['agent_id'] == current_agent['agent_id'] else " "
                        print(f"{marker} {agent['name']} ({agent['agent_id']})")
                    print()
                    continue
                
                elif user_input.lower().startswith('switch '):
                    agent_id = user_input[7:].strip()
                    # Find agent
                    found = False
                    for agent in agents:
                        if agent['agent_id'] == agent_id:
                            current_agent = agent
                            print(f"\n✅ Switched to: {agent['name']}\n")
                            found = True
                            break
                    if not found:
                        print(f"❌ Agent '{agent_id}' not found\n")
                    continue
                
                # Send message to current agent
                print(f"\n{current_agent['name']} > ", end="", flush=True)
                response = await client.send_message(
                    agent_id=current_agent['agent_id'],
                    message=user_input
                )
                
                # Display response
                if isinstance(response, dict) and 'content' in response:
                    print(response['content'])
                else:
                    print(json.dumps(response, indent=2))
                print()
                
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        # Run interactive chat mode
        asyncio.run(interactive_chat())
    else:
        # Run example usage
        asyncio.run(example_usage())