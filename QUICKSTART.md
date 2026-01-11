# Quick Start Guide

## 5-Minute Setup

### 1. Install and Configure

```bash
cd rag-service
./setup.sh
```

### 2. Edit Configuration

```bash
nano .env
```

Set these required values:
```env
API_KEY=my-secret-key-123
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Start the Service

```bash
./run.sh
```

The service will be available at: http://localhost:8000

### 4. Test the Service

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## First API Calls

### Ingest a Document

```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "X-API-Key: my-secret-key-123" \
  -F "content=Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming."
```

### Query the Document

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "X-API-Key: my-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "include_sources": true}'
```

## Laravel Integration Quick Setup

1. Copy the RagService class to `app/Services/RagService.php` (see README.md)

2. Add to `.env`:
```env
RAG_SERVICE_URL=http://localhost:8000
RAG_SERVICE_API_KEY=my-secret-key-123
```

3. Add to `config/services.php`:
```php
'rag' => [
    'base_url' => env('RAG_SERVICE_URL', 'http://localhost:8000'),
    'api_key' => env('RAG_SERVICE_API_KEY'),
],
```

4. Use in your controller:
```php
use App\Services\RagService;

$rag = app(RagService::class);
$result = $rag->query("What is Python?");
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the interactive API docs at http://localhost:8000/docs
- Configure production deployment (systemd/supervisor)
- Set up nginx reverse proxy for HTTPS
