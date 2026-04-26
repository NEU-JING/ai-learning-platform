#!/bin/bash
# Test runner script - fixes venv path issues

cd "$(dirname "$0")/backend"

# Set Python path to use venv packages
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Make sure we use venv python with correct site-packages
export VENV_PYTHON="$(pwd)/venv/bin/python"

# Run tests with correct environment
"$VENV_PYTHON" -m pytest ../tests/test_complete.py -v --tb=short "$@"