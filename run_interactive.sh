#!/bin/bash
# ABOUTME: Run script that properly sets up the Python environment for interactive testing
# ABOUTME: Ensures PYTHONPATH is set correctly for a2a_mcp module imports

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Export PYTHONPATH to include src directory
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

echo "=== Video Generation Interactive Test ==="
echo "PYTHONPATH set to: ${PYTHONPATH}"
echo ""

# Run the interactive test
python3 "${SCRIPT_DIR}/test_interactive.py"