#!/usr/bin/env python3
"""ABOUTME: Simple interactive Oracle tester - focuses on Oracle functionality without complex system startup.
ABOUTME: This provides quick Oracle testing with AWIE and Context-Driven Orchestrator integration."""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_oracle_interactive():
    """Interactive Oracle testing session"""
    
    print("🧠 SOLOPRENEUR ORACLE INTERACTIVE TESTER")
    print("🎯 Testing Oracle with AWIE and Context-Driven Orchestrator")
    print("=" * 60)
    
    try:
        # Initialize Oracle
        logger.info("🚀 Initializing Solopreneur Oracle...")
        from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
        
        oracle = AutonomousWorkflowIntelligenceOracle()
        logger.info("✅ Oracle initialized successfully")
        
        # Test Tier 3 agents
        logger.info("🔧 Testing Tier 3 agents...")
        
        # Test AWIE Scheduler
        try:
            from a2a_mcp.agents.tier3.awie_scheduler_agent import AWIESchedulerAgent
            awie_scheduler = AWIESchedulerAgent()
            logger.info("✅ AWIE Scheduler Agent ready")
        except Exception as e:
            logger.warning(f"⚠️ AWIE Scheduler issue: {e}")
        
        # Test Context-Driven Orchestrator
        try:
            from a2a_mcp.agents.tier3.context_driven_orchestrator import ContextDrivenOrchestrator
            orchestrator = ContextDrivenOrchestrator()
            logger.info("✅ Context-Driven Orchestrator ready")
        except Exception as e:
            logger.warning(f"⚠️ Context-Driven Orchestrator issue: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ORACLE SYSTEM READY FOR TESTING!")
        print("=" * 60)
        print("💡 Example requests:")
        print("   • 'create AI content strategy with SERP optimization'")
        print("   • 'organize my development workflow'")
        print("   • 'coordinate multiple agents for research project'")
        print("   • 'schedule content creation workflow'")
        print("   • 'analyze and optimize my coding workflow'")
        print("=" * 60)
        
        # Interactive testing loop
        while True:
            try:
                request = input("\n🎯 Enter your request (or 'quit' to exit): ").strip()
                
                if request.lower() in ['quit', 'exit', 'q']:
                    print("👋 Oracle testing session ended")
                    break
                
                if not request:
                    print("⚠️ Please enter a request")
                    continue
                
                print("🔄 Processing request through Oracle...")
                start_time = asyncio.get_event_loop().time()
                
                # Process through Oracle
                import hashlib
                request_hash = hashlib.md5(request.encode()).hexdigest()[:8]
                context_id = f"test_{request_hash}"
                task_id = f"task_{request_hash}"
                
                result = await oracle._process_manual_task_request(request, context_id, task_id)
                
                end_time = asyncio.get_event_loop().time()
                processing_time = end_time - start_time
                
                if result and "content" in result:
                    print("\n" + "="*60)
                    print("🎯 SOLOPRENEUR ORACLE RESPONSE:")
                    print("="*60)
                    print(result["content"])
                    print("="*60)
                    
                    # Show metadata and performance
                    print("📊 RESPONSE METADATA:")
                    if "metadata" in result:
                        metadata = result["metadata"]
                        for key, value in metadata.items():
                            print(f"   {key}: {value}")
                    
                    print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
                    print(f"📝 Response Length: {len(result['content'])} characters")
                    
                else:
                    print("❌ No response generated")
                
            except KeyboardInterrupt:
                print("\n👋 Oracle testing session ended")
                break
            except EOFError:
                print("\n👋 Oracle testing session ended")
                break
            except Exception as e:
                print(f"❌ Error processing request: {e}")
                logger.error(f"Processing error: {e}")
        
    except Exception as e:
        print(f"❌ Failed to initialize Oracle: {e}")
        logger.error(f"Initialization error: {e}")

async def run_system_tests():
    """Run quick system tests before interactive session"""
    
    print("🔧 RUNNING SYSTEM TESTS...")
    print("-" * 30)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Oracle import and initialization
    try:
        from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
        oracle = AutonomousWorkflowIntelligenceOracle()
        print("✅ Test 1: Oracle initialization - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Oracle initialization - FAILED: {e}")
    
    # Test 2: AWIE Scheduler
    try:
        from a2a_mcp.agents.tier3.awie_scheduler_agent import AWIESchedulerAgent
        scheduler = AWIESchedulerAgent()
        print("✅ Test 2: AWIE Scheduler - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: AWIE Scheduler - FAILED: {e}")
    
    # Test 3: Context-Driven Orchestrator
    try:
        from a2a_mcp.agents.tier3.context_driven_orchestrator import ContextDrivenOrchestrator
        orchestrator = ContextDrivenOrchestrator()
        print("✅ Test 3: Context-Driven Orchestrator - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Context-Driven Orchestrator - FAILED: {e}")
    
    print(f"\n📊 SYSTEM TESTS: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed - system ready!")
        return True
    else:
        print("⚠️ Some tests failed - system may have issues")
        return False

async def main():
    """Main function"""
    
    print("🧠 SOLOPRENEUR ORACLE TESTING SUITE")
    print("🎯 Simple Oracle testing without full system complexity")
    print("=" * 60)
    
    # Run system tests first
    tests_passed = await run_system_tests()
    
    if tests_passed:
        # Run interactive session
        await test_oracle_interactive()
    else:
        print("\n❌ System tests failed - please check configuration")
        print("💡 Try running individual component tests first")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Testing session ended")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")