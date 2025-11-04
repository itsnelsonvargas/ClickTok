@echo off
REM ClickTok Docker Setup Verification Script for Windows

echo ==========================================
echo   ClickTok Docker Setup Verification
echo ==========================================
echo.

set PASSED=0
set FAILED=0

REM Test 1: Docker installed
echo Testing: Docker installation...
docker --version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Docker installed
    docker --version
    set /a PASSED+=1
) else (
    echo [FAIL] Docker not found. Please install Docker Desktop.
    set /a FAILED+=1
)
echo.

REM Test 2: Docker running
echo Testing: Docker daemon running...
docker info >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Docker is running
    set /a PASSED+=1
) else (
    echo [FAIL] Docker daemon not running. Please start Docker Desktop.
    set /a FAILED+=1
)
echo.

REM Test 3: Docker Compose installed
echo Testing: Docker Compose installation...
docker-compose --version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Docker Compose installed
    docker-compose --version
    set /a PASSED+=1
) else (
    echo [FAIL] Docker Compose not found.
    set /a FAILED+=1
)
echo.

REM Test 4: Check required files
echo Checking required files...
if exist "Dockerfile" (
    echo [PASS] Dockerfile found
    set /a PASSED+=1
) else (
    echo [FAIL] Dockerfile missing
    set /a FAILED+=1
)

if exist "docker-compose.yml" (
    echo [PASS] docker-compose.yml found
    set /a PASSED+=1
) else (
    echo [FAIL] docker-compose.yml missing
    set /a FAILED+=1
)

if exist "requirements.txt" (
    echo [PASS] requirements.txt found
    set /a PASSED+=1
) else (
    echo [FAIL] requirements.txt missing
    set /a FAILED+=1
)

if exist "main.py" (
    echo [PASS] main.py found
    set /a PASSED+=1
) else (
    echo [FAIL] main.py missing
    set /a FAILED+=1
)
echo.

REM Test 5: Docker Compose config
echo Testing: Docker Compose configuration...
docker-compose config >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] docker-compose.yml is valid
    set /a PASSED+=1
) else (
    echo [FAIL] docker-compose.yml has errors
    set /a FAILED+=1
)
echo.

REM Test 6: Build Docker image
echo Building Docker image (this may take a few minutes)...
echo Please wait...
docker-compose build >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Docker image built successfully
    set /a PASSED+=1
) else (
    echo [FAIL] Build failed
    set /a FAILED+=1
)
echo.

REM Test 7: Test container
echo Testing container dependencies...
docker-compose run --rm clicktok python --version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Python available in container
    set /a PASSED+=1
) else (
    echo [FAIL] Python not available
    set /a FAILED+=1
)

docker-compose run --rm clicktok ffmpeg -version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] FFmpeg available in container
    set /a PASSED+=1
) else (
    echo [FAIL] FFmpeg not available
    set /a FAILED+=1
)

docker-compose run --rm clicktok python -c "import moviepy, playwright, requests, bs4" >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] Python dependencies installed
    set /a PASSED+=1
) else (
    echo [FAIL] Some Python dependencies missing
    set /a FAILED+=1
)
echo.

REM Summary
echo ==========================================
echo   Test Summary
echo ==========================================
echo Tests Passed: %PASSED%
echo Tests Failed: %FAILED%
echo.

if %FAILED%==0 (
    echo [SUCCESS] All tests passed!
    echo.
    echo Your Docker setup is ready to use!
    echo.
    echo Next steps:
    echo   1. Start the application:
    echo      docker-compose up
    echo.
    echo   2. Or use the quick-start script:
    echo      docker-start.bat
    echo.
    echo   3. Read the documentation:
    echo      DOCKER_README.md
    echo.
) else (
    echo [ERROR] Some tests failed
    echo.
    echo Please fix the issues above before running ClickTok.
    echo See DOCKER_README.md for troubleshooting.
    echo.
)

echo ==========================================
pause
