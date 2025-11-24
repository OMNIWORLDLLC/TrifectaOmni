@echo off
REM ============================================================================
REM TrifectaOmni - Test Suite Runner
REM ============================================================================

color 0D
title TrifectaOmni - Test Suite

echo.
echo ================================================================================
echo   TRIFECTA OMNI - COMPREHENSIVE TEST SUITE
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

echo Select test suite to run:
echo.
echo   1. Demo Setup Verification
echo   2. Arbitrage Calculations Test
echo   3. Token Equivalence Test
echo   4. Full Test Suite (All Tests)
echo   5. Exit
echo.

set /p TEST_CHOICE="Enter your choice (1-5): "

if "%TEST_CHOICE%"=="1" goto :test_demo
if "%TEST_CHOICE%"=="2" goto :test_arbitrage
if "%TEST_CHOICE%"=="3" goto :test_tokens
if "%TEST_CHOICE%"=="4" goto :test_all
if "%TEST_CHOICE%"=="5" exit /b 0

echo Invalid choice
pause
exit /b 1

:test_demo
echo.
echo ================================================================================
echo   Testing Demo Setup
echo ================================================================================
echo.
python test_demo_setup.py
goto :end

:test_arbitrage
echo.
echo ================================================================================
echo   Testing Arbitrage Calculations
echo ================================================================================
echo.
python test_arbitrage_calculations.py
goto :end

:test_tokens
echo.
echo ================================================================================
echo   Testing Token Equivalence System
echo ================================================================================
echo.
python test_token_equivalence.py
goto :end

:test_all
echo.
echo ================================================================================
echo   Running Full Test Suite
echo ================================================================================
echo.
echo [1/3] Demo Setup Test...
python test_demo_setup.py
echo.
echo [2/3] Arbitrage Calculations Test...
python test_arbitrage_calculations.py
echo.
echo [3/3] Token Equivalence Test...
python test_token_equivalence.py
echo.
echo ================================================================================
echo   All Tests Complete
echo ================================================================================
goto :end

:end
echo.
pause
