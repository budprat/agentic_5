#!/usr/bin/env python3
"""Simple query tool for A2A-MCP system."""

import asyncio
import json
import os
import sys
from uuid import uuid4

import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard, MessageSendParams, SendStreamingMessageRequest


async def query_orchestrator(message: str):
    """Send a query to the orchestrator and display results."""
    
    # Load environment
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Get orchestrator agent card from MCP
    from a2a_mcp.mcp import client as mcp_client
    
    async with mcp_client.init_session('localhost', 10100, 'sse') as session:
        resources = await mcp_client.find_resource(session, 'resource://agent_cards/orchestrator_agent')
        data = json.loads(resources.contents[0].text)
        orchestrator_data = data['agent_card'][0]
    
    orchestrator = AgentCard(**orchestrator_data)
    
    # Send message
    context_id = uuid4().hex
    
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
                    'contextId': context_id,
                }
            )
        )
        
        print(f"Query: {message}")
        print("-" * 50)
        print("Processing...\n")
        
        async for chunk in a2a_client.send_message_streaming(request):
            if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                result = chunk.root.result
                
                # Display different types of responses
                if hasattr(result, 'status'):
                    if hasattr(result.status, 'state'):
                        state = result.status.state
                        if state != 'working':
                            print(f"Status: {state}")
                    
                    if hasattr(result.status, 'message'):
                        if hasattr(result.status.message, 'parts'):
                            for part in result.status.message.parts:
                                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                    text = part.root.text
                                    if text and not text.startswith('Task'):
                                        print(f"\n{text}")
                
                elif hasattr(result, 'artifact'):
                    artifact_name = result.artifact.name
                    if artifact_name and 'result' in artifact_name.lower():
                        print(f"\n[{artifact_name}]")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python query.py <your question>")
        print("\nExamples:")
        print('  python query.py "Plan a trip to Paris for next week"')
        print('  python query.py "Book a flight from New York to London"')
        print('  python query.py "Find hotels in Tokyo"')
        sys.exit(1)
    
    # Get query from command line
    query = " ".join(sys.argv[1:])
    
    try:
        await query_orchestrator(query)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure all services are running:")
        print("  ./status.sh")


if __name__ == "__main__":
    asyncio.run(main())