#!/bin/bash
# Script to test ADK agents with proper conda environment

# Use the specific Python from the conda environment
PYTHON_PATH="/opt/anaconda3/envs/a2a-mcp/bin/python"

# Install required dependencies
echo "Installing Google ADK in a2a-mcp environment..."
$PYTHON_PATH -m pip install google-adk==0.3.0

# Install other required dependencies
$PYTHON_PATH -m pip install python-dotenv
$PYTHON_PATH -m pip install deprecated

# Verify the correct Python is being used
echo "Using Python from: $PYTHON_PATH"
echo "Python version: $($PYTHON_PATH --version)"

# Run the tests
echo "Running ADK agent tests..."
$PYTHON_PATH test_adk_clean.py