#!/usr/bin/env python3
"""
Direct test of ADK pure implementations without going through __init__.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print("❌ Error: GOOGLE_API_KEY not found in environment")
    sys.exit(1)

os.environ['GOOGLE_API_KEY'] = google_api_key

# Import ADK components
from google.adk import Runner
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai import types

print("=== Direct ADK Test ===")
print(f"Using Python: {sys.executable}")


async def test_basic_sequential():
    """Test basic sequential agent directly"""
    print("\n=== Testing Basic Sequential Agent ===")
    
    try:
        # Create sub-agents directly
        research_agent = Agent(
            name="research_agent",
            model="gemini-2.0-flash",
            description="Research specialist",
            instruction="You are a research specialist. Gather relevant information on the given topic."
        )
        
        writing_agent = Agent(
            name="writing_agent",
            model="gemini-2.0-flash",
            description="Content writer",
            instruction="You are a content writer. Create engaging content based on research provided."
        )
        
        # Create sequential orchestrator
        orchestrator = SequentialAgent(
            name="content_creator",
            sub_agents=[research_agent, writing_agent],
            description="Content creation orchestrator"
        )
        
        # Create session service and runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=orchestrator,
            app_name="test_app",
            session_service=session_service
        )
        
        # Create session
        session = session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_sequential"
        )
        
        # Test query
        query = "Write about the benefits of meditation"
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run the agent
        response_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = '\n'.join([p.text for p in event.content.parts if p.text])
        
        print(f"✅ Sequential agent executed successfully")
        print(f"   Response length: {len(response_text)} characters")
        if response_text:
            print(f"   First 200 chars: {response_text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Sequential agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_structured_output():
    """Test LlmAgent with structured output"""
    print("\n=== Testing Structured Output ===")
    
    try:
        from pydantic import BaseModel, Field
        
        class MarketAnalysis(BaseModel):
            trend_analysis: str = Field(description="Analysis of current market trends")
            risk_factors: list[str] = Field(description="Key risk factors")
            recommendations: list[str] = Field(description="Investment recommendations")
        
        # Create LlmAgent with structured output
        analyst = LlmAgent(
            name="market_analyst",
            model="gemini-2.0-flash",
            instruction="You are a financial market analyst. Provide structured analysis.",
            output_schema=MarketAnalysis,
            output_key="analysis"
        )
        
        # Create session service and runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=analyst,
            app_name="test_app",
            session_service=session_service
        )
        
        # Create session
        session = session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_structured"
        )
        
        # Test query
        query = "Analyze the current technology sector market"
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run the agent
        response_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = '\n'.join([p.text for p in event.content.parts if p.text])
        
        print(f"✅ Structured output agent executed successfully")
        print(f"   Response received: {bool(response_text)}")
        
        # Try to parse the response
        if response_text:
            try:
                import json
                data = json.loads(response_text)
                print(f"   Contains trend_analysis: {'trend_analysis' in data}")
                print(f"   Contains risk_factors: {'risk_factors' in data}")
                print(f"   Contains recommendations: {'recommendations' in data}")
            except:
                print(f"   Response is text format (not parsed JSON)")
        
        return True
        
    except Exception as e:
        print(f"❌ Structured output failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_grounding_tool():
    """Test agent with grounding tool"""
    print("\n=== Testing Grounding Tool ===")
    
    try:
        from google.adk.tools import google_search
        
        # Create agent with google search tool
        grounding_agent = Agent(
            name="grounding_agent",
            model="gemini-2.0-flash",
            description="Agent with search capabilities",
            instruction="You are a helpful assistant that can search for information using google_search tool.",
            tools=[google_search]
        )
        
        # Create session service and runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=grounding_agent,
            app_name="test_app",
            session_service=session_service
        )
        
        # Create session
        session = session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_grounding"
        )
        
        # Test query
        query = "What is the current weather in Paris?"
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run the agent
        response_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = '\n'.join([p.text for p in event.content.parts if p.text])
        
        print(f"✅ Grounding agent executed successfully")
        print(f"   Response received: {bool(response_text)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Grounding agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n✅ GOOGLE_API_KEY loaded from .env")
    
    # Run tests
    results = []
    
    # Test basic sequential
    result1 = await test_basic_sequential()
    results.append(("Basic Sequential", result1))
    
    # Test structured output
    result2 = await test_structured_output()
    results.append(("Structured Output", result2))
    
    # Test grounding
    result3 = await test_grounding_tool()
    results.append(("Grounding Tool", result3))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All ADK features working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())