#!/bin/bash

# Lexen Legal AI Setup Script
echo "🚀 Setting up Lexen Legal AI Assistant..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama first:"
    echo "   macOS: brew install ollama"
    echo "   Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   Windows: winget install Ollama.Ollama"
    exit 1
fi

echo "✅ Ollama found"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "🔄 Starting Ollama server..."
    ollama serve &
    sleep 5
fi

echo "✅ Ollama server is running"

# Pull the Llama3 model if not already available
echo "📥 Checking for Llama3 model..."
if ! ollama list | grep -q "llama3"; then
    echo "📥 Pulling Llama3 model (this may take a few minutes)..."
    ollama pull llama3
else
    echo "✅ Llama3 model already available"
fi

# Create output directory
mkdir -p output

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v poetry &> /dev/null; then
    echo "Using Poetry..."
    poetry install
else
    echo "Using pip..."
    pip install -r requirements.txt
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the legal AI assistant:"
echo "   python main.py"
echo ""
echo "🔧 To test the connection:"
echo "   curl http://localhost:11434/api/tags"
