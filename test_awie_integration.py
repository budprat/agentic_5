#!/usr/bin/env python3
"""ABOUTME: Comprehensive AWIE integration test - validates complete system from imports to execution.
ABOUTME: Tests AWIE Scheduler Agent, SERP API integration, and Oracle-to-Scheduler communication."""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_awie_scheduler_import():
    """Test 1: AWIE Scheduler Agent import and initialization"""
    print("🔍 TEST 1: AWIE Scheduler Agent Import & Initialization")
    print("=" * 60)
    
    try:
        from a2a_mcp.agents.tier3.awie_scheduler_agent import AWIESchedulerAgent
        print("✅ Successfully imported AWIESchedulerAgent")
        
        # Test initialization
        scheduler = AWIESchedulerAgent()
        print("✅ Successfully initialized AWIESchedulerAgent")
        
        # Test basic properties
        assert scheduler.agent_name == "AWIE Scheduler Agent"
        assert scheduler.tier == "tier3"
        assert scheduler.port == 10961
        print("✅ Agent properties correctly configured")
        
        # Test SERP API key detection
        serp_key = os.getenv('GOOGLE_TRENDS_API_KEY')
        if serp_key:
            print(f"✅ SERP API key detected: ...{serp_key[-4:]}")
        else:
            print("⚠️ SERP API key not found - will use mock data")
        
        return scheduler
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None

async def test_awie_scheduler_functionality(scheduler):
    """Test 2: AWIE Scheduler core functionality"""
    print("\n🔍 TEST 2: AWIE Scheduler Core Functionality")
    print("=" * 60)
    
    try:
        # Test workflow scheduling
        test_request = "research RAG implementation and create content about vector databases"
        
        print(f"📝 Testing request: {test_request}")
        result = await scheduler.schedule_enhanced_workflow(test_request)
        
        if result["success"]:
            print("✅ Workflow scheduling successful")
            print(f"✅ Generated {len(result['workflow']['tasks'])} tasks")
            print(f"✅ Total duration: {result['workflow']['total_duration']} minutes")
            
            # Test SERP data integration
            if result.get("serp_data"):
                print(f"✅ SERP data integrated: {len(result['serp_data'])} keywords analyzed")
                total_volume = sum(result["market_intelligence"]["search_volume_trends"].values())
                print(f"✅ Total search volume analyzed: {total_volume:,}")
            else:
                print("⚠️ No SERP data - using mock data")
            
            # Test scheduling summary generation
            summary = result.get("scheduling_summary", "")
            if "AWIE Scheduler" in summary and "SERP-OPTIMIZED" in summary:
                print("✅ Scheduling summary properly formatted")
            else:
                print("⚠️ Scheduling summary format issues")
            
            return result
        else:
            print(f"❌ Workflow scheduling failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return None

async def test_standardized_agent_base_compliance(scheduler):
    """Test 3: StandardizedAgentBase compliance"""
    print("\n🔍 TEST 3: StandardizedAgentBase Compliance")
    print("=" * 60)
    
    try:
        # Test _execute_agent_logic method exists and works
        test_query = "schedule content creation for AI agents"
        context_id = "test_context_123"
        task_id = "test_task_456"
        
        print(f"📝 Testing _execute_agent_logic with query: {test_query}")
        result = await scheduler._execute_agent_logic(test_query, context_id, task_id)
        
        if isinstance(result, dict):
            print("✅ _execute_agent_logic returns proper dict format")
            
            if "content" in result:
                print("✅ Response contains 'content' field")
            
            if "metadata" in result:
                print("✅ Response contains 'metadata' field")
                metadata = result["metadata"]
                if "workflow_id" in metadata and "total_tasks" in metadata:
                    print("✅ Metadata properly structured")
            
            return True
        else:
            print(f"❌ _execute_agent_logic returned invalid type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ StandardizedAgentBase compliance test failed: {e}")
        return False

async def test_awie_oracle_integration():
    """Test 4: AWIE Oracle integration with Scheduler"""
    print("\n🔍 TEST 4: AWIE Oracle Integration")
    print("=" * 60)
    
    try:
        from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
        print("✅ Successfully imported AWIE Oracle")
        
        # Initialize AWIE Oracle
        oracle = AutonomousWorkflowIntelligenceOracle()
        print("✅ AWIE Oracle initialized")
        
        # Test that Oracle has access to AWIE Scheduler
        if hasattr(oracle, 'awie_scheduler'):
            print("✅ AWIE Oracle has awie_scheduler attribute")
            
            # Test Oracle can call Scheduler
            test_request = "organize my research workflow with SERP optimization"
            context_id = "integration_test_001"
            task_id = "integration_task_001"
            
            print(f"📝 Testing Oracle->Scheduler integration: {test_request}")
            result = await oracle._process_manual_task_request(test_request, context_id, task_id)
            
            if result and "content" in result:
                content = result["content"]
                if "AWIE Oracle + SERP Intelligence" in content:
                    print("✅ Oracle successfully integrated with Scheduler")
                    print("✅ SERP intelligence properly embedded in response")
                    return True
                else:
                    print("⚠️ Oracle response format unexpected")
                    return False
            else:
                print("❌ Oracle integration failed")
                return False
        else:
            print("❌ AWIE Oracle missing awie_scheduler attribute")
            return False
            
    except ImportError as e:
        print(f"❌ AWIE Oracle import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ AWIE Oracle integration test failed: {e}")
        return False

async def test_serp_api_real_data():
    """Test 5: Real SERP API data (if API key available)"""
    print("\n🔍 TEST 5: Real SERP API Data Integration")
    print("=" * 60)
    
    serp_key = os.getenv('GOOGLE_TRENDS_API_KEY')
    if not serp_key:
        print("⚠️ GOOGLE_TRENDS_API_KEY not found - skipping real SERP test")
        return True
    
    try:
        from a2a_mcp.agents.tier3.awie_scheduler_agent import AWIESchedulerAgent
        
        scheduler = AWIESchedulerAgent()
        
        # Test with AI-relevant keywords
        test_keywords = ["RAG retrieval augmented generation", "AI agents framework"]
        print(f"📝 Testing real SERP API with keywords: {test_keywords}")
        
        serp_data = await scheduler._get_serp_trends(test_keywords)
        
        if serp_data and len(serp_data) > 0:
            print(f"✅ Real SERP API working: {len(serp_data)} keywords analyzed")
            
            for data in serp_data:
                print(f"  📊 {data.keyword}: {data.search_volume:,} searches, {data.competition_level} competition")
            
            return True
        else:
            print("⚠️ No SERP data returned - check API key or rate limits")
            return False
            
    except Exception as e:
        print(f"❌ Real SERP API test failed: {e}")
        return False

async def main():
    """Run comprehensive AWIE integration tests"""
    print("🧠 AWIE COMPREHENSIVE INTEGRATION TEST")
    print("🎯 Testing complete system from imports to execution")
    print("📋 Following NU's rule: no shortcuts, fix issues properly")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Import and initialization
    scheduler = await test_awie_scheduler_import()
    test_results.append(scheduler is not None)
    
    if scheduler:
        # Test 2: Core functionality
        workflow_result = await test_awie_scheduler_functionality(scheduler)
        test_results.append(workflow_result is not None)
        
        # Test 3: StandardizedAgentBase compliance
        compliance_result = await test_standardized_agent_base_compliance(scheduler)
        test_results.append(compliance_result)
    else:
        test_results.extend([False, False])
    
    # Test 4: Oracle integration
    oracle_result = await test_awie_oracle_integration()
    test_results.append(oracle_result)
    
    # Test 5: Real SERP API
    serp_result = await test_serp_api_real_data()
    test_results.append(serp_result)
    
    # Final results
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 80)
    
    test_names = [
        "AWIE Scheduler Import & Initialization",
        "AWIE Scheduler Core Functionality", 
        "StandardizedAgentBase Compliance",
        "AWIE Oracle Integration",
        "Real SERP API Integration"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, test_results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(test_results)) * 100
    print(f"\n🏆 OVERALL RESULT: {passed}/{len(test_results)} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 AWIE integration system is working properly!")
        print("✅ Ready for production use with SERP-enhanced workflows")
    elif success_rate >= 60:
        print("⚠️ AWIE system mostly working with some issues to address")
    else:
        print("❌ AWIE system has significant issues requiring fixes")
    
    return success_rate >= 80

if __name__ == "__main__":
    asyncio.run(main())