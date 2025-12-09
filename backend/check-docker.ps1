# Check Docker availability
Write-Host "Checking Docker..." -ForegroundColor Cyan

# Check if Docker is installed
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Docker installed: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
        Write-Host "   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Docker is not installed" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if Docker daemon is running
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Docker daemon is running" -ForegroundColor Green
        
        # Get Docker Compose version
        try {
            $composeVersion = docker compose version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "SUCCESS: Docker Compose available: $composeVersion" -ForegroundColor Green
            }
        } catch {
            Write-Host "WARNING: Docker Compose may not be available" -ForegroundColor Yellow
        }
        
        return $true
    } else {
        Write-Host "ERROR: Docker daemon is not running" -ForegroundColor Red
        Write-Host "   Error: $dockerInfo" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "SOLUTION:" -ForegroundColor Cyan
        Write-Host "   1. Start Docker Desktop from the Start Menu" -ForegroundColor White
        Write-Host "   2. Wait for Docker Desktop to fully start (whale icon in system tray)" -ForegroundColor White
        Write-Host "   3. Run this script again" -ForegroundColor White
        Write-Host ""
        Write-Host "   Or start Docker Desktop with:" -ForegroundColor Cyan
        $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        Write-Host "   Start-Process `"$dockerPath`"" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "ERROR: Cannot connect to Docker daemon" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please start Docker Desktop first" -ForegroundColor Cyan
    exit 1
}
