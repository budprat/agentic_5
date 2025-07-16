#!/usr/bin/env python3
# ABOUTME: Verify all imports are working correctly in the conda environment
# ABOUTME: Tests video generation system components can be imported

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=== Verifying Video Generation System Imports ===")
print(f"Python: {sys.version}")
print(f"PYTHONPATH: {sys.path[0]}")
print()

# Test core dependencies
print("1. Testing core dependencies...")
try:
    import grpc
    print(f"✓ grpcio: {grpc.__version__}")
except ImportError as e:
    print(f"❌ grpcio: {e}")

try:
    import httpx
    print(f"✓ httpx: {httpx.__version__}")
except ImportError as e:
    print(f"❌ httpx: {e}")

try:
    import fastapi
    print(f"✓ fastapi: {fastapi.__version__}")
except ImportError as e:
    print(f"❌ fastapi: {e}")

try:
    import redis
    print(f"✓ redis: {redis.__version__}")
except ImportError as e:
    print(f"❌ redis: {e}")

# Test video generator imports
print("\n2. Testing video generator imports...")
try:
    from video_generator.workflow.video_generation_workflow import VideoGenerationWorkflow
    print("✓ VideoGenerationWorkflow imported successfully")
except ImportError as e:
    print(f"❌ VideoGenerationWorkflow: {e}")

try:
    from video_generator.agents.script_writer import ScriptWriter
    print("✓ ScriptWriter imported successfully")
except ImportError as e:
    print(f"❌ ScriptWriter: {e}")

try:
    from video_generator.cache.cache_integration import CachedWorkflowIntegration
    print("✓ CachedWorkflowIntegration imported successfully")
except ImportError as e:
    print(f"❌ CachedWorkflowIntegration: {e}")

# Test a2a_mcp imports
print("\n3. Testing a2a_mcp imports...")
try:
    from a2a_mcp.common.parallel_workflow import ParallelWorkflowGraph
    print("✓ ParallelWorkflowGraph imported successfully")
except ImportError as e:
    print(f"❌ ParallelWorkflowGraph: {e}")

print("\n=== Import Verification Complete ===")
print("\nIf all imports passed, you can run:")
print("  python test_interactive.py")
print("  python -m video_generator.api.combined_server")