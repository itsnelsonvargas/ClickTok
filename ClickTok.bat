@echo off
REM ClickTok - GUI Launcher
REM Double-click this file to launch ClickTok

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Prevent window from closing on error
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit /b

REM Clear screen for clean display
cls

echo.
echo ============================================================
echo   ClickTok - TikTok Affiliate Marketing Automation
echo ============================================================
echo.
echo Current directory: %CD%
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

REM Check if dependencies are installed (quick check for moviepy)
python -c "import moviepy" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   DEPENDENCIES NOT INSTALLED - Auto-Installing...
    echo ============================================================
    echo.
    echo First time setup detected!
    echo Installing dependencies automatically...
    echo This will take about 5-10 minutes. Please wait...
    echo.

    REM Try setup once
    call setup.bat
    if errorlevel 1 (
        echo.
        echo ============================================================
        echo   First Install Attempt Failed - Retrying...
        echo ============================================================
        echo.
        echo Trying alternative installation method...
        echo.

        REM Try direct pip install of critical packages
        echo Installing critical packages directly...
        python -m pip install --upgrade pip
        python -m pip install requests beautifulsoup4 lxml Pillow numpy moviepy imageio imageio-ffmpeg playwright python-dotenv

        if errorlevel 1 (
            echo.
            echo ============================================================
            echo   SETUP FAILED AFTER RETRY
            echo ============================================================
            echo.
            echo Automatic installation failed after multiple attempts.
            echo.
            echo Please try manual steps:
            echo   1. Close this window
            echo   2. See: PYTHON_313_FIX.txt
            echo   3. Or see: INSTALL.md for troubleshooting
            echo.
            pause
            exit /b 1
        )
    )
    echo.
    echo ============================================================
    echo   Setup Complete! Starting ClickTok now...
    echo ============================================================
    echo.
)

echo Starting ClickTok GUI...
echo.

REM Launch the GUI application
python main.py

REM Check if launch failed
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   Launch Failed - Checking Dependencies...
    echo ============================================================
    echo.

    REM Check if it's a dependency issue
    python -c "import moviepy.editor" >nul 2>&1
    if errorlevel 1 (
        echo Dependency issue detected!
        echo Attempting one more repair...
        echo.

        REM Try to fix with direct install
        python -m pip install --force-reinstall moviepy
        python -m pip install --force-reinstall imageio imageio-ffmpeg

        echo.
        echo Retrying launch...
        echo.
        python main.py

        if errorlevel 1 (
            echo.
            echo ============================================================
            echo   ERROR PERSISTS
            echo ============================================================
            echo.
            echo ClickTok still cannot start after automatic repairs.
            echo.
            echo Manual intervention recommended:
            echo   1. See: PYTHON_313_FIX.txt for Python 3.13 issues
            echo   2. See: INSTALL.md for detailed troubleshooting
            echo   3. Try: python -m pip install --force-reinstall moviepy
            echo.
            pause
        ) else (
            echo.
            echo ============================================================
            echo   ClickTok Launched Successfully After Repair!
            echo ============================================================
            echo.
            echo The repair was successful and ClickTok is now running.
            echo You can close this console window.
            echo.
            pause
        )
    ) else (
        echo.
        echo ============================================================
        echo   ERROR OCCURRED
        echo ============================================================
        echo.
        echo ClickTok encountered an error (not dependency-related).
        echo.
        echo Check:
        echo   1. logs/system.log for details
        echo   2. Error messages above
        echo.
        echo Press any key to close...
        pause >nul
    )
) else (
    echo.
    echo ============================================================
    echo   ClickTok Launched Successfully!
    echo ============================================================
    echo.
    echo If the GUI window opened, you can close this console.
    echo Or press any key to close this window...
    pause >nul
)
