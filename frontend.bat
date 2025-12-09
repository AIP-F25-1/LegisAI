@echo off
REM Start Frontend Locally (without Docker)

echo Starting LegisAI Frontend (Local Mode)...
echo.

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

REM Check if backend is running
echo Checking backend connection...
curl -f http://localhost:8000/api/health > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend is not running!
    echo Please start the backend first:
    echo   - Local: run backend.bat
    echo   - Docker: run docker-backend.bat
    echo.
    echo Starting frontend anyway (backend may start later)...
    echo.
)

echo.
echo Starting Vite development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev

