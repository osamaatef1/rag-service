#!/bin/bash

# RAG Microservice Setup Script
# This script sets up the Python environment and installs dependencies

set -e  # Exit on error

echo "=================================="
echo "RAG Microservice Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p storage/chromadb
mkdir -p logs
mkdir -p uploads

# Copy .env.example to .env if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running the service."
else
    echo ".env file already exists. Skipping..."
fi

echo ""
echo "=================================="
echo "Setup completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - Set API_KEY for authentication"
echo "   - Configure your LLM provider (OpenAI, Anthropic, or Ollama)"
echo "   - Set ALLOWED_ORIGINS for CORS"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the service:"
echo "   ./run.sh"
echo ""
echo "4. Or run in development mode:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
