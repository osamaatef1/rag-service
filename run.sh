#!/bin/bash

# RAG Microservice Run Script
# This script starts the FastAPI service

set -e  # Exit on error

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using default values."
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Set default values if not in .env
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}

echo "=================================="
echo "Starting RAG Microservice"
echo "=================================="
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Environment: ${APP_ENV:-production}"
echo "=================================="
echo ""

# Start the service with uvicorn
if [ "${APP_ENV}" = "development" ]; then
    echo "Running in DEVELOPMENT mode with auto-reload..."
    uvicorn app.main:app --host $HOST --port $PORT --reload --log-level info
else
    echo "Running in PRODUCTION mode..."
    uvicorn app.main:app --host $HOST --port $PORT --workers $WORKERS --log-level info
fi
