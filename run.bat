@echo off
REM UniThrive Prototype Startup Script
REM This script starts the FastAPI backend server

echo ===========================================
echo UniThrive Prototype
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ===========================================
echo Starting UniThrive Server
echo ===========================================
echo.
echo API will be available at: http://localhost:8000
echo Documentation will be at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat

echo.
echo Server stopped.
pause
