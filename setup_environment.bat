@echo off
REM ============================================================================
REM TrifectaOmni - Environment Setup Only (No Launch)
REM ============================================================================

color 0C
title TrifectaOmni - Environment Setup

echo.
echo ================================================================================
echo   TRIFECTA OMNI - ENVIRONMENT SETUP
echo ================================================================================
echo.
echo This script will:
echo   - Create Python virtual environment
echo   - Install all dependencies
echo   - Setup directory structure
echo   - Prepare configuration files
echo.
echo It will NOT launch the scanner automatically.
echo.

set /p CONTINUE="Continue? (Y/N): "
if /i not "%CONTINUE%"=="Y" exit /b 0

echo.
echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
python --version

echo.
echo [*] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [*] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo [*] Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo Creating minimal requirements.txt...
    (
        echo numpy==1.24.3
        echo pandas==2.0.3
        echo scikit-learn==1.3.0
        echo yfinance==0.2.28
        echo ccxt==4.0.0
        echo websockets==11.0.3
        echo fastapi==0.103.0
        echo uvicorn==0.23.2
        echo pydantic==2.3.0
        echo python-dotenv==1.0.0
        echo aiohttp==3.8.5
    ) > requirements.txt
    pip install -r requirements.txt
)

echo.
echo [*] Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "dashboard" mkdir dashboard
echo [OK] Directories created

echo.
echo [*] Setting up configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] .env created from template
    )
)

echo.
echo ================================================================================
echo   SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo.
echo   1. (Optional) Edit .env file with your API credentials
echo      notepad .env
echo.
echo   2. Run demo scanner:
echo      quick_start_demo.bat
echo.
echo   3. Or run production scanner:
echo      launch_production.bat
echo.
echo   4. Or use main installer:
echo      install_and_run.bat
echo.

pause
