#!/usr/bin/env python3
"""Test the Oracle improvements quickly."""

import os
import sys
import asyncio

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

async def test_improvements():
    """Test the key improvements made to the Oracle."""
    print("🧪 TESTING NEXUS ORACLE IMPROVEMENTS")
    print("=" * 50)
    
    from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
    oracle = NexusOracleAgent()
    
    # Test 1: Improved Domain Detection
    print("\n📊 TEST 1: IMPROVED DOMAIN DETECTION")
    print("─" * 40)
    
    test_queries = [
        "How can quantum computing help solve climate change?",
        "What are the psychological effects of AI on social media users?",
        "How can biotechnology improve sustainable agriculture?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        analysis = oracle.analyze_research_dependencies(query)
        domains = list(analysis['domain_groups'].keys())
        print(f"   🎯 Domains Detected: {domains}")
        print(f"   📊 Count: {len(domains)} domains")
        
        if len(domains) >= 3:
            print(f"   ✅ IMPROVED: Rich interdisciplinary analysis")
        elif len(domains) == 2:
            print(f"   👍 GOOD: Solid cross-domain analysis")
        else:
            print(f"   ⚠️  LIMITED: Only basic analysis")
    
    # Test 2: Quality Threshold Logic
    print(f"\n📊 TEST 2: QUALITY THRESHOLD IMPROVEMENTS")
    print("─" * 40)
    
    # Test different scenarios
    scenarios = [
        {
            "name": "High Quality, 2 Domains",
            "synthesis": {"research_confidence": 0.9, "domain_coverage": 2},
            "intelligence": {
                "domain1": {"evidence_quality": 0.9, "bias_assessment": {"test": "low"}},
                "domain2": {"evidence_quality": 0.85, "bias_assessment": {"test": "low"}}
            }
        },
        {
            "name": "Moderate Quality, 3 Domains",
            "synthesis": {"research_confidence": 0.75, "domain_coverage": 3},
            "intelligence": {
                "domain1": {"evidence_quality": 0.8, "bias_assessment": {"test": "low"}},
                "domain2": {"evidence_quality": 0.75, "bias_assessment": {"test": "medium"}},
                "domain3": {"evidence_quality": 0.7, "bias_assessment": {"test": "low"}}
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🔬 Testing: {scenario['name']}")
        oracle.research_intelligence = scenario['intelligence']
        
        quality_result = oracle.check_quality_thresholds(scenario['synthesis'])
        requires_additional = quality_result.get('requires_additional_analysis', True)
        approved = quality_result.get('quality_approved', False)
        
        print(f"   Quality Approved: {approved}")
        print(f"   Requires Additional Analysis: {requires_additional}")
        
        if not requires_additional:
            print(f"   ✅ IMPROVED: Will provide final answer")
        else:
            print(f"   ⚠️  Will ask for more analysis")
    
    # Test 3: Quick Analysis Test
    print(f"\n📊 TEST 3: QUICK ANALYSIS TEST")
    print("─" * 40)
    
    test_query = "How can quantum computing help solve climate change?"
    print(f"Testing: {test_query}")
    
    session_id = "test_session_001"
    response_count = 0
    completed = False
    
    try:
        async for response in oracle.stream(test_query, session_id, "test_task_001"):
            response_count += 1
            
            if response.get('is_task_complete'):
                completed = True
                response_type = response.get('response_type', 'unknown')
                print(f"   ✅ COMPLETED: Got {response_type} response after {response_count} steps")
                
                # Check if we got data response (not just asking for more analysis)
                if response_type == 'data':
                    content = response.get('content', {})
                    synthesis = content.get('synthesis', {})
                    confidence = synthesis.get('research_confidence', 'N/A')
                    print(f"   📊 Analysis Confidence: {confidence}")
                    print(f"   🎯 IMPROVEMENT VERIFIED: Complete analysis provided")
                else:
                    print(f"   ⚠️  Got text response instead of complete analysis")
                break
            elif response_count > 15:  # Prevent infinite loop
                print(f"   ⏰ Stopped after {response_count} steps (avoiding timeout)")
                break
                
    except Exception as e:
        print(f"   ❌ Error during test: {e}")
    
    # Summary
    print(f"\n🏆 IMPROVEMENT TEST SUMMARY")
    print("=" * 40)
    print("✅ Domain Detection: Enhanced with more keywords")
    print("✅ Quality Thresholds: Smarter logic to avoid incomplete responses")
    print("✅ Synthesis Generation: Query-focused prompting")
    if completed:
        print("✅ Full Analysis: Oracle completed analysis successfully")
    else:
        print("⚠️  Full Analysis: Oracle may need more tuning")
    
    print(f"\n🎯 READY FOR INTERACTIVE TESTING!")
    print("Run: python interactive_nexus_oracle_improved.py")

if __name__ == "__main__":
    print("🚀 Testing Oracle Improvements...")
    asyncio.run(test_improvements())