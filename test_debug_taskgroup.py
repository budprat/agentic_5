#!/usr/bin/env python3
# ABOUTME: Debug the TaskGroup error by catching the full exception
# ABOUTME: Tests the agent initialization and stream method directly

import asyncio
import logging
import os
import sys
import traceback
from a2a_mcp.agents.solopreneur_oracle.technical_intelligence_agent import TechnicalIntelligenceAgent

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_agent_initialization():
    """Test if agent can be initialized."""
    print("Testing agent initialization...")
    
    # Check GOOGLE_API_KEY
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        print(f"✓ GOOGLE_API_KEY is set: {api_key[:10]}...")
    else:
        print("✗ GOOGLE_API_KEY is not set!")
    
    try:
        agent = TechnicalIntelligenceAgent()
        print(f"✓ Agent created: {agent.agent_name}")
        
        # Check if agent needs initialization
        if hasattr(agent, 'agent') and agent.agent is None:
            print("  Agent needs initialization...")
            await agent.init_agent()
            print("✓ Agent initialized successfully")
        else:
            print("  Agent already initialized or doesn't need initialization")
            
        return agent
        
    except Exception as e:
        print(f"✗ Error initializing agent: {e}")
        traceback.print_exc()
        return None

async def test_agent_stream(agent):
    """Test the agent stream method."""
    print("\nTesting agent stream method...")
    
    query = "What are the best practices for implementing a microservices architecture?"
    context_id = "test-context-123"
    task_id = "test-task-456"
    
    try:
        print(f"Calling stream with query: {query}")
        
        # Iterate through the stream
        async for response in agent.stream(query, context_id, task_id):
            print(f"Stream response: {response}")
            
            if response.get('is_task_complete'):
                print("✓ Task completed successfully")
                return True
                
    except Exception as e:
        print(f"✗ Error in stream method: {e}")
        print("\nFull exception details:")
        traceback.print_exc()
        
        # Try to get more details about TaskGroup errors
        if "TaskGroup" in str(e):
            print("\nThis is a TaskGroup error. Checking for sub-exceptions...")
            if hasattr(e, '__cause__') and e.__cause__:
                print(f"Cause: {e.__cause__}")
            if hasattr(e, '__context__') and e.__context__:
                print(f"Context: {e.__context__}")
            if hasattr(e, 'exceptions') and e.exceptions:
                print(f"Sub-exceptions: {e.exceptions}")
                
        return False

async def main():
    """Run the debug tests."""
    print("TaskGroup Error Debugging")
    print("=" * 60)
    
    # Test initialization
    agent = await test_agent_initialization()
    
    if agent:
        # Test stream
        await test_agent_stream(agent)
    else:
        print("\n✗ Cannot test stream - agent initialization failed")

if __name__ == "__main__":
    asyncio.run(main())