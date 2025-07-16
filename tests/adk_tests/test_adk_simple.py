#!/usr/bin/env python3
"""
Simple test of ADK agents without import dependencies
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print("❌ Error: GOOGLE_API_KEY not found in environment")
    exit(1)

os.environ['GOOGLE_API_KEY'] = google_api_key

# Import ADK components
from google.adk import Runner
from google.adk.agents import Agent, SequentialAgent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search, code_execution
from google.genai import types
from pydantic import BaseModel, Field


async def test_search_agent():
    """Test agent with google search tool"""
    print("\n=== Testing Search Agent ===")
    
    # Create agent with search tool
    search_agent = Agent(
        name="search_agent",
        model="gemini-2.0-flash",
        description="Agent with search capabilities",
        instruction="""You are a helpful assistant that can search for current information.
        Use the google_search tool when users ask about current events or need up-to-date information.""",
        tools=[google_search]
    )
    
    # Create session and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=search_agent,
        app_name="test",
        session_service=session_service
    )
    
    session = session_service.create_session(
        app_name="test",
        user_id="user",
        session_id="search_test"
    )
    
    # Test query
    query = "What are the latest developments in AI?"
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    print(f"Query: {query}")
    print("Response: ", end="", flush=True)
    
    response_text = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = '\n'.join([p.text for p in event.content.parts if p.text])
                print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
    
    return bool(response_text)


async def test_code_agent():
    """Test agent with code execution tool"""
    print("\n=== Testing Code Execution Agent ===")
    
    # Create agent with code execution
    code_agent = Agent(
        name="code_agent",
        model="gemini-2.0-flash",
        description="Agent that can execute code",
        instruction="""You are a helpful coding assistant that can execute Python code.
        Use the code_execution tool to run calculations and demonstrate code examples.""",
        tools=[code_execution]
    )
    
    # Create session and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=code_agent,
        app_name="test",
        session_service=session_service
    )
    
    session = session_service.create_session(
        app_name="test",
        user_id="user",
        session_id="code_test"
    )
    
    # Test query
    query = "Calculate the factorial of 10"
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    print(f"Query: {query}")
    print("Response: ", end="", flush=True)
    
    response_text = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = '\n'.join([p.text for p in event.content.parts if p.text])
                print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
    
    return bool(response_text)


async def test_structured_agent():
    """Test agent with structured output"""
    print("\n=== Testing Structured Output Agent ===")
    
    class TaskAnalysis(BaseModel):
        task_name: str = Field(description="Name of the task")
        complexity: str = Field(description="Complexity level: simple, moderate, complex")
        steps: list[str] = Field(description="Steps to complete the task")
        estimated_time: str = Field(description="Estimated time to complete")
    
    # Create structured agent
    struct_agent = LlmAgent(
        name="task_analyzer",
        model="gemini-2.0-flash",
        instruction="Analyze tasks and provide structured breakdown.",
        output_schema=TaskAnalysis,
        output_key="analysis"
    )
    
    # Create session and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=struct_agent,
        app_name="test",
        session_service=session_service
    )
    
    session = session_service.create_session(
        app_name="test",
        user_id="user",
        session_id="struct_test"
    )
    
    # Test query
    query = "Build a web application with user authentication"
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    print(f"Query: {query}")
    print("Response: ", end="", flush=True)
    
    response_text = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = '\n'.join([p.text for p in event.content.parts if p.text])
                # Try to parse JSON
                try:
                    import json
                    data = json.loads(response_text)
                    print(f"Task: {data.get('task_name', 'N/A')}")
                    print(f"Complexity: {data.get('complexity', 'N/A')}")
                    print(f"Steps: {len(data.get('steps', []))}")
                except:
                    print(response_text[:100] + "...")
    
    return bool(response_text)


async def main():
    print("=== Google ADK Simple Test Suite ===")
    print(f"API Key: {'✅ Loaded' if os.getenv('GOOGLE_API_KEY') else '❌ Missing'}")
    
    results = []
    
    # Test search agent
    try:
        result = await test_search_agent()
        results.append(("Search Agent", result))
    except Exception as e:
        print(f"❌ Search agent error: {e}")
        results.append(("Search Agent", False))
    
    # Test code agent  
    try:
        result = await test_code_agent()
        results.append(("Code Agent", result))
    except Exception as e:
        print(f"❌ Code agent error: {e}")
        results.append(("Code Agent", False))
    
    # Test structured agent
    try:
        result = await test_structured_agent()
        results.append(("Structured Agent", result))
    except Exception as e:
        print(f"❌ Structured agent error: {e}")
        results.append(("Structured Agent", False))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    asyncio.run(main())