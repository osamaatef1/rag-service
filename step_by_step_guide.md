# Step-by-Step Guide: Using the RAG Service

## Prerequisites
1. Make sure your service is running: `./run.sh` or `python -m uvicorn app.main:app --reload`
2. The service will run on: `http://localhost:8000`
3. Your vector database will be stored in: `./storage/chromadb`

---

## STEP 1: Add Text to Vector Database

### Option A: Add Plain Text
```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -F 'content=Python is a high-level programming language. It is widely used for web development, data science, and automation.' \
  -F 'metadata={"title": "Python Introduction", "category": "programming"}'
```

### Option B: Upload a File
```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -F "file=@/path/to/your/document.pdf" \
  -F 'metadata={"title": "My Document", "author": "John"}'
```

### Option C: Add from URL
```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -F 'url=https://example.com/article' \
  -F 'metadata={"source": "web"}'
```

**Response Example:**
```json
{
  "document_id": "abc-123-def-456",
  "chunks_created": 5,
  "metadata": {
    "document_id": "abc-123-def-456",
    "collection": "documents",
    "created_at": "2024-01-05T12:00:00",
    "chunk_count": 5
  }
}
```

---

## STEP 2: Query the Vector Database

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python used for?",
    "top_k": 3
  }'
```

**Response Example:**
```json
{
  "success": true,
  "query": "What is Python used for?",
  "answer": "Python is widely used for web development, data science, and automation...",
  "sources": [
    {
      "document_id": "abc-123-def-456",
      "content": "Python is a high-level programming language...",
      "relevance_score": 0.92
    }
  ],
  "processing_time_ms": 245.3
}
```

---

## STEP 3: List All Documents

```bash
curl -X GET "http://localhost:8000/api/v1/documents?limit=10&offset=0" \
  -H "X-API-Key: your-api-key-here"
```

---

## STEP 4: Delete a Document

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/abc-123-def-456" \
  -H "X-API-Key: your-api-key-here"
```

---

## What Happens Behind the Scenes?

1. **Add Document** → Text is split into chunks → Each chunk converted to 384-dimensional vector → Stored in ChromaDB with metadata
2. **Query** → Your question converted to vector → Searches for similar vectors → Returns matching text chunks → LLM generates answer
3. **Storage** → All data saved in `./storage/chromadb` directory

---

## Check Service Health

```bash
curl http://localhost:8000/health
```

## View API Documentation

Open in browser: `http://localhost:8000/docs`
