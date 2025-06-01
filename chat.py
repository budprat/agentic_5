#!/usr/bin/env python3
"""Conversational chat client for A2A-MCP system."""

import asyncio
import json
import os
import sys
from uuid import uuid4

import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard, MessageSendParams, SendStreamingMessageRequest


class ChatClient:
    def __init__(self):
        self.context_id = uuid4().hex
        self.agent_card = None
        self.load_environment()
    
    def load_environment(self):
        """Load environment variables from .env file."""
        if os.path.exists('.env'):
            with open('.env') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    async def get_orchestrator(self):
        """Get the orchestrator agent card."""
        if self.agent_card:
            return self.agent_card
            
        from a2a_mcp.mcp import client as mcp_client
        
        async with mcp_client.init_session('localhost', 10100, 'sse') as session:
            resources = await mcp_client.find_resource(session, 'resource://agent_cards/orchestrator_agent')
            data = json.loads(resources.contents[0].text)
            orchestrator_data = data['agent_card'][0]
        
        self.agent_card = AgentCard(**orchestrator_data)
        return self.agent_card
    
    async def send_message(self, message: str):
        """Send a message and return the response."""
        orchestrator = await self.get_orchestrator()
        
        async with httpx.AsyncClient(timeout=120.0) as http_client:
            a2a_client = A2AClient(http_client, orchestrator)
            
            request = SendStreamingMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(
                    message={
                        'role': 'user',
                        'parts': [{'kind': 'text', 'text': message}],
                        'messageId': uuid4().hex,
                        'taskId': uuid4().hex,
                        'contextId': self.context_id,
                    }
                )
            )
            
            responses = []
            async for chunk in a2a_client.send_message_streaming(request):
                if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                    result = chunk.root.result
                    
                    # Extract meaningful content
                    if hasattr(result, 'status'):
                        if hasattr(result.status, 'message'):
                            if hasattr(result.status.message, 'parts'):
                                for part in result.status.message.parts:
                                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                        text = part.root.text
                                        if text and not text.startswith('Task'):
                                            responses.append(text)
                    
                    elif hasattr(result, 'artifact'):
                        # Final result
                        if 'summary' in result.artifact.name.lower():
                            if hasattr(result.artifact, 'parts'):
                                for part in result.artifact.parts:
                                    if hasattr(part, 'root') and hasattr(part.root, 'data'):
                                        responses.append(part.root.data)
            
            # Return the last meaningful response
            return responses[-1] if responses else "No response received"


async def interactive_chat():
    """Run an interactive chat session."""
    client = ChatClient()
    
    print("A2A-MCP Chat Client")
    print("===================")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'help' for examples")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Assistant: Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nExample queries:")
                print("- Plan a trip to Tokyo")
                print("- Book a flight from New York to Los Angeles")
                print("- Find hotels in Paris for next weekend")
                print("- I need a rental car in London")
                print()
                continue
            
            if not user_input:
                continue
            
            print("Assistant: ", end="", flush=True)
            response = await client.send_message(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nAssistant: Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure all services are running (./status.sh)")


async def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        client = ChatClient()
        
        print(f"Query: {query}")
        print("-" * 50)
        
        try:
            response = await client.send_message(query)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure all services are running: ./status.sh")
    else:
        # Interactive chat mode
        await interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())