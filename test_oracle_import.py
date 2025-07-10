#!/usr/bin/env python3
# ABOUTME: Test if the Oracle agent can be imported and check for errors
# ABOUTME: Diagnose import issues that might prevent the agent from starting

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/home/user/solopreneur')

try:
    print("Testing Oracle agent import...")
    
    # Set required environment variables
    os.environ['GOOGLE_API_KEY'] = 'AIzaSyBGUGI7fZQT06Hl49OKcTMS5BgPEqC8fvY'
    
    # Try importing the Oracle agent
    from src.a2a_mcp.agents.solopreneur_oracle.solopreneur_oracle_agent_adk import SolopreneurOracleAgent
    print("✅ Oracle agent imported successfully")
    
    # Try creating an instance
    oracle = SolopreneurOracleAgent()
    print("✅ Oracle agent instance created successfully")
    
    # Check basic properties
    print(f"   Agent name: {oracle.agent_name}")
    print(f"   Description: {oracle.description}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()