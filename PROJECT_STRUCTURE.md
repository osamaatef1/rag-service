# RAG Service Project Structure

Complete overview of the RAG microservice architecture and files.

## Directory Tree

```
rag-service/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   └── rate_limit.py        # Rate limiting dependency
│   │   │
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── documents.py         # Document management endpoints
│   │       ├── query.py             # RAG query endpoints
│   │       └── health.py            # Health check endpoint
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management (env vars)
│   │   ├── security.py              # API key authentication
│   │   └── logging.py               # Logging configuration
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py           # Main RAG orchestration
│   │   ├── llm_service.py           # LLM provider abstraction
│   │   ├── vector_store.py          # ChromaDB vector operations
│   │   └── document_service.py      # Document lifecycle management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic request/response models
│   │
│   └── utils/
│       ├── __init__.py
│       ├── cache.py                 # In-memory query cache
│       └── document_processor.py    # Text extraction & chunking
│
├── storage/
│   └── chromadb/                    # Vector database persistence
│       └── .gitkeep
│
├── logs/                            # Application logs
│   └── .gitkeep
│
├── .env                             # Environment configuration (active)
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── requirements.txt                 # Python dependencies
├── setup.sh                         # Setup script (executable)
├── run.sh                           # Run script (executable)
├── README.md                        # Complete documentation
├── QUICKSTART.md                    # Quick setup guide
├── PROJECT_STRUCTURE.md             # This file
└── rag-service.service.example      # systemd service template
```

## Key Components

### Core Application (`app/main.py`)
- FastAPI application initialization
- Middleware configuration (CORS, GZip, timing)
- Global exception handlers
- Route registration
- Startup/shutdown events

### API Layer (`app/api/`)
- **routes/documents.py**: Document ingestion, listing, deletion
- **routes/query.py**: RAG query processing
- **routes/health.py**: Service health checks
- **dependencies/rate_limit.py**: Rate limiting logic

### Business Logic (`app/services/`)
- **rag_service.py**: Orchestrates retrieval + generation
- **llm_service.py**: Abstracts OpenAI/Anthropic/Ollama
- **vector_store.py**: ChromaDB operations (add, search, delete)
- **document_service.py**: Document ingestion pipeline

### Data Models (`app/models/`)
- **schemas.py**: All Pydantic models for validation
  - Request models (DocumentIngestRequest, QueryRequest)
  - Response models (QueryResponse, HealthResponse)
  - Error handling (ErrorResponse)

### Configuration (`app/core/`)
- **config.py**: Environment variable loading with Pydantic
- **security.py**: API key verification dependency
- **logging.py**: Structured logging setup

### Utilities (`app/utils/`)
- **cache.py**: Simple TTL-based cache for queries
- **document_processor.py**: Text extraction (PDF, DOCX, TXT, URL)

## Data Flow

### Document Ingestion
```
Client Request
    ↓
API Route (documents.py)
    ↓
Document Service
    ↓
Document Processor (extract & chunk)
    ↓
Vector Store (embed & store)
    ↓
Response
```

### RAG Query
```
Client Request
    ↓
API Route (query.py)
    ↓
RAG Service
    ↓
├─→ Check Cache (if enabled)
│   └─→ Return cached result
│
└─→ Vector Store (semantic search)
    ↓
    Retrieved Context
    ↓
    LLM Service (generate answer)
    ↓
    Cache Result
    ↓
    Response
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Root information |
| GET | `/health` | Service health check |
| POST | `/api/v1/documents/ingest` | Ingest documents |
| GET | `/api/v1/documents` | List documents |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| POST | `/api/v1/query` | RAG query |

## Configuration Files

- **`.env`**: Active configuration (not in git)
- **`.env.example`**: Configuration template
- **`requirements.txt`**: Python package dependencies
- **`setup.sh`**: Automated setup script
- **`run.sh`**: Service startup script
- **`rag-service.service.example`**: systemd service template

## Security Features

1. **API Key Authentication**: All endpoints (except health) require X-API-Key header
2. **Rate Limiting**: Per-client request limiting
3. **CORS**: Configurable allowed origins
4. **Input Validation**: Pydantic schema validation
5. **Error Handling**: No sensitive info in error responses

## Storage

- **ChromaDB**: `./storage/chromadb/` - Persistent vector storage
- **Logs**: `./logs/app.log` - Application logs with rotation
- **Uploads**: File uploads are temporary (not persisted)

## Extension Points

To extend the service:

1. **Add new document types**: Extend `document_processor.py`
2. **Add new LLM providers**: Extend `llm_service.py`
3. **Add new vector DBs**: Create new store in `services/`
4. **Add custom metadata**: Modify schemas in `models/schemas.py`
5. **Add authentication methods**: Extend `core/security.py`
6. **Add new endpoints**: Create routes in `api/routes/`

## Dependencies

### Core
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### RAG Stack
- **LangChain**: RAG framework
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embeddings

### LLM Providers
- **OpenAI**: GPT models
- **Anthropic**: Claude models
- **Ollama**: Local models

### Document Processing
- **PyPDF**: PDF extraction
- **python-docx**: Word document processing
- **unstructured**: General document parsing

## Performance Considerations

- **Workers**: Multiple uvicorn workers for concurrency
- **Caching**: Query result caching (configurable TTL)
- **Chunking**: Optimized chunk size and overlap
- **Embeddings**: Local sentence-transformers (no API calls)
- **Vector Search**: Cosine similarity with configurable threshold

## Monitoring

- **Health Endpoint**: `/health` provides status and metrics
- **Logs**: Structured logging with rotation
- **Process Time**: X-Process-Time header on all responses
- **Error Tracking**: All exceptions logged with traceback

## Deployment Options

1. **Development**: Direct uvicorn with reload
2. **Production**: Multiple workers with systemd/supervisor
3. **Containerized**: Docker (Dockerfile not included but structure supports it)
4. **Reverse Proxy**: Behind nginx for HTTPS and load balancing
