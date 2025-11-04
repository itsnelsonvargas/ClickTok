@echo off
REM Deployment Validation Script for Windows
REM Run this before deploying to another computer

echo ==========================================
echo   ClickTok Deployment Validation
echo ==========================================
echo.

set PASSED=0
set FAILED=0
set WARNINGS=0

REM Check 1: Required files exist
echo === Checking Required Files ===
call :check_file "Dockerfile"
call :check_file "docker-compose.yml"
call :check_file ".dockerignore"
call :check_file "docker-entrypoint.sh"
call :check_file "requirements.txt"
call :check_file "main.py"
call :check_file "env.example"
call :check_file "config\credentials.json.example"
call :check_file "README.md"
call :check_file "DOCKER_README.md"
echo.

REM Check 2: Sensitive files
echo === Checking for Sensitive Files ===
if exist ".env" (
    findstr /C:"YOUR_" .env >nul 2>&1
    if %errorlevel%==0 (
        echo [PASS] .env has placeholder values
        set /a PASSED+=1
    ) else (
        echo [WARNING] .env may contain real values
        set /a WARNINGS+=1
    )
)

if exist "config\credentials.json" (
    findstr /C:"YOUR_" config\credentials.json >nul 2>&1
    if %errorlevel%==0 (
        echo [PASS] credentials.json has placeholder values
        set /a PASSED+=1
    ) else (
        echo [WARNING] credentials.json may contain real credentials
        set /a WARNINGS+=1
    )
)
echo.

REM Check 3: Docker availability
echo === Checking Docker ===
docker --version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Docker is installed
    set /a PASSED+=1

    docker info >nul 2>&1
    if %errorlevel%==0 (
        echo [PASS] Docker daemon is running
        set /a PASSED+=1
    ) else (
        echo [WARNING] Docker daemon not running
        set /a WARNINGS+=1
    )
) else (
    echo [WARNING] Docker not installed
    set /a WARNINGS+=1
)

docker-compose --version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Docker Compose is installed
    set /a PASSED+=1
) else (
    echo [WARNING] Docker Compose not installed
    set /a WARNINGS+=1
)
echo.

REM Check 4: Documentation
echo === Checking Documentation ===
call :check_file "README.md"
call :check_file "DOCKER_README.md"
call :check_file "DOCKER_QUICKSTART.md"
call :check_file "DEPLOY_ANYWHERE.md"
echo.

REM Check 5: Scripts
echo === Checking Scripts ===
call :check_file "docker-start.bat"
call :check_file "docker-start.sh"
call :check_file "docker-test.bat"
call :check_file "docker-test.sh"
echo.

REM Check 6: Git status
echo === Checking Git ===
if exist ".git" (
    git status --short 2>nul | findstr /R "." >nul
    if %errorlevel%==0 (
        echo [WARNING] Uncommitted changes exist
        set /a WARNINGS+=1
        git status --short
    ) else (
        echo [PASS] No uncommitted changes
        set /a PASSED+=1
    )
) else (
    echo [INFO] Not a git repository
)
echo.

REM Summary
echo ==========================================
echo   Validation Summary
echo ==========================================
echo Passed:   %PASSED%
echo Warnings: %WARNINGS%
echo Failed:   %FAILED%
echo.

if %FAILED%==0 (
    echo [SUCCESS] READY FOR DEPLOYMENT
    echo.
    echo Your ClickTok project is ready to deploy!
    echo.
    echo Deployment options:
    echo   1. Git clone: git push ^&^& (on target^) git clone ^<repo^>
    echo   2. Folder copy: Copy entire ClickTok folder to target
    echo   3. Docker image: docker save clicktok:latest ^| gzip ^> clicktok.tar.gz
    echo.
    echo On target computer:
    echo   1. Install Docker Desktop
    echo   2. Double-click docker-start.bat or run: docker-compose up --build
    echo.
) else (
    echo [ERROR] NOT READY FOR DEPLOYMENT
    echo.
    echo Please fix the issues above before deploying.
    echo.
)

pause
exit /b 0

REM Function to check if file exists
:check_file
if exist %1 (
    echo [PASS] %~1 exists
    set /a PASSED+=1
) else (
    echo [FAIL] %~1 missing
    set /a FAILED+=1
)
exit /b 0
