# Script to pull Ollama model into the Docker container

Write-Host "Pulling Ollama model (llama3.1:8b)..." -ForegroundColor Cyan
Write-Host "This may take several minutes (~4.7GB download)..." -ForegroundColor Yellow
Write-Host ""

# Check if Ollama container is running
$ollamaRunning = docker ps --filter "name=legisai-ollama" --format "{{.Names}}"
if (-not $ollamaRunning) {
    Write-Host "ERROR: Ollama container is not running!" -ForegroundColor Red
    Write-Host "Start it with: docker compose up -d ollama" -ForegroundColor Yellow
    exit 1
}

Write-Host "Ollama container is running. Pulling model..." -ForegroundColor Green
Write-Host ""

# Pull the model
docker exec legisai-ollama ollama pull llama3.1:8b

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Model downloaded!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying installation..." -ForegroundColor Cyan
    docker exec legisai-ollama ollama list
    Write-Host ""
    Write-Host "You may need to restart the backend for it to detect the model:" -ForegroundColor Yellow
    Write-Host "  docker compose restart backend" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "ERROR: Model download failed. Check your internet connection and try again." -ForegroundColor Red
    exit 1
}

