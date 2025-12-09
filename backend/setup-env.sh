#!/bin/bash
# Setup script to create .env file with API key

echo "LegisAI Environment Setup"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "WARNING: .env file already exists!"
    read -p "Do you want to overwrite it? (y/N) " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "Setting up environment variables..."
echo ""

# Get API key
echo "CourtListener API Key (optional):"
echo "  - Leave empty to skip"
echo "  - Or enter your API token"
echo "  - Or paste shared key from project owner"
echo ""
read -p "Enter API key (or press Enter to skip): " apiKey

# Create .env file
cat > .env << EOF
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
EOF

echo ""
echo "✅ .env file created successfully!"
echo ""

if [ -n "$apiKey" ]; then
    echo "API key configured. Restart backend to apply:"
    echo "  docker compose restart backend"
else
    echo "No API key configured. You can add it later by:"
    echo "  1. Edit backend/.env"
    echo "  2. Add: COURTLISTENER_API_TOKEN=your_key"
    echo "  3. Restart: docker compose restart backend"
fi

echo ""

