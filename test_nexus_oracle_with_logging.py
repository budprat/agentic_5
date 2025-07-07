#!/usr/bin/env python3
"""Test Nexus Oracle with enhanced logging to monitor behavior."""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'nexus_oracle_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_oracle_with_logging():
    """Test Oracle with detailed logging."""
    print("🔍 NEXUS ORACLE LOGGING TEST")
    print("=" * 50)
    
    from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
    oracle = NexusOracleAgent()
    
    session_id = f"logging_test_{datetime.now().strftime('%H%M%S')}"
    
    logger.info(f"Starting Oracle test session: {session_id}")
    logger.info(f"Oracle quality thresholds: {oracle.quality_thresholds}")
    
    # Test query that might trigger JSON parsing issues
    query = "How can AI and biotechnology collaborate to address climate change while ensuring ethical guidelines?"
    
    print(f"👤 User Query: {query}")
    print("─" * 60)
    
    response_count = 0
    json_errors = 0
    successful_responses = 0
    
    try:
        async for response in oracle.stream(query, session_id, "logging_test_001"):
            response_count += 1
            content = response.get('content', '')
            
            if not response.get('is_task_complete'):
                print(f"⚡ Step {response_count}: {content}")
                logger.info(f"Processing step {response_count}: {content[:50]}...")
            else:
                print(f"\n🎯 FINAL RESULT (Response #{response_count}):")
                
                if response.get('response_type') == 'data':
                    analysis = response.get('content', {})
                    logger.info(f"Received structured analysis with {len(analysis)} top-level keys")
                    
                    # Check for synthesis quality
                    synthesis = analysis.get('synthesis', {})
                    if synthesis:
                        confidence = synthesis.get('research_confidence', 'N/A')
                        domain_count = synthesis.get('domain_coverage', 0)
                        summary = synthesis.get('executive_summary', 'No summary')
                        
                        print(f"📊 Analysis Quality:")
                        print(f"   Confidence: {confidence}")
                        print(f"   Domains: {domain_count}")
                        print(f"   Summary: {summary[:100]}...")
                        
                        logger.info(f"Analysis confidence: {confidence}, domains: {domain_count}")
                        successful_responses += 1
                    else:
                        logger.warning("No synthesis found in analysis")
                else:
                    print(f"📝 Text Response: {content[:150]}...")
                    logger.info(f"Received text response: {len(content)} characters")
                    successful_responses += 1
                break
                
    except Exception as e:
        logger.error(f"Error during Oracle processing: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return False
    
    # Check Oracle state
    print(f"\n🧠 ORACLE STATE AFTER TEST:")
    print(f"   Query History: {len(oracle.query_history)} entries")
    print(f"   Research Cache: {len(oracle.research_intelligence)} domains")
    print(f"   Session Context: {oracle.context_id}")
    
    logger.info(f"Test completed - Responses: {response_count}, Successful: {successful_responses}")
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Total Responses: {response_count}")
    print(f"   Successful Analyses: {successful_responses}")
    print(f"   Session ID: {session_id}")
    
    if successful_responses > 0:
        print(f"✅ Oracle functioning correctly!")
        logger.info("Oracle test completed successfully")
        return True
    else:
        print(f"⚠️  No successful responses generated")
        logger.warning("Oracle test completed with issues")
        return False

async def test_error_handling():
    """Test Oracle's error handling capabilities."""
    print(f"\n🛠️ ERROR HANDLING TEST")
    print("─" * 30)
    
    from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
    oracle = NexusOracleAgent()
    
    # Test scenarios that might cause issues
    test_cases = [
        ("Normal Query", "AI applications in renewable energy"),
        ("Very Short", "AI"),
        ("Very Long", "artificial intelligence machine learning deep learning neural networks quantum computing biotechnology genomics proteomics computational biology systems biology synthetic biology climate change environmental science sustainability renewable energy solar wind hydro geothermal policy governance regulation ethics"),
        ("Special Characters", "AI & ML: How do $$$ investments → better outcomes? (2024)")
    ]
    
    for test_name, test_query in test_cases:
        logger.info(f"Testing error handling for: {test_name}")
        print(f"\n🔬 {test_name}: {test_query[:50]}...")
        
        try:
            # Test dependency analysis (fast)
            result = oracle.analyze_research_dependencies(test_query)
            domains = len(result.get('domain_groups', {}))
            print(f"   ✅ Dependency analysis: {domains} domains detected")
            logger.info(f"{test_name} dependency analysis successful: {domains} domains")
        except Exception as e:
            print(f"   ❌ Dependency analysis failed: {e}")
            logger.error(f"{test_name} dependency analysis failed: {e}")
    
    print(f"\n✅ Error handling tests completed")

if __name__ == "__main__":
    async def main():
        logger.info("Starting Nexus Oracle logging test")
        
        # Test normal operation with logging
        success = await test_oracle_with_logging()
        
        # Test error handling
        await test_error_handling()
        
        if success:
            print(f"\n🎉 ALL TESTS SUCCESSFUL!")
            logger.info("All tests completed successfully")
        else:
            print(f"\n⚠️  SOME ISSUES DETECTED")
            logger.warning("Some tests had issues")
    
    print("🚀 Starting Oracle Logging Test...")
    asyncio.run(main())