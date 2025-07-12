#!/usr/bin/env python3
# ABOUTME: Test runner script for the A2A MCP framework
# ABOUTME: Runs all tests and provides a summary of results

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests in the tests directory"""
    # Get the root directory
    root_dir = Path(__file__).parent
    tests_dir = root_dir / "tests"
    
    # Add src to Python path
    src_path = str(root_dir / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    print("🧪 Running A2A MCP Framework Tests")
    print("=" * 50)
    
    # Find all test files
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found!")
        return 1
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    print()
    
    # Run pytest
    cmd = [
        sys.executable, "-m", "pytest",
        str(tests_dir),
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    print("Running pytest...")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("\n❌ pytest not found. Install it with: pip install pytest")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    sys.exit(exit_code)