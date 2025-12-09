#!/bin/bash
# Docker start script for LegisAI Backend

set -e

echo "🐳 Starting LegisAI Backend with Docker Compose..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update with your API keys."
    else
        echo "⚠️  .env.example not found. Creating basic .env..."
        echo "OLLAMA_HOST=http://ollama:11434" > .env
        echo "PORT=8000" >> .env
    fi
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/vector_store uploads legal_data

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up --build -d

echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check if Ollama is running and pull model if needed
echo "🤖 Checking Ollama..."
if docker exec legisai-ollama ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Ollama model already installed"
else
    echo "📥 Pulling Ollama model (llama3.1:8b)..."
    docker exec legisai-ollama ollama pull llama3.1:8b
fi

# Check backend health
echo "🏥 Checking backend health..."
sleep 5
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
else
    echo "⚠️  Backend may still be starting. Check logs with: docker-compose logs -f backend"
fi

echo ""
echo "✅ LegisAI Backend is starting!"
echo ""
echo "📊 View logs:    docker-compose logs -f"
echo "🛑 Stop:         docker-compose down"
echo "🔍 Status:       docker-compose ps"
echo "🌐 API:          http://localhost:8000"
echo "📚 Docs:         http://localhost:8000/docs"

