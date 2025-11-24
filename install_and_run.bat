@echo off
REM ============================================================================
REM TrifectaOmni - One-Click Windows Installer and Launcher
REM ============================================================================
setlocal EnableDelayedExpansion

color 0A
title TrifectaOmni - One-Click Setup and Launch

echo.
echo ================================================================================
echo.
echo           TRIFECTA OMNI - ONE CLICK INSTALLER (WINDOWS)
echo.
echo       AI-Powered Trading System with Live Demo Capabilities
echo.
echo ================================================================================
echo.

REM Check if Python is installed
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo [OK] Python found

REM Check Python version
echo.
echo [*] Verifying Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [X] Python 3.8 or higher required
    pause
    exit /b 1
)
echo [OK] Python version compatible

REM Check if pip is available
echo.
echo [*] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [X] pip not found! Installing pip...
    python -m ensurepip --default-pip
)
echo [OK] pip available

REM Check if Git is installed (optional but recommended)
echo.
echo [*] Checking Git (optional)...
git --version >nul 2>&1
if errorlevel 1 (
    echo [!] Git not found (optional - for updates)
    echo    Download from https://git-scm.com/download/win
) else (
    git --version
    echo [OK] Git found
)

REM Create virtual environment if it doesn't exist
echo.
echo [*] Setting up virtual environment...
if not exist "venv" (
    echo Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [X] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [X] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Upgrade pip
echo.
echo [*] Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel --quiet
echo [OK] pip upgraded

REM Install requirements
echo.
echo [*] Installing Python dependencies (this may take a few minutes)...
echo     Please be patient...
echo.

REM Check if requirements.txt exists, if not create minimal one
if not exist "requirements.txt" (
    echo Creating requirements.txt...
    (
        echo numpy==1.24.3
        echo pandas==2.0.3
        echo scikit-learn==1.3.0
        echo torch==2.0.1
        echo tensorflow==2.13.0
        echo yfinance==0.2.28
        echo ccxt==4.0.0
        echo websockets==11.0.3
        echo fastapi==0.103.0
        echo uvicorn==0.23.2
        echo pydantic==2.3.0
        echo python-dotenv==1.0.0
        echo aiohttp==3.8.5
        echo psutil==5.9.5
        echo requests==2.31.0
    ) > requirements.txt
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Some packages failed to install
    echo     Continuing anyway...
)
echo [OK] Dependencies installed

REM Install package in development mode
echo.
echo [*] Installing TrifectaOmni package...
if exist "setup.py" (
    python -m pip install -e . --quiet
    echo [OK] Package installed
) else (
    echo [!] setup.py not found - skipping package install
)

REM Create necessary directories
echo.
echo [*] Creating directory structure...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "data\market_data" mkdir data\market_data
if not exist "data\models" mkdir data\models
if not exist "dashboard" mkdir dashboard
echo [OK] Directories created

REM Create .env if it doesn't exist
echo.
echo [*] Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from template...
        copy .env.example .env >nul
        echo [OK] .env created from template
        echo.
        echo [!] IMPORTANT: Edit .env file to add your API credentials
        echo     For demo mode, no configuration needed!
    ) else (
        echo [!] .env.example not found - will run in demo mode
    )
) else (
    echo [OK] .env already configured
)

REM Installation complete
echo.
echo ================================================================================
echo.
echo                   INSTALLATION COMPLETE!
echo.
echo ================================================================================
echo.

REM Ask user which mode to run
echo.
echo Select running mode:
echo.
echo   1. Demo Mode (Free, No API Keys Required)
echo      - Uses Yahoo Finance data (~60s delay)
echo      - Perfect for testing and learning
echo      - No configuration needed
echo.
echo   2. Production Mode (Real-Time APIs)
echo      - Uses your configured APIs from .env
echo      - Real-time data (^<1s latency)
echo      - Requires API configuration
echo.
echo   3. Exit (Setup Complete, Run Later)
echo.

set /p MODE="Enter your choice (1, 2, or 3): "

if "%MODE%"=="1" goto :demo_mode
if "%MODE%"=="2" goto :production_mode
if "%MODE%"=="3" goto :exit_success
echo Invalid choice. Starting demo mode...
goto :demo_mode

:demo_mode
echo.
echo ================================================================================
echo   LAUNCHING DEMO MODE
echo ================================================================================
echo.
echo Starting real-time multi-asset scanner (Demo)...
echo.
echo Dashboard will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the scanner
echo.
python realtime_multi_asset_demo.py
goto :end

:production_mode
echo.
echo ================================================================================
echo   LAUNCHING PRODUCTION MODE
echo ================================================================================
echo.

REM Check if .env is configured
if not exist ".env" (
    echo [!] .env file not found!
    echo     Creating from template...
    if exist ".env.example" (
        copy .env.example .env >nul
    )
    echo.
    echo [!] Please edit .env file with your API credentials
    echo     Then run this script again
    pause
    exit /b 0
)

echo Starting real-time multi-asset scanner (Production)...
echo.
echo API Status Check:
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('  MT5:', 'Configured' if os.getenv('MT5_LOGIN') else 'Not Configured'); print('  CCXT: Available (no keys needed for data)'); print('  DEX:', 'Configured' if os.getenv('DEX_RPC') else 'Not Configured'); print('  Pocket:', 'Configured' if os.getenv('POCKET_TOKEN') else 'Not Configured')" 2>nul
echo.
echo Dashboard will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the scanner
echo.
python realtime_multi_asset_demo_production.py
goto :end

:exit_success
echo.
echo Setup complete! To run later, use:
echo.
echo   Demo Mode:       install_and_run.bat
echo   Production Mode: install_and_run.bat
echo.
echo Or run directly:
echo   Demo:       venv\Scripts\activate ^&^& python realtime_multi_asset_demo.py
echo   Production: venv\Scripts\activate ^&^& python realtime_multi_asset_demo_production.py
echo.
pause
exit /b 0

:end
echo.
echo ================================================================================
echo   Scanner stopped
echo ================================================================================
echo.
pause
exit /b 0
