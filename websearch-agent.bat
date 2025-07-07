@echo off
REM WebSearch Agent Windows Batch Wrapper
REM This script activates the virtual environment and runs the websearch agent

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist "venv" (
    echo Error: Virtual environment not found. Please run 'python -m venv venv' first.
    exit /b 1
)

REM Check if the Python script exists
if not exist "websearch_agent.py" (
    echo Error: websearch_agent.py not found in the current directory.
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Pass all arguments to the Python script
python websearch_agent.py %*

REM Store the exit code
set EXIT_CODE=%ERRORLEVEL%

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

REM Exit with the same code as the Python script
exit /b %EXIT_CODE% 