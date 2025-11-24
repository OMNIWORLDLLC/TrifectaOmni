@echo off
REM ============================================================================
REM TrifectaOmni - Quick Start Demo (No Configuration Required)
REM ============================================================================

color 0B
title TrifectaOmni - Demo Scanner

echo.
echo ================================================================================
echo   TRIFECTA OMNI - QUICK START DEMO
echo ================================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [X] Virtual environment not found!
    echo.
    echo Please run install_and_run.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if Python packages are installed
python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing required packages...
    pip install yfinance fastapi uvicorn websockets --quiet
)

echo [*] Starting Demo Scanner...
echo.
echo Mode: DEMO (Yahoo Finance - Free)
echo Latency: ~60 seconds (acceptable for testing)
echo API Keys: Not required
echo.
echo Features:
echo   - Cryptocurrency Arbitrage Detection
echo   - Forex Trading Signals
echo   - Binary Options Opportunities
echo   - Real-Time Dashboard
echo   - Paper Trading System
echo.
echo Dashboard: http://localhost:8080
echo.
echo Press Ctrl+C to stop
echo.
echo ================================================================================
echo.

python realtime_multi_asset_demo.py

pause
