# A2A-MCP Test Suite

Comprehensive test suite for the A2A-MCP (Agent-to-Agent Model Context Protocol) framework.

## Test Directory Structure

```
tests/
├── adk_tests/              # Google ADK integration tests
├── integration_tests/      # Integration and workflow tests
├── import_tests/          # Import verification tests
├── video_tests/           # Video generation system tests
├── api_tests/             # API and WebSocket tests
├── other_tests/           # Miscellaneous tests
└── video_generator/       # Video generator unit tests
```

## Test Categories

### 1. ADK Tests (`adk_tests/`)
**13 files** - Google Agent Development Kit integration
- Interactive chat interfaces
- Agent type demonstrations
- Tool integration tests (google_search, code_execution)
- See `adk_tests/README.md` for details

### 2. Integration Tests (`integration_tests/`)
**4 files** - End-to-end system integration

- **test_comprehensive.py** - Full system integration test
- **test_orchestrator_integration.py** - Orchestrator component integration
- **test_real_workflow.py** - Real-world workflow scenarios
- **test_workflow_direct.py** - Direct workflow execution tests

### 3. Import Tests (`import_tests/`)
**5 files** - Module import verification

- **test_all_imports.py** - Comprehensive import check
- **test_imports.py** - Basic import verification
- **test_imports_check.py** - Import dependency checker
- **test_imports_fixed.py** - Fixed import tests
- **verify_imports.py** - Import validation utility

### 4. Video Tests (`video_tests/`)
**8 files** - Video generation system tests

- **test_video_direct.py** - Direct video generation
- **test_video_final.py** - Final video system tests
- **test_video_gen_fix.py** - Video generation fixes
- **test_video_generation.py** - Core video generation
- **test_video_orchestrator.py** - Video orchestrator tests
- **test_video_orchestrator_real.py** - Real video orchestration
- **test_video_real.py** - Real-world video scenarios
- **test_video_simple.py** - Simple video generation tests

### 5. API Tests (`api_tests/`)
**3 files** - API and WebSocket functionality

- **test_api_client.py** - API client tests
- **test_api_server.py** - API server tests
- **test_websocket_client.html** - WebSocket client test page

### 6. Other Tests (`other_tests/`)
**6 files** - Miscellaneous test utilities

- **demo_without_redis.py** - Demo without Redis dependency
- **test_architecture.py** - Architecture validation
- **test_interactive.py** - Interactive testing utilities
- **test_launch.py** - Launch system tests
- **test_no_redis.py** - Tests without Redis
- **test_simple.py** - Simple functionality tests

### 7. Core Test Files (Root)
**11 files** - Core testing infrastructure

- **run_tests.py** - Main test runner
- **run_real_test.py** - Real environment test runner
- **run_video_tests.py** - Video test runner
- **conftest.py** - Pytest configuration
- **test_a2a_protocol.py** - A2A protocol tests
- **test_agents.py** - Agent functionality tests
- **test_base_agent.py** - Base agent tests
- **test_example_agents.py** - Example agent tests
- **test_quality_framework.py** - Quality framework tests
- **test_video_orchestrator.py** - Video orchestrator tests
- **validate_architecture.py** - Architecture validation

## Running Tests

### Prerequisites
```bash
# Activate conda environment
conda activate a2a-mcp

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests
```bash
cd /Users/mac/Agents/agentic_5
python tests/run_tests.py
```

### Run Specific Test Categories

```bash
# ADK Tests
cd tests/adk_tests
./run_interactive_adk.sh

# Integration Tests
pytest tests/integration_tests/

# Video Tests
python tests/run_video_tests.py

# Import Tests
python tests/import_tests/test_all_imports.py
```

### Interactive Testing

```bash
# ADK Interactive Chat
cd tests/adk_tests
python chat_with_adk.py

# General Interactive Test
python tests/other_tests/test_interactive.py
```

## Test Summary

- **Total Test Files**: 52
- **Python Test Files**: 48
- **Shell Scripts**: 3 (in adk_tests/)
- **HTML Files**: 1
- **Jupyter Notebooks**: 1 (in adk_tests/)

## Key Test Results

### ✅ Working
- Google ADK integration (Sequential, Parallel, LlmAgent)
- Basic agent functionality
- API server and client
- Import verification

### ⚠️ Issues
- Langchain dependencies in some agent imports
- Redis dependency in some tests (alternative no-redis versions available)
- Some video generation tests require specific setup

### 📝 Notes
- Use conda environment `a2a-mcp` for all tests
- API keys should be in `.env` file
- Some tests require additional services (Redis, MCP servers)

## Created/Updated
- ADK tests created: 2025-07-16
- Test reorganization: 2025-07-16