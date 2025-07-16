#!/usr/bin/env python3
# ABOUTME: Real interactive test of video generation workflow without mock data
# ABOUTME: Executes actual workflow with all agents and produces real results

"""
Real Interactive Test of Video Generation Workflow

This script tests the actual video generation workflow without any mock data.
It executes the real agents and produces actual results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
from datetime import datetime
from typing import Dict, Any


async def test_real_workflow():
    """Test the real video generation workflow."""
    print("=" * 80)
    print("Video Generation System - Real Workflow Test")
    print("=" * 80)
    print("\nThis test executes the ACTUAL workflow with REAL agents.")
    print("No mock data will be used.\n")
    
    # Get user input
    print("Enter video generation parameters:")
    content = input("Content/Topic (e.g., 'Python async/await tutorial'): ").strip()
    if not content:
        content = "Python async/await tutorial"
    
    # Get platform with validation
    platform_input = input("Platform (youtube/tiktok/instagram_reels): ").lower().strip()
    valid_platforms = ["youtube", "tiktok", "instagram_reels"]
    platform = platform_input if platform_input in valid_platforms else "youtube"
    if platform_input and platform_input not in valid_platforms:
        print(f"  ⚠️  Invalid platform '{platform_input}', using 'youtube' instead")
    
    style = input("Style (educational/entertaining/promotional): ").lower().strip() or "educational"
    tone = input("Tone (professional/casual/humorous): ").lower().strip() or "professional"
    
    # Create request
    request = {
        "content": content,
        "platforms": [platform],
        "style": style,
        "tone": tone,
        # Add duration_preferences at top level for compatibility
        "duration_preferences": {
            "youtube": 300,  # 5 minutes
            "tiktok": 60,    # 1 minute
            "instagram_reels": 30,  # 30 seconds
            # Add capitalized versions as fallback
            "Youtube": 300,
            "TikTok": 60,
            "Instagram_reels": 30
        },
        "preferences": {
            "duration": {
                "youtube": 300,  # 5 minutes
                "tiktok": 60,    # 1 minute
                "instagram_reels": 30,  # 30 seconds
                # Add capitalized versions as fallback
                "Youtube": 300,
                "TikTok": 60,
                "Instagram_reels": 30
            },
            "quality_thresholds": {
                "script_coherence": 0.85,
                "visual_feasibility": 0.80,
                "engagement_potential": 0.75,
                "platform_compliance": 0.90
            }
        }
    }
    
    print("\n" + "-" * 60)
    print("Request Configuration:")
    print(json.dumps(request, indent=2))
    print("-" * 60)
    
    # Import and initialize workflow
    try:
        from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow
        
        print("\n🚀 Initializing Video Generation Workflow...")
        workflow = VideoGenerationWorkflow()
        
        print(f"\n✓ Workflow initialized successfully!")
        print(f"  - Active agents: {list(workflow.agents.keys())}")
        print(f"  - Workflow nodes: {len(workflow.workflow_graph.nodes)}")
        print(f"  - Connection pool: {'Active' if workflow.connection_pool else 'Inactive'}")
        print(f"  - Quality framework: {'Enabled' if workflow.quality_framework else 'Disabled'}")
        
        # Execute the real workflow
        print("\n🔄 Executing workflow...")
        print("This will run the actual agents and may take some time...\n")
        
        start_time = datetime.now()
        
        # Execute workflow
        try:
            result = await workflow.execute(request)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n✅ Workflow completed in {duration:.2f} seconds!")
            
            # Display results
            print("\n" + "=" * 60)
            print("WORKFLOW RESULTS")
            print("=" * 60)
            
            if result.get("status") == "completed":
                print("\n📝 Generated Script:")
                script_output = result.get("outputs", {}).get("script", {})
                if script_output:
                    print(f"  Content: {script_output.get('content', 'No content generated')[:200]}...")
                    print(f"  Duration: {script_output.get('duration', 0)} seconds")
                    print(f"  Word count: {script_output.get('word_count', 0)}")
                
                print("\n🎬 Storyboard:")
                storyboard_output = result.get("outputs", {}).get("storyboard", {})
                if storyboard_output:
                    print(f"  Scenes: {storyboard_output.get('scenes', 0)}")
                    print(f"  Shots: {storyboard_output.get('shots', 0)}")
                    print(f"  Transitions: {len(storyboard_output.get('transitions', []))}")
                
                print("\n⏱️ Timing Plan:")
                timing_output = result.get("outputs", {}).get("timing_plan", {})
                if timing_output:
                    print(f"  Total duration: {timing_output.get('total_duration', 0)} seconds")
                    print(f"  Sections: {timing_output.get('sections', 0)}")
                    print(f"  Key moments: {timing_output.get('key_moments', [])}")
                
                print("\n✅ Quality Validation:")
                quality = result.get("quality_validation", {})
                if quality.get("passed"):
                    print("  All quality thresholds passed!")
                    scores = quality.get("scores", {})
                    for metric, score in scores.items():
                        print(f"  - {metric}: {score:.2f}")
                else:
                    print("  ⚠️  Some quality thresholds not met:")
                    for issue in quality.get("failed_metrics", []):
                        print(f"    - {issue}")
                
                print("\n📊 Workflow Metadata:")
                metadata = result.get("metadata", {})
                print(f"  Workflow ID: {result.get('workflow_id', 'N/A')}")
                print(f"  Platform: {metadata.get('platform', 'N/A')}")
                print(f"  Nodes executed: {metadata.get('nodes_executed', 0)}")
                print(f"  Workflow duration: {metadata.get('workflow_duration', 0):.2f}s")
                
                if result.get("recommendations"):
                    print("\n💡 Recommendations:")
                    for rec in result["recommendations"]:
                        print(f"  - {rec}")
            
            elif result.get("status") == "failed":
                print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
            else:
                print(f"\n⚠️  Unexpected status: {result.get('status', 'Unknown')}")
            
            # Show raw result if requested
            show_raw = input("\n\nShow raw result JSON? (y/N): ").lower().strip()
            if show_raw == 'y':
                print("\nRaw Result:")
                print(json.dumps(result, indent=2, default=str))
                
        except Exception as e:
            print(f"\n❌ Error during workflow execution: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            await workflow.cleanup()
            print("✓ Cleanup completed")
            
    except ImportError as e:
        print(f"\n❌ Failed to import workflow: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  - pip install -r requirements.txt")
        print("  - Ensure PYTHONPATH includes the src directory")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


async def test_individual_agents():
    """Test individual agents directly."""
    print("\n" + "=" * 80)
    print("Individual Agent Test")
    print("=" * 80)
    
    agent_choice = input("\nTest individual agent? (script/scene/timing/N): ").lower().strip()
    
    if agent_choice == 'script':
        from video_generator.agents.script_writer import ScriptWriter
        from video_generator.agents.a2a_agent_wrapper import TaskContext, TaskResult
        
        agent = ScriptWriter()
        context = TaskContext(
            task_id="test_001",
            session_id="session_001",
            context_id="context_001",
            metadata={
                "content": "Create a tutorial on Python decorators",
                "style": "educational",
                "platform": "youtube",
                "duration": 300
            }
        )
        
        print("\n🔄 Executing ScriptWriter...")
        result = await agent._execute_agent_logic(context)
        
        if result.status == "success":
            print("\n✅ Script generated successfully!")
            if result.result and result.result.get("artifacts"):
                for artifact in result.result["artifacts"]:
                    print(f"\nArtifact Type: {artifact.get('type')}")
                    print(f"Content: {artifact.get('content', {})}")
        else:
            print(f"\n❌ Script generation failed: {result.error}")
    
    elif agent_choice == 'scene':
        from video_generator.agents.scene_designer import SceneDesigner
        print("\n✓ SceneDesigner test - implement similar to script test")
    
    elif agent_choice == 'timing':
        from video_generator.agents.timing_coordinator import TimingCoordinator
        print("\n✓ TimingCoordinator test - implement similar to script test")


async def main():
    """Main test function."""
    while True:
        print("\n" + "=" * 80)
        print("Video Generation System - Real Test Menu")
        print("=" * 80)
        print("\n1. Test Complete Workflow (Real Execution)")
        print("2. Test Individual Agents")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            await test_real_workflow()
        elif choice == "2":
            await test_individual_agents()
        elif choice == "3":
            print("\nExiting test...")
            break
        else:
            print("\n⚠️  Invalid choice. Please try again.")
        
        if choice in ["1", "2"]:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("\n🚀 Starting Video Generation System - Real Test")
    print("This will execute the ACTUAL workflow without any mock data.")
    print("Make sure all dependencies are properly installed.\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()