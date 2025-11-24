@echo off
REM ============================================================================
REM TrifectaOmni - Production Scanner Launcher
REM ============================================================================

color 0E
title TrifectaOmni - Production Scanner

echo.
echo ================================================================================
echo   TRIFECTA OMNI - PRODUCTION SCANNER
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

REM Check if .env exists
if not exist ".env" (
    echo [!] .env file not found!
    echo.
    if exist ".env.example" (
        echo Creating .env from template...
        copy .env.example .env
        echo.
        echo [!] IMPORTANT: Edit .env file with your API credentials:
        echo.
        echo   For MT5 (Forex):
        echo     MT5_LOGIN=your_login
        echo     MT5_SERVER=your_server
        echo     MT5_PASSWORD=your_password
        echo.
        echo   For Crypto (CCXT):
        echo     No keys needed for market data!
        echo     Just: pip install ccxt
        echo.
        echo   For DEX/Blockchain:
        echo     DEX_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
        echo.
        echo   For Binary Options:
        echo     POCKET_TOKEN=your_token
        echo.
        echo After editing .env, run this script again
        echo.
        notepad .env
        pause
        exit /b 0
    ) else (
        echo [X] .env.example not found!
        pause
        exit /b 1
    )
)

echo [*] Checking API Configuration...
echo.

REM Load and check environment
python -c "import os; from dotenv import load_dotenv; load_dotenv(); mt5=bool(os.getenv('MT5_LOGIN')); dex=bool(os.getenv('DEX_RPC')); pocket=bool(os.getenv('POCKET_TOKEN')); print('API Status:'); print('  MT5 (Forex):', 'Configured' if mt5 else 'Not Configured'); print('  CCXT (Crypto): Available (install: pip install ccxt)'); print('  DEX (Blockchain):', 'Configured' if dex else 'Not Configured'); print('  Pocket (Binary):', 'Configured' if pocket else 'Not Configured'); print(); configured_any = mt5 or dex or pocket; print('Status:', 'Ready to run' if configured_any else 'No APIs configured - will run in fallback mode'); exit(0 if configured_any else 0)" 2>nul

echo.
echo ================================================================================
echo   Starting Production Scanner
echo ================================================================================
echo.
echo Mode: PRODUCTION (Real-Time APIs)
echo Latency: ^<1 second
echo Dashboard: http://localhost:8080
echo.
echo Press Ctrl+C to stop
echo.
echo ================================================================================
echo.

python realtime_multi_asset_demo_production.py

pause
