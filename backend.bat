@echo off
REM Start Backend Locally (without Docker)

echo Starting LegisAI Backend (Local Mode)...
echo.

cd backend

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist venv\Lib\site-packages\fastapi (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if Ollama is running locally
echo Checking Ollama...
curl -f http://127.0.0.1:11434/api/tags > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama is not running locally!
    echo Please start Ollama first:
    echo   1. Install Ollama from https://ollama.ai
    echo   2. Run: ollama serve
    echo   3. Pull model: ollama pull llama3.1:8b
    echo.
    pause
    exit /b 1
)

REM Create .env if it doesn't exist
if not exist .env (
    if exist .env.example (
        copy .env.example .env
    ) else (
        echo OLLAMA_HOST=http://127.0.0.1:11434 > .env
        echo PORT=8000 >> .env
    )
)

REM Create necessary directories
if not exist data\vector_store mkdir data\vector_store
if not exist uploads mkdir uploads

echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

