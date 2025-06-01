#!/usr/bin/env python3
"""Debug script for planner agent startup."""

import os
import sys
import json
import traceback

# Set up environment
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("Environment Check:")
print(f"GOOGLE_API_KEY: {'Set' if os.environ.get('GOOGLE_API_KEY') else 'Not set'}")
print(f"Working directory: {os.getcwd()}")
print()

# Try importing modules
print("Import Check:")
try:
    import a2a_mcp
    print("✓ a2a_mcp imported")
except Exception as e:
    print(f"✗ a2a_mcp import failed: {e}")

try:
    from a2a_mcp.agents.langgraph_planner_agent import LangraphPlannerAgent
    print("✓ LangraphPlannerAgent imported")
except Exception as e:
    print(f"✗ LangraphPlannerAgent import failed: {e}")
    traceback.print_exc()

try:
    import langchain_google_genai
    print("✓ langchain_google_genai imported")
except Exception as e:
    print(f"✗ langchain_google_genai import failed: {e}")

try:
    import langgraph
    print("✓ langgraph imported")
except Exception as e:
    print(f"✗ langgraph import failed: {e}")

# Try loading agent card
print("\nAgent Card Check:")
agent_card_path = "agent_cards/planner_agent.json"
if os.path.exists(agent_card_path):
    with open(agent_card_path) as f:
        agent_card = json.load(f)
    print(f"✓ Agent card loaded: {agent_card['name']}")
    print(f"  URL: {agent_card['url']}")
else:
    print(f"✗ Agent card not found at {agent_card_path}")

# Try initializing the agent
print("\nAgent Initialization Check:")
try:
    from a2a_mcp.common.utils import init_api_key
    init_api_key()
    print("✓ API key initialized")
    
    agent = LangraphPlannerAgent()
    print("✓ LangraphPlannerAgent created successfully")
except Exception as e:
    print(f"✗ Agent initialization failed: {e}")
    traceback.print_exc()

print("\nIf all checks pass, the agent should start successfully.")