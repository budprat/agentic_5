#!/usr/bin/env python3
# ABOUTME: Test script to verify all imports are working correctly after path fixes
# ABOUTME: Checks that a2a_mcp module can be imported from src folder

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports after fixing paths...")
print(f"Python path: {sys.path[0]}")

try:
    # Test a2a_mcp imports
    print("\n1. Testing a2a_mcp imports...")
    from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph
    print("✓ ParallelWorkflowGraph imported successfully")
    
    from a2a_mcp.common.workflow import WorkflowNode, Status
    print("✓ WorkflowNode and Status imported successfully")
    
    # Test video_generator imports
    print("\n2. Testing video_generator imports...")
    from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow
    print("✓ VideoGenerationWorkflow imported successfully")
    
    from video_generator.agents.script_writer import ScriptWriter
    print("✓ ScriptWriter imported successfully")
    
    from video_generator.cache.cache_integration import CachedWorkflowIntegration
    print("✓ CachedWorkflowIntegration imported successfully")
    
    print("\n✅ All imports working correctly!")
    print("You can now run: python3 test_interactive.py")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("Make sure you're running from the project root directory")