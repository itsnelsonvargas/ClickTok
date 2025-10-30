@echo off
REM ClickTok - Windows Setup Script
REM One-command installation for Windows users

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ============================================================
echo   ClickTok - Automated Setup for Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if setup.py exists
if not exist "setup.py" (
    echo [ERROR] setup.py not found in current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Run the Python setup script
echo Starting installation...
echo.
python "%~dp0setup.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed. See error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup complete! ClickTok is ready to use.
echo.
echo To launch: python main.py
echo ============================================================
echo.
pause
