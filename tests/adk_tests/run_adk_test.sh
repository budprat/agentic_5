#!/bin/bash
# Run ADK pure implementation tests with conda environment

echo "Activating conda environment 'a2a-mcp'..."

# Use the conda Python directly
PYTHON_PATH="/opt/anaconda3/envs/a2a-mcp/bin/python"

echo "Using Python: $PYTHON_PATH"

# Run the test
echo "Running ADK pure implementation tests..."
$PYTHON_PATH test_adk_pure.py