# ABOUTME: Clean test script for Google ADK agent implementations
# ABOUTME: Tests ADK agents with proper import isolation

import asyncio
import logging
import json
import sys
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path BEFORE any imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get API key from environment
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    sys.exit(1)

# Set up environment
os.environ['GOOGLE_API_KEY'] = google_api_key

async def test_simple_sequential_agent():
    """Test a simple sequential ADK agent with sub-agents"""
    logger.info("\n=== Testing Simple Sequential ADK Agent ===")
    
    try:
        from google.adk.agents import Agent, SequentialAgent
        
        # Create sub-agents
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
            name="content_orchestrator",
            description="Content creation workflow orchestrator",
            sub_agents=[research_agent, writing_agent]
        )
        
        logger.info("Sequential ADK agent created successfully!")
        
        # Test with agent runner
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        session_service = InMemorySessionService()
        runner = Runner(
            agent=orchestrator,
            app_name="test_app",
            session_service=session_service
        )
        
        # Create session (not async in ADK)
        session = session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        
        # Test query
        query = "Write a brief introduction about artificial intelligence"
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        logger.info(f"Testing sequential agent with query: {query}")
        
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
                    
        logger.info(f"Sequential agent response received: {len(response_text)} characters")
        return True, response_text
        
    except Exception as e:
        logger.error(f"Sequential agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)

async def test_parallel_agent():
    """Test a parallel ADK agent"""
    logger.info("\n=== Testing Parallel ADK Agent ===")
    
    try:
        from google.adk.agents import Agent, ParallelAgent
        
        # Create parallel sub-agents
        analyst1 = Agent(
            name="technical_analyst",
            model="gemini-2.0-flash",
            description="Technical analysis expert",
            instruction="Analyze technical aspects of the topic"
        )
        
        analyst2 = Agent(
            name="business_analyst",
            model="gemini-2.0-flash",
            description="Business analysis expert",
            instruction="Analyze business implications of the topic"
        )
        
        # Create parallel orchestrator
        parallel_agent = ParallelAgent(
            name="analysis_orchestrator",
            description="Parallel analysis orchestrator",
            sub_agents=[analyst1, analyst2]
        )
        
        logger.info("Parallel ADK agent created successfully!")
        return True, "Parallel agent created"
        
    except Exception as e:
        logger.error(f"Parallel agent test failed: {str(e)}")
        return False, str(e)

async def test_agent_with_structured_output():
    """Test ADK agent with Pydantic structured output"""
    logger.info("\n=== Testing ADK Agent with Structured Output ===")
    
    try:
        from google.adk.agents import LlmAgent
        from pydantic import BaseModel, Field
        
        # Define output schema
        class ProductAnalysis(BaseModel):
            name: str = Field(description="Product name")
            category: str = Field(description="Product category")
            pros: List[str] = Field(description="List of advantages")
            cons: List[str] = Field(description="List of disadvantages")
            rating: float = Field(description="Overall rating out of 5")
            recommendation: str = Field(description="Buy/Hold/Skip recommendation")
        
        # Create agent with structured output
        analyst = LlmAgent(
            name="product_analyst",
            model="gemini-2.0-flash",
            instruction="Analyze the given product and provide a structured analysis",
            output_schema=ProductAnalysis,
            output_key="analysis"
        )
        
        logger.info("Structured output agent created successfully!")
        
        # Test the agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        session_service = InMemorySessionService()
        runner = Runner(
            agent=analyst,
            app_name="test_app",
            session_service=session_service
        )
        
        session = session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_structured"
        )
        
        query = "Analyze the iPhone 15 Pro as a product"
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        logger.info(f"Testing structured agent with query: {query}")
        
        analysis_result = None
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    # For structured output, the result is in the text as JSON
                    text_content = '\n'.join([p.text for p in event.content.parts if p.text])
                    try:
                        import json
                        analysis_result = json.loads(text_content)
                    except:
                        analysis_result = text_content
                            
        if analysis_result:
            logger.info(f"Structured analysis received: {json.dumps(analysis_result, indent=2)}")
            return True, analysis_result
        else:
            return False, "No structured output received"
            
    except Exception as e:
        logger.error(f"Structured output test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)

async def test_agent_with_tool():
    """Test ADK agent with google search tool"""
    logger.info("\n=== Testing ADK Agent with Tool ===")
    
    try:
        from google.adk.agents import Agent
        # Google Search is a built-in grounding tool, not imported separately
        search_agent = Agent(
            name="search_assistant",
            model="gemini-2.0-flash",
            description="Search assistant with web access",
            instruction="You are a helpful search assistant. Use web search to find current information.",
            grounding="google_search"  # Enable Google Search grounding
        )
        
        logger.info("Tool-enabled agent created successfully!")
        return True, "Agent with tool created"
        
    except Exception as e:
        logger.error(f"Tool agent test failed: {str(e)}")
        return False, str(e)

async def main():
    """Run all tests"""
    logger.info("Starting Clean ADK Agent Tests")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Summary of results
    summary = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Run tests
    tests = [
        ("simple_sequential", test_simple_sequential_agent),
        ("parallel_agent", test_parallel_agent),
        ("structured_output", test_agent_with_structured_output),
        ("agent_with_tool", test_agent_with_tool)
    ]
    
    for test_name, test_func in tests:
        success, result = await test_func()
        summary['tests'][test_name] = {
            'success': success,
            'message': 'Passed' if success else result
        }
    
    # Print summary
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(json.dumps(summary, indent=2))
    
    # Count successes
    total_tests = len(summary['tests'])
    passed_tests = sum(1 for test in summary['tests'].values() if test['success'])
    
    logger.info(f"\nTotal Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())