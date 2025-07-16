#!/usr/bin/env python3
# ABOUTME: Master test runner for real video generation workflow without any mocks
# ABOUTME: Provides comprehensive testing of all components with actual execution

"""
Real Video Generation System Test Runner

This script provides comprehensive testing of the video generation system
with REAL execution - no mock data. It tests:
1. Complete workflow execution
2. Individual agent testing
3. Cache system validation
4. Connection pool monitoring
5. Quality framework checks
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional


class RealWorkflowTester:
    """Test runner for real video generation workflow."""
    
    def __init__(self):
        self.workflow = None
        self.test_results = []
    
    async def setup_workflow(self):
        """Initialize the workflow."""
        from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow
        
        print("🚀 Initializing Video Generation Workflow...")
        self.workflow = VideoGenerationWorkflow()
        
        # Verify all components
        print("\n✓ Workflow Components:")
        print(f"  - Agents loaded: {len(self.workflow.agents)}")
        print(f"  - Workflow nodes: {len(self.workflow.workflow_graph.nodes)}")
        print(f"  - Connection pool: {'Active' if self.workflow.connection_pool else 'Inactive'}")
        print(f"  - Quality framework: {'Enabled' if self.workflow.quality_framework.is_enabled() else 'Disabled'}")
        print(f"  - Response formatter: {'Ready' if self.workflow.response_formatter else 'Not ready'}")
        
        # Show agent details
        print("\n📦 Active Agents:")
        for agent_name, agent in self.workflow.agents.items():
            print(f"  - {agent_name}: {type(agent).__name__}")
    
    async def test_complete_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Test complete workflow execution."""
        print("\n" + "="*80)
        print("EXECUTING COMPLETE WORKFLOW (REAL)")
        print("="*80)
        
        print("\n📋 Request Details:")
        print(json.dumps(request, indent=2))
        
        start_time = datetime.now()
        
        try:
            # Execute real workflow
            print("\n🔄 Starting workflow execution...")
            result = await self.workflow.execute(request)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Record test result
            self.test_results.append({
                "test": "complete_workflow",
                "status": result.get("status"),
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display results
            self._display_workflow_results(result, duration)
            
            return result
            
        except Exception as e:
            print(f"\n❌ Workflow execution failed: {e}")
            import traceback
            traceback.print_exc()
            
            self.test_results.append({
                "test": "complete_workflow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "failed", "error": str(e)}
    
    def _display_workflow_results(self, result: Dict[str, Any], duration: float):
        """Display workflow execution results."""
        print(f"\n✅ Workflow completed in {duration:.2f} seconds!")
        
        status = result.get("status", "unknown")
        print(f"\n📊 Overall Status: {status.upper()}")
        
        if status in ["completed", "completed_with_warnings"]:
            outputs = result.get("outputs", {})
            
            # Script output
            if outputs.get("script"):
                print("\n📝 Generated Script:")
                script = outputs["script"]
                content = script.get("content", {})
                
                if isinstance(content, dict):
                    print(f"  Title: {content.get('title', 'N/A')}")
                    print(f"  Duration: {content.get('duration', 0)} seconds")
                    print(f"  Sections: {len(content.get('sections', []))}")
                    
                    # Show first section
                    sections = content.get("sections", [])
                    if sections:
                        print(f"\n  First Section:")
                        print(f"    - Title: {sections[0].get('title', 'N/A')}")
                        print(f"    - Content: {sections[0].get('content', '')[:100]}...")
                else:
                    print(f"  Content: {str(content)[:200]}...")
            
            # Storyboard output
            if outputs.get("storyboard"):
                print("\n🎬 Generated Storyboard:")
                storyboard = outputs["storyboard"]
                scenes = storyboard.get("scenes", [])
                print(f"  Total scenes: {len(scenes)}")
                
                # Show first few scenes
                for i, scene in enumerate(scenes[:3]):
                    print(f"\n  Scene {i+1}:")
                    print(f"    - Description: {scene.get('description', 'N/A')}")
                    print(f"    - Shot type: {scene.get('shot_type', 'N/A')}")
                    print(f"    - Duration: {scene.get('duration', 0)}s")
            
            # Timing plan output
            if outputs.get("timing_plan"):
                print("\n⏱️ Timing Optimization:")
                timing = outputs["timing_plan"]
                print(f"  Total duration: {timing.get('total_duration', 0)} seconds")
                print(f"  Sections: {timing.get('sections', 0)}")
                
                if timing.get("pacing_analysis"):
                    print(f"  Pacing: {timing['pacing_analysis'].get('overall_pace', 'N/A')}")
                    print(f"  Key moments: {timing['pacing_analysis'].get('key_moments', [])}")
            
            # Quality validation
            quality = result.get("quality_validation", {})
            print("\n✅ Quality Validation:")
            print(f"  Overall: {'PASSED' if quality.get('passed') else 'FAILED'}")
            
            if quality.get("scores"):
                print("  Scores:")
                for metric, score in quality["scores"].items():
                    threshold = self.workflow.config.quality_thresholds.get(metric, 0.8)
                    status = "✓" if score >= threshold else "✗"
                    print(f"    {status} {metric}: {score:.2f} (threshold: {threshold})")
            
            # Metadata
            metadata = result.get("metadata", {})
            print("\n📊 Execution Metadata:")
            print(f"  Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"  Platform: {metadata.get('platform', 'N/A')}")
            print(f"  Nodes executed: {metadata.get('nodes_executed', 0)}")
            print(f"  Workflow duration: {metadata.get('workflow_duration', duration):.2f}s")
            
            # Recommendations
            if result.get("recommendations"):
                print("\n💡 Recommendations:")
                for rec in result["recommendations"]:
                    print(f"  - {rec}")
    
    async def test_individual_agent(self, agent_name: str, test_context: Dict[str, Any]):
        """Test an individual agent."""
        print(f"\n" + "="*80)
        print(f"TESTING INDIVIDUAL AGENT: {agent_name.upper()}")
        print("="*80)
        
        if agent_name not in self.workflow.agents:
            print(f"❌ Agent '{agent_name}' not found!")
            return
        
        agent = self.workflow.agents[agent_name]
        print(f"\n✓ Agent type: {type(agent).__name__}")
        
        # Create task context
        from video_generator.agents.a2a_agent_wrapper import TaskContext
        
        context = TaskContext(
            task_id=f"test_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            session_id="test_session",
            context_id="test_context",
            metadata=test_context
        )
        
        print(f"\n🔄 Executing {agent_name}...")
        start_time = datetime.now()
        
        try:
            # Check if agent has the execute method
            if hasattr(agent, '_execute_agent_logic'):
                result = await agent._execute_agent_logic(context)
            elif hasattr(agent, 'process'):
                result = await agent.process(
                    test_context.get("query", "Test query"),
                    test_context
                )
            else:
                print(f"❌ Agent doesn't have a known execution method!")
                return
            
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"\n✅ Agent execution completed in {duration:.2f}s")
            
            # Display result based on type
            if hasattr(result, 'status'):
                print(f"  Status: {result.status}")
                if hasattr(result, 'result') and result.result:
                    print(f"  Result type: {type(result.result).__name__}")
                    if isinstance(result.result, dict):
                        print(f"  Artifacts: {len(result.result.get('artifacts', []))}")
            else:
                print(f"  Result: {result}")
            
            self.test_results.append({
                "test": f"agent_{agent_name}",
                "status": "success",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"\n❌ Agent execution failed: {e}")
            import traceback
            traceback.print_exc()
            
            self.test_results.append({
                "test": f"agent_{agent_name}",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def test_cache_system(self):
        """Test the cache system."""
        print("\n" + "="*80)
        print("TESTING CACHE SYSTEM (REAL)")
        print("="*80)
        
        try:
            if not self.workflow.cache_integration:
                from video_generator.cache.cache_integration import create_cached_workflow
                self.workflow.cache_integration = await create_cached_workflow()
            
            cache = self.workflow.cache_integration
            
            # Test cache operations
            print("\n1. Testing cache lookup...")
            test_request = {
                "content": "Python async programming",
                "platforms": ["youtube"],
                "style": "educational",
                "preferences": {}
            }
            
            cached = await cache.check_generation_cache(test_request)
            print(f"   Cache hit: {'Yes' if cached else 'No'}")
            
            # Get analytics
            print("\n2. Cache Analytics:")
            analytics = await cache.get_cache_analytics()
            perf = analytics["performance"]
            
            print(f"   Total hits: {perf['total_cache_hits']}")
            print(f"   Time saved: {perf['time_saved_seconds']:.1f}s")
            print(f"   Hits by type:")
            for cache_type, hits in perf["hits_by_type"].items():
                print(f"     - {cache_type}: {hits}")
            
            # Test template enhancement
            print("\n3. Template Enhancement Test:")
            enhancements = await cache.enhance_with_templates(
                "script",
                {"platform": "youtube", "style": "educational"}
            )
            
            print(f"   Structure templates: {len(enhancements.get('structure', {}))}")
            print(f"   Hook templates: {len(enhancements.get('hook_templates', []))}")
            
            print("\n✅ Cache system operational!")
            
        except Exception as e:
            print(f"\n❌ Cache test failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_connection_pool(self):
        """Test connection pool status."""
        print("\n" + "="*80)
        print("CONNECTION POOL STATUS")
        print("="*80)
        
        if not self.workflow.connection_pool:
            print("❌ Connection pool not initialized!")
            return
        
        pool = self.workflow.connection_pool
        
        # Get metrics
        metrics = pool.get_metrics()
        print("\n📊 Connection Pool Metrics:")
        print(f"  Active connections: {metrics['active_connections']}")
        print(f"  Total connections created: {metrics['connections_created']}")
        print(f"  Connections reused: {metrics['connections_reused']}")
        print(f"  Connection reuse rate: {metrics['connection_reuse_rate']}%")
        print(f"  Average requests per connection: {metrics['average_requests_per_connection']:.1f}")
        
        # Get connection stats
        stats = pool.get_connection_stats()
        if stats:
            print("\n📈 Active Connection Details:")
            for port, conn_stats in stats.items():
                print(f"  Port {port}:")
                print(f"    - Status: {conn_stats['status']}")
                print(f"    - Age: {conn_stats['age_seconds']:.1f}s")
                print(f"    - Requests: {conn_stats['request_count']}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("\n" + "="*80)
        print("COMPREHENSIVE VIDEO GENERATION SYSTEM TEST")
        print("="*80)
        print("This will test ALL components with REAL execution.")
        print("No mock data will be used.\n")
        
        # Test 1: Basic YouTube video
        print("\n🧪 Test 1: Basic YouTube Educational Video")
        await self.test_complete_workflow({
            "content": "Introduction to Python decorators",
            "platforms": ["youtube"],
            "style": "educational",
            "tone": "professional",
            "preferences": {
                "duration": {"youtube": 300}
            }
        })
        
        await asyncio.sleep(2)  # Brief pause between tests
        
        # Test 2: TikTok video
        print("\n🧪 Test 2: TikTok Entertainment Video")
        await self.test_complete_workflow({
            "content": "5 Python tricks you didn't know",
            "platforms": ["tiktok"],
            "style": "entertaining",
            "tone": "casual",
            "preferences": {
                "duration": {"tiktok": 60}
            }
        })
        
        # Test 3: Individual agents
        print("\n🧪 Test 3: Individual Agent Tests")
        
        await self.test_individual_agent("script_writer", {
            "content": "Web scraping with Python",
            "platform": "youtube",
            "style": "tutorial",
            "duration": 180
        })
        
        await self.test_individual_agent("scene_designer", {
            "script": {"content": "Test script content"},
            "platform": "youtube",
            "style": "educational"
        })
        
        # Test 4: Cache system
        print("\n🧪 Test 4: Cache System")
        await self.test_cache_system()
        
        # Test 5: Connection pool
        print("\n🧪 Test 5: Connection Pool")
        await self.test_connection_pool()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("status") in ["success", "completed"])
        failed = total_tests - passed
        
        print(f"\nTotal tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\nFailed tests:")
            for result in self.test_results:
                if result.get("status") not in ["success", "completed"]:
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        print(f"\nSuccess rate: {(passed/total_tests*100):.1f}%")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.workflow:
            print("\n🧹 Cleaning up...")
            await self.workflow.cleanup()
            print("✓ Cleanup completed")


async def interactive_test():
    """Run interactive test with user input."""
    tester = RealWorkflowTester()
    
    try:
        await tester.setup_workflow()
        
        while True:
            print("\n" + "="*80)
            print("VIDEO GENERATION SYSTEM - REAL TEST MENU")
            print("="*80)
            print("\n1. Run Comprehensive Test Suite")
            print("2. Test Custom Video Request")
            print("3. Test Individual Agent")
            print("4. Check System Status")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                await tester.run_comprehensive_test()
            
            elif choice == "2":
                print("\nEnter video generation parameters:")
                content = input("Content: ").strip() or "Python programming tutorial"
                platform = input("Platform (youtube/tiktok/instagram_reels): ").lower() or "youtube"
                style = input("Style (educational/entertaining/promotional): ").lower() or "educational"
                tone = input("Tone (professional/casual/humorous): ").lower() or "professional"
                
                await tester.test_complete_workflow({
                    "content": content,
                    "platforms": [platform],
                    "style": style,
                    "tone": tone,
                    "preferences": {
                        "duration": {
                            "youtube": 300,
                            "tiktok": 60,
                            "instagram_reels": 30
                        }
                    }
                })
            
            elif choice == "3":
                print("\nAvailable agents:", list(tester.workflow.agents.keys()))
                agent = input("Select agent: ").strip()
                if agent in tester.workflow.agents:
                    content = input("Test content: ").strip() or "Test content"
                    await tester.test_individual_agent(agent, {
                        "content": content,
                        "platform": "youtube",
                        "style": "educational"
                    })
                else:
                    print("❌ Invalid agent name!")
            
            elif choice == "4":
                print("\n📊 System Status:")
                print(f"  Workflow: {'Active' if tester.workflow else 'Inactive'}")
                print(f"  Agents: {len(tester.workflow.agents) if tester.workflow else 0}")
                print(f"  Tests run: {len(tester.test_results)}")
                await tester.test_connection_pool()
            
            elif choice == "5":
                print("\nExiting...")
                break
            
            else:
                print("❌ Invalid choice!")
            
            if choice in ["1", "2", "3", "4"]:
                input("\nPress Enter to continue...")
        
    finally:
        await tester.cleanup()


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real Video Generation System Test")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--interactive", action="store_true", help="Run interactive test")
    parser.add_argument("--content", type=str, help="Test content for quick test")
    parser.add_argument("--platform", type=str, default="youtube", help="Platform for quick test")
    
    args = parser.parse_args()
    
    if args.comprehensive:
        tester = RealWorkflowTester()
        await tester.setup_workflow()
        await tester.run_comprehensive_test()
        await tester.cleanup()
    
    elif args.content:
        tester = RealWorkflowTester()
        await tester.setup_workflow()
        await tester.test_complete_workflow({
            "content": args.content,
            "platforms": [args.platform],
            "style": "educational",
            "tone": "professional",
            "preferences": {
                "duration": {
                    "youtube": 300,
                    "tiktok": 60,
                    "instagram_reels": 30
                }
            }
        })
        await tester.cleanup()
    
    else:
        # Default to interactive mode
        await interactive_test()


if __name__ == "__main__":
    print("\n🚀 Video Generation System - Real Test Runner")
    print("This executes the ACTUAL workflow with NO mock data.")
    print("Ensure all dependencies are installed and services are running.\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()