#!/usr/bin/env python3
"""Test all imports to verify dependencies are properly installed."""

import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
print()

# Test core dependencies
print("Testing core dependencies...")
try:
    import google.adk
    print("✓ google.adk")
except ImportError as e:
    print(f"✗ google.adk: {e}")

try:
    import a2a
    print("✓ a2a")
except ImportError as e:
    print(f"✗ a2a: {e}")

try:
    import google.genai
    print("✓ google.genai")
except ImportError as e:
    print(f"✗ google.genai: {e}")

# Test framework imports
print("\nTesting framework imports...")
try:
    from a2a_mcp.common.workflow import WorkflowGraph
    print("✓ WorkflowGraph")
except ImportError as e:
    print(f"✗ WorkflowGraph: {e}")

try:
    from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
    print("✓ StandardizedAgentBase")
except ImportError as e:
    print(f"✗ StandardizedAgentBase: {e}")

try:
    from a2a_mcp.common.enhanced_workflow import EnhancedWorkflowGraph
    print("✓ EnhancedWorkflowGraph")
except ImportError as e:
    print(f"✗ EnhancedWorkflowGraph: {e}")

# Test additional dependencies
print("\nTesting additional dependencies...")
dependencies = [
    "aiohttp", "aiofiles", "pydantic", "httpx", "websockets",
    "structlog", "rich", "click", "pytest", "fastmcp",
    "mcp", "OpenSSL", "redis", "prometheus_client"
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ {dep}")
    except ImportError as e:
        print(f"✗ {dep}: {e}")

# Note about aioredis
print("\nNote: aioredis has compatibility issues with Python 3.12.")
print("Use redis.asyncio instead for async Redis operations.")

print("\nAll import tests complete!")