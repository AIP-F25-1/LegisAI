# Docker start script for LegisAI Backend (PowerShell)

Write-Host "🐳 Starting LegisAI Backend with Docker Compose..." -ForegroundColor Cyan

# Check Docker availability first
Write-Host "🔍 Checking Docker..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker daemon is not running!" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Solution:" -ForegroundColor Cyan
        Write-Host "   1. Start Docker Desktop from the Start Menu" -ForegroundColor White
        Write-Host "   2. Wait for Docker Desktop to fully start (whale icon in system tray)" -ForegroundColor White
        Write-Host "   3. Run this script again" -ForegroundColor White
        Write-Host ""
        Write-Host "   Trying to start Docker Desktop automatically..." -ForegroundColor Yellow
        try {
            if (Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe") {
                Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
                Write-Host "   ✅ Docker Desktop starting... Please wait and run this script again in ~30 seconds" -ForegroundColor Green
            } elseif (Test-Path "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe") {
                Start-Process "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
                Write-Host "   ✅ Docker Desktop starting... Please wait and run this script again in ~30 seconds" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Docker Desktop not found in default location" -ForegroundColor Red
                Write-Host "   Please start Docker Desktop manually" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ❌ Could not start Docker Desktop automatically" -ForegroundColor Red
        }
        exit 1
    }
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to Docker daemon: $_" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "✅ Created .env file. Please update with your API keys." -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env.example not found. Creating basic .env..." -ForegroundColor Yellow
        @"
OLLAMA_HOST=http://ollama:11434
PORT=8000
"@ | Out-File -FilePath .env -Encoding utf8
    }
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Cyan
@("data\vector_store", "uploads", "legal_data") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Build and start containers
Write-Host "🔨 Building and starting containers..." -ForegroundColor Cyan
docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers. Check Docker is running." -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check if Ollama is running and pull model if needed
Write-Host "🤖 Checking Ollama..." -ForegroundColor Cyan
try {
    $ollamaList = docker exec legisai-ollama ollama list 2>&1
    if ($ollamaList -match "llama3.1:8b") {
        Write-Host "✅ Ollama model already installed" -ForegroundColor Green
    } else {
        Write-Host "📥 Pulling Ollama model (llama3.1:8b)..." -ForegroundColor Yellow
        Write-Host "⏳ This may take several minutes (model size ~4.7GB)..." -ForegroundColor Yellow
        docker exec legisai-ollama ollama pull llama3.1:8b
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Model downloaded successfully!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Model download may have failed. Check logs." -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "⚠️  Could not check Ollama. Container may still be starting." -ForegroundColor Yellow
    Write-Host "   Wait a few minutes and check manually: docker exec legisai-ollama ollama list" -ForegroundColor Yellow
}

# Check backend health
Write-Host "🏥 Checking backend health..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend returned status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Backend may still be starting. Check logs with: docker compose logs -f backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ LegisAI Backend is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 View logs:    docker compose logs -f" -ForegroundColor Cyan
Write-Host "🛑 Stop:         docker compose down" -ForegroundColor Cyan
Write-Host "🔍 Status:       docker compose ps" -ForegroundColor Cyan
Write-Host "🌐 API:          http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

