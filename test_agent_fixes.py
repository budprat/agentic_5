#!/usr/bin/env python3
"""Test the fixed Market Oracle agents."""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent_fixes_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_fixed_agents():
    """Test the three fixed agents."""
    print("\n" + "="*80)
    print("🔧 TESTING FIXED AGENTS")
    print("="*80)
    
    # Import the fixed agents
    from src.a2a_mcp.agents.market_oracle.fundamental_analyst_agent import FundamentalAnalystAgent
    from src.a2a_mcp.agents.market_oracle.trend_correlator_agent import TrendCorrelatorAgent
    from src.a2a_mcp.agents.market_oracle.report_synthesizer_agent import ReportSynthesizerAgent
    
    results = {}
    
    # Test 1: Fundamental Analyst (fixed agent name)
    print("\n1️⃣ Testing Fundamental Analyst...")
    try:
        agent = FundamentalAnalystAgent()
        print(f"   ✅ Agent initialized with name: {agent.agent_name}")
        
        # Test agent functionality
        query = "Analyze AAPL fundamentals"
        async for response in agent.stream(query, "test_fundamental", "task_1"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    print("   ✅ Agent responded with data")
                    results['fundamental_analyst'] = "SUCCESS"
                break
                
        if 'fundamental_analyst' not in results:
            results['fundamental_analyst'] = "NO_DATA"
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['fundamental_analyst'] = f"ERROR: {e}"
        
    # Test 2: Trend Correlator (fixed integer conversion)
    print("\n2️⃣ Testing Trend Correlator...")
    try:
        agent = TrendCorrelatorAgent()
        print(f"   ✅ Agent initialized")
        
        # Test agent functionality
        query = "Analyze TSLA trend correlation"
        async for response in agent.stream(query, "test_trend", "task_2"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    print("   ✅ Agent responded with data")
                    results['trend_correlator'] = "SUCCESS"
                break
                
        if 'trend_correlator' not in results:
            results['trend_correlator'] = "NO_DATA"
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['trend_correlator'] = f"ERROR: {e}"
        
    # Test 3: Report Synthesizer (fixed timedelta import)
    print("\n3️⃣ Testing Report Synthesizer...")
    try:
        agent = ReportSynthesizerAgent()
        print(f"   ✅ Agent initialized")
        
        # Test agent functionality
        query = "Generate report for NVDA"
        async for response in agent.stream(query, "test_report", "task_3"):
            if response.get('is_task_complete'):
                if response.get('response_type') == 'data':
                    print("   ✅ Agent responded with data")
                    results['report_synthesizer'] = "SUCCESS"
                break
                
        if 'report_synthesizer' not in results:
            results['report_synthesizer'] = "NO_DATA"
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['report_synthesizer'] = f"ERROR: {e}"
        
    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    all_success = True
    for agent, status in results.items():
        if status == "SUCCESS":
            print(f"✅ {agent}: {status}")
        else:
            print(f"❌ {agent}: {status}")
            all_success = False
            
    if all_success:
        print("\n🎉 ALL AGENTS FIXED AND WORKING!")
    else:
        print("\n⚠️  Some agents still have issues")
        
    print("="*80)
    
if __name__ == "__main__":
    asyncio.run(test_fixed_agents())