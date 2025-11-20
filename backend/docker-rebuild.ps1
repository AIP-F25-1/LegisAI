# Docker Rebuild Script - Clears cache and rebuilds containers

Write-Host "Clearing Docker cache..." -ForegroundColor Cyan

# Stop and remove containers
Write-Host "Stopping containers..." -ForegroundColor Yellow
docker compose down -v 2>&1 | Out-Null

# Clear build cache
Write-Host "Clearing build cache..." -ForegroundColor Yellow
docker builder prune -f 2>&1 | Out-Null

Write-Host "SUCCESS: Cache cleared" -ForegroundColor Green
Write-Host ""
Write-Host "Building containers (no cache)..." -ForegroundColor Cyan
Write-Host "   This will take several minutes..." -ForegroundColor Yellow
Write-Host ""

# Build without cache
docker compose build --no-cache

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting containers..." -ForegroundColor Cyan
    docker compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS: Containers started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "View logs:    docker compose logs -f" -ForegroundColor Cyan
        Write-Host "Status:       docker compose ps" -ForegroundColor Cyan
        Write-Host "API:          http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "ERROR: Failed to start containers" -ForegroundColor Red
        Write-Host "   Check logs with: docker compose logs" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Write-Host "   Check the error messages above" -ForegroundColor Yellow
    exit 1
}
