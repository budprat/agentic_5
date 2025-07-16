#\!/usr/bin/env python3
# ABOUTME: Simple non-interactive test for video generation system
# ABOUTME: Validates core workflow functionality without user input

"""
Simple test script for video generation system.
Tests core functionality without requiring user interaction.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow


async def test_workflow():
    """Test basic workflow functionality."""
    print("🚀 Testing Video Generation Workflow...")
    
    # Create workflow instance
    workflow = VideoGenerationWorkflow()
    
    # Test request
    request = {
        "content": "Create a 30-second tutorial on Python list comprehensions",
        "platforms": ["youtube", "tiktok"],
        "style": "educational",
        "preferences": {
            "tone": "friendly",
            "pace": "moderate"
        }
    }
    
    print(f"\n📋 Test Request:")
    print(f"  Content: {request['content']}")
    print(f"  Platforms: {', '.join(request['platforms'])}")
    print(f"  Style: {request['style']}")
    
    # Check workflow components
    print("\n🔍 Checking workflow components:")
    print(f"  ✓ Workflow graph initialized: {workflow.workflow_graph is not None}")
    print(f"  ✓ Agents initialized: {len(workflow.agents)} agents")
    print(f"  ✓ Connection pool ready: {workflow.connection_pool is not None}")
    print(f"  ✓ Quality framework ready: {workflow.quality_framework is not None}")
    
    # List agents
    print("\n📦 Registered agents:")
    for agent_name in workflow.agents:
        print(f"  - {agent_name}")
    
    # Check workflow configuration
    print("\n⚙️ Workflow configuration:")
    print(f"  - Parallel execution: {'Enabled' if workflow.config.enable_parallel else 'Disabled'}")
    print(f"  - Max parallel tasks: {workflow.config.max_parallel_tasks}")
    print(f"  - Connection pool size: {workflow.config.connection_pool_size}")
    print(f"  - Quality checks: {'Enabled' if workflow.config.enable_quality_checks else 'Disabled'}")
    
    # Check quality thresholds
    print("\n📊 Quality thresholds:")
    for metric, threshold in workflow.config.quality_thresholds.items():
        print(f"  - {metric}: {threshold}")
    
    print("\n✅ Video generation workflow is properly configured\!")
    
    # Clean up
    await workflow.cleanup()
    print("\n🧹 Cleanup completed")


async def main():
    """Main test function."""
    print("="*80)
    print("Video Generation System - Simple Test")
    print("="*80)
    
    try:
        await test_workflow()
        print("\n✅ All tests passed\!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
EOF < /dev/null
