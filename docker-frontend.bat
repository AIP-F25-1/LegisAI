@echo off
REM Start Frontend with Docker

echo Starting LegisAI Frontend with Docker...
echo.

REM Check Docker availability
echo Checking Docker...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon is not running!
    echo.
    echo SOLUTION:
    echo    1. Start Docker Desktop from the Start Menu
    echo    2. Wait for Docker Desktop to fully start
    echo    3. Run this script again
    echo.
    pause
    exit /b 1
)
echo SUCCESS: Docker is running

REM Check if backend is running
echo Checking if backend is running...
docker ps --filter "name=legisai-backend" --format "{{.Names}}" | findstr "legisai-backend" > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend container is not running!
    echo Please start the backend first:
    echo   Run: docker-backend.bat
    echo.
    pause
    exit /b 1
)

REM Build and start frontend container (from project root)
echo Building and starting frontend container...
if exist docker-compose.yml (
    docker compose build frontend
    docker compose up -d frontend
) else (
    echo ERROR: docker-compose.yml not found in current directory
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Waiting for frontend to be ready...
timeout /t 10 /nobreak > nul

REM Check frontend health
echo Checking frontend health...
curl -f http://localhost:5173 > nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Frontend is healthy!
) else (
    echo WARNING: Frontend may still be starting
)

echo.
echo SUCCESS: LegisAI Frontend is running!
echo.
echo Services:
echo    Frontend:  http://localhost:5173
echo    Backend:   http://localhost:8000
echo.
echo Commands:
echo    View logs:    docker compose logs -f frontend
echo    Stop:         docker compose stop frontend
echo    Status:       docker compose ps frontend
echo.
pause

