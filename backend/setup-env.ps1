# Setup script to create .env file with API key

Write-Host "LegisAI Environment Setup" -ForegroundColor Cyan
Write-Host ""

# Check if .env already exists
if (Test-Path .env) {
    Write-Host "WARNING: .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "Setting up environment variables..." -ForegroundColor Green
Write-Host ""

# Get API key
Write-Host "CourtListener API Key (optional):" -ForegroundColor Cyan
Write-Host "  - Leave empty to skip" -ForegroundColor Gray
Write-Host "  - Or enter your API token" -ForegroundColor Gray
Write-Host "  - Or paste shared key from project owner" -ForegroundColor Gray
Write-Host ""
$apiKey = Read-Host "Enter API key (or press Enter to skip)"

# Create .env file
$envContent = @"
# LegisAI Backend Environment Variables

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434

# Server Configuration
PORT=8000
ENVIRONMENT=production

# CourtListener API (Optional)
COURTLISTENER_API_TOKEN=$apiKey

# Python Configuration
PYTHONPATH=/app
PYTHONUNBUFFERED=1
"@

$envContent | Out-File -FilePath .env -Encoding utf8 -NoNewline

Write-Host ""
Write-Host "✅ .env file created successfully!" -ForegroundColor Green
Write-Host ""

if ($apiKey) {
    Write-Host "API key configured. Restart backend to apply:" -ForegroundColor Cyan
    Write-Host "  docker compose restart backend" -ForegroundColor White
} else {
    Write-Host "No API key configured. You can add it later by:" -ForegroundColor Yellow
    Write-Host "  1. Edit backend/.env" -ForegroundColor White
    Write-Host "  2. Add: COURTLISTENER_API_TOKEN=your_key" -ForegroundColor White
    Write-Host "  3. Restart: docker compose restart backend" -ForegroundColor White
}

Write-Host ""

