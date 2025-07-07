#!/bin/bash

# WebSearch Agent Shell Wrapper
# This script activates the virtual environment and runs the websearch agent

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run 'python3 -m venv venv' first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if the Python script exists
if [ ! -f "websearch_agent.py" ]; then
    echo "Error: websearch_agent.py not found in the current directory."
    exit 1
fi

# Pass all arguments to the Python script
python websearch_agent.py "$@"

# Store the exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

# Exit with the same code as the Python script
exit $EXIT_CODE 