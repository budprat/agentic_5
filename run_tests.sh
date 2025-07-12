#!/bin/bash
# ABOUTME: Test runner script for the A2A MCP Framework
# ABOUTME: Runs all tests with coverage reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   A2A MCP Framework Test Runner${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source .venv/bin/activate
    else
        echo -e "${RED}Error: No virtual environment found${NC}"
        echo "Please run ./start.sh first to set up the environment"
        exit 1
    fi
fi

# Install test dependencies if needed
echo -e "${YELLOW}Checking test dependencies...${NC}"
pip install -q pytest pytest-asyncio pytest-cov pytest-mock

# Run tests with coverage
echo ""
echo -e "${YELLOW}Running tests with coverage...${NC}"
echo ""

# Set PYTHONPATH to include src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run pytest with coverage
pytest tests/ \
    --cov=a2a_mcp \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    -v \
    --tb=short \
    "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Coverage report generated in: htmlcov/index.html"
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi