#!/usr/bin/env python3
"""Comprehensive test of all Market Oracle agents."""

import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import all agents
from src.a2a_mcp.agents.market_oracle.oracle_prime_agent_supabase import OraclePrimeAgentSupabase
from src.a2a_mcp.agents.market_oracle.fundamental_analyst_agent import FundamentalAnalystAgent
from src.a2a_mcp.agents.market_oracle.technical_prophet_agent import TechnicalProphetAgent
from src.a2a_mcp.agents.market_oracle.sentiment_seeker_agent_brightdata import SentimentSeekerAgentBrightData
from src.a2a_mcp.agents.market_oracle.news_hawk_agent import NewsHawkAgent
from src.a2a_mcp.agents.market_oracle.risk_guardian_agent import RiskGuardianAgent
from src.a2a_mcp.agents.market_oracle.trend_correlator_agent import TrendCorrelatorAgent
from src.a2a_mcp.agents.market_oracle.report_synthesizer_agent import ReportSynthesizerAgent
from src.a2a_mcp.agents.market_oracle.audio_briefer_agent import AudioBrieferAgent

async def test_agent(agent_class, agent_name, test_request):
    """Test a single agent."""
    print(f"\n{'='*60}")
    print(f"🧪 Testing {agent_name}")
    print(f"{'='*60}")
    
    try:
        # Initialize agent
        print(f"✅ Initializing {agent_name}...")
        agent = agent_class()
        print(f"✅ {agent_name} initialized successfully")
        
        # Test the stream method
        print(f"\n📤 Sending request: {test_request}")
        
        response_chunks = []
        # Add timeout for streaming operations
        try:
            # Check if this is News Hawk (which has a different stream signature)
            if agent_name == "News Hawk":
                # Create a timeout for the entire streaming operation
                async with asyncio.timeout(45):  # 45 second timeout for News Hawk
                    async for chunk in agent.stream(test_request):
                        if isinstance(chunk, str):
                            response_chunks.append(chunk)
                        else:
                            response_chunks.append(str(chunk))
            else:
                # Other agents expect context_id and task_id
                context_id = f"test-{agent_name.lower().replace(' ', '-')}"
                task_id = f"task-{datetime.now().timestamp()}"
                async with asyncio.timeout(30):  # 30 second timeout for other agents
                    async for chunk in agent.stream(test_request, context_id, task_id):
                        if isinstance(chunk, dict):
                            # Handle dict response
                            content = chunk.get('content', '')
                            if content:
                                response_chunks.append(str(content))
                            # Also check for other possible content fields
                            elif 'message' in chunk:
                                response_chunks.append(str(chunk['message']))
                            elif 'text' in chunk:
                                response_chunks.append(str(chunk['text']))
                            else:
                                # Convert the whole dict to string if no content field
                                response_chunks.append(json.dumps(chunk))
                        elif isinstance(chunk, str):
                            response_chunks.append(chunk)
                        else:
                            response_chunks.append(str(chunk))
        except asyncio.TimeoutError:
            error = f"Timeout waiting for response from {agent_name}"
            print(f"❌ {error}")
            return False, error
        
        full_response = ''.join(response_chunks)
        
        if full_response:
            print(f"✅ {agent_name} responded successfully")
            print(f"📊 Response length: {len(full_response)} characters")
            print(f"📝 Response preview: {full_response[:200]}...")
            return True, None
        else:
            error = f"Empty response from {agent_name}"
            print(f"❌ {error}")
            return False, error
            
    except Exception as e:
        error = f"Error testing {agent_name}: {str(e)}"
        print(f"❌ {error}")
        import traceback
        traceback.print_exc()
        return False, error

async def test_all_agents():
    """Test all Market Oracle agents."""
    print(f"\n🚀 Market Oracle Agent Test Suite")
    print(f"📅 {datetime.now()}")
    print(f"{'='*60}")
    
    # Test configurations for each agent
    test_configs = [
        (OraclePrimeAgentSupabase, "Oracle Prime (Master)", "Analyze AAPL stock"),
        (FundamentalAnalystAgent, "Fundamental Analyst", "Analyze AAPL fundamentals"),
        (TechnicalProphetAgent, "Technical Prophet", "Analyze AAPL technical indicators"),
        (SentimentSeekerAgentBrightData, "Sentiment Seeker", "Analyze AAPL sentiment"),
        (NewsHawkAgent, "News Hawk", "Get latest AAPL news"),
        (RiskGuardianAgent, "Risk Guardian", "Analyze AAPL risk profile"),
        (TrendCorrelatorAgent, "Trend Correlator", "Analyze AAPL trends"),
        (ReportSynthesizerAgent, "Report Synthesizer", "Create AAPL report"),
        (AudioBrieferAgent, "Audio Briefer", "Create AAPL audio brief"),
    ]
    
    results = []
    
    # Test each agent
    for agent_class, agent_name, test_request in test_configs:
        success, error = await test_agent(agent_class, agent_name, test_request)
        results.append((agent_name, success, error))
    
    # Summary report
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful
    
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    print(f"\n📋 Detailed Results:")
    for agent_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {agent_name}")
        if error:
            print(f"       Error: {error}")
    
    # Test Oracle Prime's orchestration capability
    if successful > 5:  # If most agents work
        print(f"\n{'='*60}")
        print(f"🎯 Testing Oracle Prime Orchestration")
        print(f"{'='*60}")
        
        try:
            oracle = OraclePrimeAgentSupabase()
            complex_request = """
            Provide a comprehensive analysis of NVDA (NVIDIA) including:
            1. Current market sentiment
            2. Technical indicators
            3. Risk assessment
            4. Recent news impact
            """
            
            print(f"📤 Sending complex orchestration request...")
            response = []
            async for chunk in oracle.stream(complex_request):
                response.append(chunk)
            
            if response:
                print(f"✅ Orchestration successful!")
                print(f"📊 Generated comprehensive analysis")
            else:
                print(f"❌ Orchestration failed - empty response")
                
        except Exception as e:
            print(f"❌ Orchestration error: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"✅ Test suite completed!")
    print(f"{'='*60}")

    return successful, failed

async def check_dependencies():
    """Check if all required services are available."""
    print(f"\n🔍 Checking Dependencies...")
    
    # Check environment variables
    required_vars = [
        'GOOGLE_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'BRIGHTDATA_API_TOKEN',
        'BRAVE_API_KEY',
        'ELEVENLABS_API_KEY',
        'GOOGLE_TRENDS_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
    else:
        print(f"✅ All required environment variables are set")
    
    # Check if Supabase is accessible
    try:
        from src.a2a_mcp.common.supabase_client import SupabaseClient
        client = SupabaseClient()
        print(f"✅ Supabase connection available")
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
    
    return len(missing_vars) == 0

if __name__ == "__main__":
    # Check dependencies first
    deps_ok = asyncio.run(check_dependencies())
    
    if not deps_ok:
        print("\n⚠️  Some dependencies are missing. Tests may fail.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    # Run the tests
    successful, failed = asyncio.run(test_all_agents())
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)