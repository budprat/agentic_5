# ADK Test Suite

This directory contains all test files for Google ADK (Agent Development Kit) integration.

## Test Files Overview

### Interactive Test Scripts

1. **chat_with_adk.py** (3,343 bytes)
   - Simple interactive chat interface
   - Single agent chat loop
   - Commands: 'exit' to quit, 'clear' to clear history

2. **test_adk_interactive.py** (10,024 bytes)
   - Menu-based interactive tester
   - Multiple agent types to choose from:
     - Simple Chat Agent
     - Sequential Agent (Research + Writing)
     - Parallel Agent (Multiple perspectives)
     - Structured Output Agent (JSON)
     - Code Assistant Agent
     - Custom Agent (user-defined)

3. **test_adk_notebook.ipynb** (14,918 bytes)
   - Jupyter notebook for interactive testing
   - Examples of all agent types
   - Interactive widgets for chat

### Automated Test Scripts

4. **test_adk_simple.py** (7,313 bytes)
   - Simplified test suite
   - Tests: Search Agent, Code Agent, Structured Agent
   - No complex dependencies

5. **test_adk_final.py** (8,811 bytes)
   - Fixed version with proper tool imports
   - Tests: Sequential, Structured Output, Google Search
   - All tests passing

6. **test_adk_clean.py** (10,144 bytes)
   - Clean test without langchain dependencies
   - Basic ADK functionality tests
   - Session management examples

7. **test_adk_agents.py** (12,019 bytes)
   - Comprehensive test for all agent types
   - Original test with import chain issues

8. **test_adk_direct.py** (10,214 bytes)
   - Direct import test
   - Attempts to bypass __init__.py

9. **test_adk_pure.py** (9,056 bytes)
   - Tests for pure ADK implementations
   - Tier 1, 2, 3 agent tests

10. **test_adk_pure_v2.py** (12,404 bytes)
    - Updated version with fixed imports
    - Uses Runner and proper session creation

### Shell Scripts

11. **run_interactive_adk.sh** (787 bytes)
    - Launcher for interactive tests
    - Options: 'simple' or 'menu'
    - Uses conda environment

12. **run_adk_test.sh** (335 bytes)
    - Simple test runner
    - Activates conda environment

13. **test_with_env.sh** (643 bytes)
    - Environment setup and test runner
    - Installs dependencies if needed

## Running the Tests

### Prerequisites
- Conda environment: `a2a-mcp`
- Google API key in `.env` file
- Required packages: `google-adk==0.3.0`, `python-dotenv`

### Quick Start

```bash
# Simple interactive chat
cd tests/adk_tests
./run_interactive_adk.sh simple

# Menu-based interface
./run_interactive_adk.sh menu

# Run automated tests
/opt/anaconda3/envs/a2a-mcp/bin/python test_adk_simple.py

# Jupyter notebook
jupyter notebook test_adk_notebook.ipynb
```

### Test Results Summary

- ✅ Sequential Agents: Working
- ✅ Structured Output (LlmAgent): Working with JSON output
- ✅ Google Search Tool: Working with `tools=[google_search]`
- ✅ Code Execution Tool: Working with `tools=[code_execution]`
- ❌ Import chain issues with StandardizedAgentBase (langchain dependency)

### Key Learnings

1. Use `tools=[google_search]` not `grounding="google_search"`
2. Only ONE built-in tool allowed per agent
3. Session creation is synchronous (not async)
4. Structured output warning about transfer configurations is expected
5. Must use conda environment `a2a-mcp` for all tests

## Created Date
All files created on: 2025-07-16