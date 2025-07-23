@echo off
REM run_tests.bat - Windows test runner for MetadataFetcher
REM Usage: run_tests.bat
REM This script sets PYTHONPATH to the project root and runs pytest on the tests/ directory with verbose output.

set PYTHONPATH=.
pytest -v tests 