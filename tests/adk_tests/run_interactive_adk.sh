#!/bin/bash
# Run interactive ADK tests with conda environment

echo "🚀 Starting ADK Interactive Tester..."
echo "=================================="

# Use the conda Python directly
PYTHON_PATH="/opt/anaconda3/envs/a2a-mcp/bin/python"

# Check which script to run
if [ "$1" == "simple" ]; then
    echo "Running simple chat interface..."
    $PYTHON_PATH chat_with_adk.py
elif [ "$1" == "menu" ]; then
    echo "Running menu-based interface..."
    $PYTHON_PATH test_adk_interactive.py
else
    echo "Choose an interface:"
    echo "  ./run_interactive_adk.sh simple  - Simple chat interface"
    echo "  ./run_interactive_adk.sh menu    - Menu with different agent types"
    echo ""
    echo "Defaulting to simple chat interface..."
    echo ""
    $PYTHON_PATH chat_with_adk.py
fi