# RAG Microservice

A production-ready RAG (Retrieval-Augmented Generation) microservice built with FastAPI, LangChain, and ChromaDB. This service provides RESTful APIs for document ingestion, semantic search, and AI-powered question answering.

## Features

- **Multi-Source Document Ingestion**: Upload files (PDF, TXT, MD, DOC, DOCX), raw text, or URLs
- **Vector Database**: ChromaDB for local persistent storage with easy deployment
- **Semantic Search**: Fast similarity search using sentence transformers
- **Multiple LLM Providers**: Support for OpenAI, Anthropic Claude, and local Ollama models
- **API Authentication**: Secure API key-based authentication
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **CORS Support**: Configurable cross-origin resource sharing
- **Query Caching**: In-memory cache for frequent queries
- **Collection Management**: Multi-tenant support with document collections/namespaces
- **Comprehensive API Documentation**: Auto-generated OpenAPI/Swagger docs

## Architecture

```
rag-service/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoint definitions
│   │   └── dependencies/    # Shared dependencies (auth, rate limiting)
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── security.py      # Authentication
│   │   └── logging.py       # Logging setup
│   ├── services/
│   │   ├── rag_service.py        # Main RAG orchestration
│   │   ├── llm_service.py        # LLM provider abstraction
│   │   ├── vector_store.py       # Vector database operations
│   │   └── document_service.py   # Document management
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── utils/
│   │   ├── cache.py              # Query caching
│   │   └── document_processor.py # Document processing
│   └── main.py              # FastAPI application
├── storage/
│   └── chromadb/           # Vector database storage
├── logs/                   # Application logs
├── .env.example            # Environment configuration template
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── run.sh                 # Run script
└── README.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment support

### Quick Setup

1. **Clone or navigate to the service directory**:
   ```bash
   cd rag-service
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This will:
   - Create a Python virtual environment
   - Install all dependencies
   - Create necessary directories
   - Copy `.env.example` to `.env`

3. **Configure environment variables**:
   ```bash
   nano .env
   ```

   Essential configurations:
   ```env
   # API Security - REQUIRED
   API_KEY=your-secret-api-key-here

   # LLM Provider - Choose one
   LLM_PROVIDER=openai  # or anthropic, ollama

   # For OpenAI
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4-turbo-preview

   # For Anthropic (if using)
   # ANTHROPIC_API_KEY=sk-ant-...
   # ANTHROPIC_MODEL=claude-3-sonnet-20240229

   # CORS Configuration
   ALLOWED_ORIGINS=http://localhost,https://yourdomain.com
   ```

4. **Start the service**:
   ```bash
   ./run.sh
   ```

   Or manually:
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

5. **Verify the service is running**:
   ```bash
   curl http://localhost:8000/health
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | API authentication key | - | Yes |
| `LLM_PROVIDER` | LLM provider (openai, anthropic, ollama) | openai | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | If using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | If using Anthropic |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `WORKERS` | Number of workers | 4 | No |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | http://localhost | No |
| `CHUNK_SIZE` | Document chunk size | 1000 | No |
| `CHUNK_OVERLAP` | Chunk overlap size | 200 | No |
| `TOP_K_RESULTS` | Default number of results | 5 | No |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per minute | 60 | No |

### LLM Provider Configuration

#### OpenAI (Recommended)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Anthropic Claude
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### Local Ollama
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication

All API endpoints (except `/health`) require API key authentication via header:
```
X-API-Key: your-api-key-here
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "vector_db_status": "connected",
  "total_documents": 150,
  "total_chunks": 2340
}
```

#### 2. Ingest Document
```http
POST /api/v1/documents/ingest
```

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: multipart/form-data
```

**Body (Form Data):**
- `file`: File upload (PDF, TXT, MD, DOC, DOCX)
- `content`: Raw text content (alternative to file)
- `url`: URL to fetch content from (alternative to file)
- `metadata`: JSON string with custom metadata
- `collection`: Collection name (optional)

**Example - File Upload:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@document.pdf" \
  -F "metadata={\"category\": \"support\", \"author\": \"John\"}" \
  -F "collection=knowledge_base"
```

**Example - Text Content:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "X-API-Key: your-api-key-here" \
  -F "content=This is my document content..." \
  -F "metadata={\"source\": \"manual_entry\"}"
```

**Example - URL:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "X-API-Key: your-api-key-here" \
  -F "url=https://example.com/article" \
  -F "metadata={\"source\": \"web\"}"
```

**Response:**
```json
{
  "success": true,
  "document_id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv",
  "message": "Document ingested successfully",
  "chunks_created": 15,
  "metadata": {
    "document_id": "a1b2c3d4...",
    "filename": "document.pdf",
    "collection": "knowledge_base",
    "created_at": "2024-01-15T10:30:00Z",
    "chunk_count": 15,
    "metadata": {
      "category": "support",
      "author": "John"
    }
  }
}
```

#### 3. Query (RAG)
```http
POST /api/v1/query
```

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Body:**
```json
{
  "query": "What is the refund policy?",
  "collection": "knowledge_base",
  "top_k": 5,
  "metadata_filter": {
    "category": "policies"
  },
  "include_sources": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the refund policy?",
    "top_k": 3,
    "include_sources": true
  }'
```

**Response:**
```json
{
  "success": true,
  "query": "What is the refund policy?",
  "answer": "According to our policy, customers can request a full refund within 30 days of purchase if they are not satisfied with the product. The refund will be processed within 5-7 business days...",
  "sources": [
    {
      "document_id": "doc_123",
      "content": "Refund policy: Full refund within 30 days...",
      "metadata": {
        "filename": "policy.pdf",
        "category": "policies"
      },
      "relevance_score": 0.95
    }
  ],
  "processing_time_ms": 1234.56,
  "metadata": {
    "documents_retrieved": 3,
    "model": "openai",
    "cached": false
  }
}
```

#### 4. List Documents
```http
GET /api/v1/documents?collection=knowledge_base&limit=50&offset=0
```

**Headers:**
```
X-API-Key: your-api-key-here
```

**Query Parameters:**
- `collection`: Filter by collection (optional)
- `limit`: Max results (1-1000, default: 100)
- `offset`: Skip results (default: 0)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/documents?limit=10" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "success": true,
  "total": 150,
  "documents": [
    {
      "document_id": "doc_123",
      "filename": "policy.pdf",
      "collection": "documents",
      "created_at": "2024-01-15T10:30:00Z",
      "chunk_count": 15,
      "metadata": {}
    }
  ],
  "limit": 10,
  "offset": 0
}
```

#### 5. Delete Document
```http
DELETE /api/v1/documents/{document_id}?collection=knowledge_base
```

**Headers:**
```
X-API-Key: your-api-key-here
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/doc_123" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc_123",
  "message": "Document deleted successfully",
  "chunks_deleted": 15
}
```

## Laravel Integration

### Installation in Laravel

Add to your Laravel project's HTTP client configuration:

**Create a service class** `app/Services/RagService.php`:

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Client\Response;

class RagService
{
    protected string $baseUrl;
    protected string $apiKey;

    public function __construct()
    {
        $this->baseUrl = config('services.rag.base_url');
        $this->apiKey = config('services.rag.api_key');
    }

    protected function client()
    {
        return Http::withHeaders([
            'X-API-Key' => $this->apiKey,
        ])->baseUrl($this->baseUrl);
    }

    /**
     * Ingest a document from text content
     */
    public function ingestText(string $content, array $metadata = [], ?string $collection = null): array
    {
        $response = $this->client()->asMultipart()->post('/api/v1/documents/ingest', [
            [
                'name' => 'content',
                'contents' => $content
            ],
            [
                'name' => 'metadata',
                'contents' => json_encode($metadata)
            ],
            [
                'name' => 'collection',
                'contents' => $collection ?? 'documents'
            ]
        ]);

        return $response->throw()->json();
    }

    /**
     * Ingest a document from file
     */
    public function ingestFile(string $filePath, array $metadata = [], ?string $collection = null): array
    {
        $response = $this->client()->attach(
            'file',
            file_get_contents($filePath),
            basename($filePath)
        )->post('/api/v1/documents/ingest', [
            'metadata' => json_encode($metadata),
            'collection' => $collection ?? 'documents'
        ]);

        return $response->throw()->json();
    }

    /**
     * Ingest a document from URL
     */
    public function ingestUrl(string $url, array $metadata = [], ?string $collection = null): array
    {
        $response = $this->client()->asMultipart()->post('/api/v1/documents/ingest', [
            [
                'name' => 'url',
                'contents' => $url
            ],
            [
                'name' => 'metadata',
                'contents' => json_encode($metadata)
            ],
            [
                'name' => 'collection',
                'contents' => $collection ?? 'documents'
            ]
        ]);

        return $response->throw()->json();
    }

    /**
     * Query the RAG system
     */
    public function query(
        string $query,
        ?string $collection = null,
        ?int $topK = null,
        ?array $metadataFilter = null,
        bool $includeSources = true
    ): array {
        $response = $this->client()->post('/api/v1/query', array_filter([
            'query' => $query,
            'collection' => $collection,
            'top_k' => $topK,
            'metadata_filter' => $metadataFilter,
            'include_sources' => $includeSources
        ]));

        return $response->throw()->json();
    }

    /**
     * List all documents
     */
    public function listDocuments(?string $collection = null, int $limit = 100, int $offset = 0): array
    {
        $response = $this->client()->get('/api/v1/documents', array_filter([
            'collection' => $collection,
            'limit' => $limit,
            'offset' => $offset
        ]));

        return $response->throw()->json();
    }

    /**
     * Delete a document
     */
    public function deleteDocument(string $documentId, ?string $collection = null): array
    {
        $response = $this->client()->delete("/api/v1/documents/{$documentId}", array_filter([
            'collection' => $collection
        ]));

        return $response->throw()->json();
    }

    /**
     * Health check
     */
    public function health(): array
    {
        $response = Http::get($this->baseUrl . '/health');
        return $response->throw()->json();
    }
}
```

**Add to `config/services.php`**:

```php
'rag' => [
    'base_url' => env('RAG_SERVICE_URL', 'http://localhost:8000'),
    'api_key' => env('RAG_SERVICE_API_KEY'),
],
```

**Add to `.env`**:

```env
RAG_SERVICE_URL=http://localhost:8000
RAG_SERVICE_API_KEY=your-api-key-here
```

### Usage Examples in Laravel

```php
use App\Services\RagService;

// Inject the service
public function __construct(protected RagService $rag)
{
}

// Ingest text
$result = $this->rag->ingestText(
    content: "Your document content here...",
    metadata: ['category' => 'support', 'author' => 'John'],
    collection: 'knowledge_base'
);

// Query
$result = $this->rag->query(
    query: "What is the refund policy?",
    collection: 'knowledge_base',
    topK: 5
);

echo $result['answer'];

// List documents
$documents = $this->rag->listDocuments(collection: 'knowledge_base');

// Delete document
$this->rag->deleteDocument($documentId);
```

## Deployment

### systemd Service

Create `/etc/systemd/system/rag-service.service`:

```ini
[Unit]
Description=RAG Microservice
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/rag-service
Environment="PATH=/path/to/rag-service/venv/bin"
ExecStart=/path/to/rag-service/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rag-service
sudo systemctl start rag-service
sudo systemctl status rag-service
```

### Supervisor Configuration

Create `/etc/supervisor/conf.d/rag-service.conf`:

```ini
[program:rag-service]
directory=/path/to/rag-service
command=/path/to/rag-service/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/path/to/rag-service/logs/supervisor.log
```

Reload supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start rag-service
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name rag.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
   ```bash
   source venv/bin/activate
   ```

2. **ChromaDB permission errors**: Check storage directory permissions
   ```bash
   chmod -R 755 storage/chromadb
   ```

3. **LLM API errors**: Verify API keys in `.env` file

4. **Port already in use**: Change PORT in `.env` or kill the process
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

### Logs

Application logs are stored in `logs/app.log`. Monitor in real-time:
```bash
tail -f logs/app.log
```

## Performance Tuning

- **Workers**: Increase `WORKERS` in `.env` for more concurrent requests
- **Chunk Size**: Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for better retrieval
- **Top K**: Lower `TOP_K_RESULTS` for faster queries
- **Cache**: Enable `ENABLE_QUERY_CACHE` for frequent queries

## Security Considerations

- Always use strong API keys
- Use HTTPS in production
- Configure CORS properly
- Implement rate limiting at nginx/load balancer level for additional protection
- Regularly update dependencies

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
# rag-service
