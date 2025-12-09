# Script to start Docker Desktop on Windows

Write-Host "🚀 Starting Docker Desktop..." -ForegroundColor Cyan

$dockerPaths = @(
    "C:\Program Files\Docker\Docker\Docker Desktop.exe",
    "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
    "$env:LOCALAPPDATA\Docker\Docker Desktop.exe"
)

$found = $false
foreach ($path in $dockerPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Found Docker Desktop at: $path" -ForegroundColor Green
        Write-Host "   Starting Docker Desktop..." -ForegroundColor Cyan
        try {
            Start-Process $path
            Write-Host "✅ Docker Desktop is starting..." -ForegroundColor Green
            Write-Host ""
            Write-Host "⏳ Please wait for Docker Desktop to fully start (~30-60 seconds)" -ForegroundColor Yellow
            Write-Host "   You'll see a whale icon in the system tray when it's ready" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   Check status with: docker info" -ForegroundColor Cyan
            $found = $true
            break
        } catch {
            Write-Host "❌ Failed to start Docker Desktop: $_" -ForegroundColor Red
        }
    }
}

if (-not $found) {
    Write-Host "❌ Docker Desktop not found in common locations" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Please:" -ForegroundColor Cyan
    Write-Host "   1. Install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "   2. Or start Docker Desktop manually from Start Menu" -ForegroundColor White
    exit 1
}

# Wait and check if Docker starts
Write-Host ""
Write-Host "⏳ Waiting for Docker to be ready..." -ForegroundColor Cyan
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    try {
        $dockerInfo = docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker is ready!" -ForegroundColor Green
            exit 0
        }
    } catch {
        # Continue waiting
    }
    $attempt++
    Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
}

Write-Host "⚠️  Docker Desktop is starting but not ready yet" -ForegroundColor Yellow
Write-Host "   Please wait a bit longer and check with: docker info" -ForegroundColor Yellow

