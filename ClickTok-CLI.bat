@echo off
REM ClickTok - CLI Launcher
REM Double-click this file to launch ClickTok in CLI mode

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Clear screen for clean display
cls

echo.
echo ============================================================
echo   ClickTok - CLI Mode
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Launch the CLI application
python main.py --cli

pause
