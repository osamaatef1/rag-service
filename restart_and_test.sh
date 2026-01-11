#!/bin/bash
# Quick script to restart server and upload Arabic JSON data

echo "=================================================="
echo "🔄 RAG Service - Restart & Test Script"
echo "=================================================="

# Check if server is running
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️  Server is already running"
    echo "   Please stop it first (Ctrl+C in server terminal)"
    echo "   Then run this script again"
    exit 1
fi

echo ""
echo "📦 Step 1: Starting server with new multilingual model..."
echo "   Model: paraphrase-multilingual-MiniLM-L12-v2"
echo "   (First time will download model - may take 2-3 minutes)"
echo ""

# Activate virtual environment and start server in background
source venv/bin/activate

# Start server
echo "Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/rag_server.log 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo "Waiting for server to be ready..."

# Wait for server to start
sleep 5

# Check if server is responding
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Server is ready!"
        break
    fi
    echo "   Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Server failed to start. Check logs:"
    tail -20 /tmp/rag_server.log
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=================================================="
echo "📤 Step 2: Uploading Arabic JSON data..."
echo "=================================================="

curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -F "file=@sample_data.json" \
  -F 'metadata={"title": "الإدارة البيئية والحياة الفطرية", "language": "ar", "category": "environment"}' \
  2>/dev/null | python3 -m json.tool

echo ""
echo "=================================================="
echo "🔍 Step 3: Testing Arabic Query..."
echo "=================================================="

sleep 2

curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "ما هي الثدييات البرية في المملكة؟", "top_k": 3}' \
  2>/dev/null | python3 -m json.tool

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Server is running at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Server PID: $SERVER_PID"
echo ""
echo "To stop server: kill $SERVER_PID"
echo "To view logs: tail -f /tmp/rag_server.log"
echo ""
