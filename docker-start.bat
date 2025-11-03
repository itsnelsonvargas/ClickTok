@echo off
REM ClickTok Docker Quick Start Script for Windows

echo ==========================================
echo   ClickTok Docker Quick Start
echo ==========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if credentials.json exists
if not exist "config\credentials.json" (
    echo [WARNING] config\credentials.json not found
    if exist "config\credentials.json.example" (
        echo Creating credentials.json from example...
        copy "config\credentials.json.example" "config\credentials.json" >nul
        echo [OK] Created. You can edit it later in the GUI.
    )
    echo.
)

REM Ask user which mode to run
echo Select mode:
echo   1. GUI Mode (Default)
echo   2. CLI Mode
echo   3. Rebuild and Start (if you changed dependencies)
echo   4. Stop and Clean Up
echo.
set /p mode="Enter choice (1-4, default 1): "

if "%mode%"=="" set mode=1

if "%mode%"=="1" (
    echo.
    echo Starting ClickTok in GUI mode...
    echo.
    docker-compose up
    goto end
)

if "%mode%"=="2" (
    echo.
    echo Starting ClickTok in CLI mode...
    echo.
    docker-compose run --rm clicktok-cli
    goto end
)

if "%mode%"=="3" (
    echo.
    echo Rebuilding and starting ClickTok...
    echo This may take a few minutes...
    echo.
    docker-compose up --build
    goto end
)

if "%mode%"=="4" (
    echo.
    echo Stopping and cleaning up...
    docker-compose down
    echo.
    echo Done! Containers stopped.
    goto end
)

echo Invalid choice!

:end
echo.
pause
