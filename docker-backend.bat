@echo off
REM Start Backend with Docker

echo Starting LegisAI Backend with Docker...
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

cd backend

REM Check if .env file exists
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo Created .env file from .env.example
    ) else (
        echo OLLAMA_HOST=http://ollama:11434 > .env
        echo PORT=8000 >> .env
        echo Created basic .env file
    )
)

REM Create necessary directories
if not exist data\vector_store mkdir data\vector_store
if not exist uploads mkdir uploads
if not exist legal_data mkdir legal_data

REM Build and start containers
echo Building and starting containers...
docker compose up --build -d

echo Waiting for services to be healthy...
timeout /t 10 /nobreak > nul

REM Check Ollama model
echo Checking Ollama model...
timeout /t 5 /nobreak > nul
docker exec legisai-ollama ollama list | findstr "llama3.1:8b" > nul 2>&1
if %errorlevel% neq 0 (
    echo Pulling Ollama model (llama3.1:8b)...
    echo This may take several minutes (~4.7GB)...
    docker exec legisai-ollama ollama pull llama3.1:8b
)

REM Check backend health
echo Checking backend health...
timeout /t 5 /nobreak > nul
curl -f http://localhost:8000/api/health > nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Backend is healthy!
) else (
    echo WARNING: Backend may still be starting
)

echo.
echo SUCCESS: LegisAI Backend is running!
echo.
echo Services:
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo    Ollama:    http://localhost:11434
echo.
echo Commands:
echo    View logs:    docker compose logs -f
echo    Stop:         docker compose down
echo    Status:       docker compose ps
echo.
pause

