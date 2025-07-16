#!/usr/bin/env python3
# ABOUTME: Test script to verify the launch system without actually starting processes
# ABOUTME: Checks environment validation, config loading, and basic functionality

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from launch_system import SystemLauncher

def test_environment_validation():
    """Test environment validation."""
    print("\n=== Testing Environment Validation ===")
    launcher = SystemLauncher()
    
    # Test without GOOGLE_API_KEY
    original_key = os.environ.get('GOOGLE_API_KEY')
    if 'GOOGLE_API_KEY' in os.environ:
        del os.environ['GOOGLE_API_KEY']
    
    is_valid, errors = launcher.validate_environment()
    print(f"Valid without API key: {is_valid}")
    print(f"Errors: {errors}")
    
    # Restore key if it existed
    if original_key:
        os.environ['GOOGLE_API_KEY'] = original_key
    
    # Test with dummy key
    os.environ['GOOGLE_API_KEY'] = 'test-key-123'
    is_valid, errors = launcher.validate_environment()
    print(f"\nValid with API key: {is_valid}")
    print(f"Errors: {errors}")

def test_agent_loading():
    """Test agent configuration loading."""
    print("\n=== Testing Agent Configuration Loading ===")
    launcher = SystemLauncher()
    
    configs = launcher.load_agent_configs()
    print(f"Loaded {len(configs)} agent configurations:")
    
    for config in configs:
        print(f"\n- Agent: {config.get('name', 'Unknown')}")
        print(f"  Type: {config.get('type', 'N/A')}")
        print(f"  Tier: {config.get('tier', 'N/A')}")
        print(f"  Port: {config.get('port', 'N/A')}")
        print(f"  File: {config.get('_file_path', 'N/A')}")

def test_health_check():
    """Test health check functionality."""
    print("\n=== Testing Health Check (no processes) ===")
    launcher = SystemLauncher()
    
    health = launcher.check_system_health()
    print(f"Overall health: {health['overall']}")
    print(f"Components: {list(health['components'].keys())}")

def main():
    """Run all tests."""
    print("Launch System Test Suite")
    print("=" * 50)
    
    test_environment_validation()
    test_agent_loading()
    test_health_check()
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main()