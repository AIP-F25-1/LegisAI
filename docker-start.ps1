# Docker start script for LegisAI (Full Stack - PowerShell)

Write-Host "Starting LegisAI Full Stack with Docker Compose..." -ForegroundColor Cyan

# Check Docker availability first
Write-Host "Checking Docker..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker daemon is not running!" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUTION:" -ForegroundColor Cyan
        Write-Host "   1. Start Docker Desktop from the Start Menu" -ForegroundColor White
        Write-Host "   2. Wait for Docker Desktop to fully start (whale icon in system tray)" -ForegroundColor White
        Write-Host "   3. Run this script again" -ForegroundColor White
        Write-Host ""
        Write-Host "   Trying to start Docker Desktop automatically..." -ForegroundColor Yellow
        try {
            if (Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe") {
                Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
                Write-Host "   Docker Desktop starting... Please wait and run this script again in ~30 seconds" -ForegroundColor Green
            } elseif (Test-Path "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe") {
                Start-Process "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
                Write-Host "   Docker Desktop starting... Please wait and run this script again in ~30 seconds" -ForegroundColor Green
            } else {
                Write-Host "   Docker Desktop not found in default location" -ForegroundColor Red
                Write-Host "   Please start Docker Desktop manually" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   Could not start Docker Desktop automatically" -ForegroundColor Red
        }
        exit 1
    }
    Write-Host "SUCCESS: Docker is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Cannot connect to Docker daemon: $_" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists in backend
if (-not (Test-Path backend\.env)) {
    Write-Host "WARNING: .env file not found in backend. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path backend\.env.example) {
        Copy-Item backend\.env.example backend\.env
        Write-Host "SUCCESS: Created .env file. Please update with your API keys." -ForegroundColor Green
    } else {
        Write-Host "WARNING: .env.example not found. Creating basic .env..." -ForegroundColor Yellow
        @"
OLLAMA_HOST=http://ollama:11434
PORT=8000
"@ | Out-File -FilePath backend\.env -Encoding utf8
    }
}

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Cyan
@("backend\data\vector_store", "backend\uploads", "backend\legal_data") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor Cyan
Write-Host "   This may take several minutes on first run..." -ForegroundColor Yellow
docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start containers. Check Docker is running." -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for services to be healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check if Ollama is running and pull model if needed
Write-Host "Checking Ollama..." -ForegroundColor Cyan
Start-Sleep -Seconds 5  # Wait for Ollama to be ready

try {
    # Check if Ollama container is running
    $ollamaStatus = docker ps --filter "name=legisai-ollama" --format "{{.Status}}" 2>&1
    if ($LASTEXITCODE -ne 0 -or -not $ollamaStatus) {
        Write-Host "WARNING: Ollama container may not be running yet" -ForegroundColor Yellow
        Write-Host "   Will check again after containers stabilize..." -ForegroundColor Yellow
    } else {
        # Wait a bit more for Ollama to fully start
        Start-Sleep -Seconds 3
        
        # Check if model is already installed
        $ollamaList = docker exec legisai-ollama ollama list 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($ollamaList -match "llama3.1:8b") {
                Write-Host "SUCCESS: Ollama model already installed" -ForegroundColor Green
            } else {
                Write-Host "Pulling Ollama model (llama3.1:8b)..." -ForegroundColor Yellow
                Write-Host "   This may take several minutes (model size ~4.7GB)..." -ForegroundColor Yellow
                Write-Host "   You can monitor progress in another terminal with: docker compose logs -f ollama" -ForegroundColor Cyan
                
                # Run pull in background or show progress
                docker exec legisai-ollama ollama pull llama3.1:8b
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "SUCCESS: Model downloaded successfully!" -ForegroundColor Green
                } else {
                    Write-Host "WARNING: Model download may have failed or is still in progress." -ForegroundColor Yellow
                    Write-Host "   Check status with: docker exec legisai-ollama ollama list" -ForegroundColor Cyan
                }
            }
        } else {
            Write-Host "WARNING: Could not check Ollama models. Container may still be starting." -ForegroundColor Yellow
            Write-Host "   Wait a few minutes and check manually: docker exec legisai-ollama ollama list" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "WARNING: Could not check Ollama. Error: $_" -ForegroundColor Yellow
    Write-Host "   You can manually pull the model later with:" -ForegroundColor Cyan
    Write-Host "   docker exec legisai-ollama ollama pull llama3.1:8b" -ForegroundColor White
}

# Check backend health
Write-Host "Checking backend health..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Backend is healthy!" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Backend returned status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Backend may still be starting. Check logs with: docker compose logs -f backend" -ForegroundColor Yellow
}

# Check frontend health
Write-Host "Checking frontend health..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Frontend is healthy!" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Frontend returned status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Frontend may still be starting. Check logs with: docker compose logs -f frontend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "SUCCESS: LegisAI Full Stack is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Ollama:    http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "   View logs:    docker compose logs -f" -ForegroundColor White
Write-Host "   Stop:         docker compose down" -ForegroundColor White
Write-Host "   Status:       docker compose ps" -ForegroundColor White
Write-Host ""

