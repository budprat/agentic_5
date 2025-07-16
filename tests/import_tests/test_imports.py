#!/usr/bin/env python3
"""Test imports for video generation system."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from src.a2a_mcp.common.connection_pool import ConnectionPool
    print("✓ ConnectionPool imported successfully")
except Exception as e:
    print(f"✗ ConnectionPool import failed: {e}")

try:
    from src.video_generator.agents.video_orchestrator_v2 import VideoOrchestratorV2
    print("✓ VideoOrchestratorV2 imported successfully")
except Exception as e:
    print(f"✗ VideoOrchestratorV2 import failed: {e}")

try:
    from src.a2a_mcp.common.enhanced_master_orchestrator_template import EnhancedMasterOrchestratorTemplate
    print("✓ EnhancedMasterOrchestratorTemplate imported successfully")
except Exception as e:
    print(f"✗ EnhancedMasterOrchestratorTemplate import failed: {e}")

print("\nAll imports completed.")