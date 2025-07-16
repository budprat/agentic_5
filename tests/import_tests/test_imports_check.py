#!/usr/bin/env python3
"""Test if Google ADK imports work correctly"""

import os
import sys

# Set up Google API key
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBPum6lU-1cRBI1gY7hA20nSUZiatS_EfI'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports...")

# Test 1: Import google.generativeai
try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
except ImportError as e:
    print(f"✗ Failed to import google.generativeai: {e}")

# Test 2: Try to import ADK
try:
    from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
    print("✓ google.adk.agents imported successfully")
except ImportError as e:
    print(f"✗ Failed to import google.adk.agents: {e}")
    print("  Note: Google ADK may need to be installed separately")
    
# Test 3: Try google.genai agents (alternative import)
try:
    from google.genai import Agent, GenerativeModel
    print("✓ google.genai imported successfully")
except ImportError as e:
    print(f"✗ Failed to import google.genai: {e}")

# Test 4: Check what's available in google package
try:
    import google
    print("\nAvailable in google package:")
    for attr in dir(google):
        if not attr.startswith('_'):
            print(f"  - google.{attr}")
except Exception as e:
    print(f"Error exploring google package: {e}")

# Test 5: Try genai models
try:
    import google.genai as genai
    print("\n✓ google.genai module found!")
    print("Available in google.genai:")
    for attr in dir(genai):
        if not attr.startswith('_') and attr[0].isupper():
            print(f"  - {attr}")
except ImportError as e:
    print(f"\n✗ google.genai not available: {e}")

print("\nConclusion: You may need to use google.genai instead of google.adk for agent development.")