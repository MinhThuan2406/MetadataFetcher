#!/bin/sh
# run_tests.sh - Cross-platform test runner for MetadataFetcher
# Usage: sh run_tests.sh
# This script sets PYTHONPATH to the project root and runs pytest on the tests/ directory with verbose output.

# For Unix/Mac
if [ "$(uname)" != "Windows_NT" ]; then
  PYTHONPATH=. pytest -v tests
else
  # For Windows (CMD or PowerShell)
  set PYTHONPATH=.
  pytest -v tests
fi 