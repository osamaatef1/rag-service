# RAG System Explained for Laravel Developers

> A comprehensive guide to understanding this Python RAG (Retrieval-Augmented Generation) service from a Laravel backend perspective.

---

## Table of Contents

1. [What is RAG?](#what-is-rag)
2. [Architecture Comparison: Laravel vs FastAPI](#architecture-comparison)
3. [Key Concepts Explained](#key-concepts-explained)
4. [Complete Flow Diagrams](#complete-flow-diagrams)
5. [File-by-File Breakdown](#file-by-file-breakdown)
6. [Code Examples with Laravel Equivalents](#code-examples-with-laravel-equivalents)
7. [Database Comparison](#database-comparison)
8. [Testing the System](#testing-the-system)

---

## What is RAG?

**RAG = Retrieval-Augmented Generation**

Think of it like this:
- **Regular ChatGPT**: Only knows what it was trained on (data up to 2023)
- **RAG System**: ChatGPT + Your own custom documents

### Real-World Analogy

```
Without RAG:
Student → Asks question → Answers from memory only

With RAG:
Student → Asks question → Searches textbook → Answers with textbook references
```

### Laravel Analogy

```php
// Without RAG (Like asking ChatGPT directly)
$answer = ChatGPT::ask("What is our company policy?");
// ChatGPT guesses or says "I don't know"

// With RAG (ChatGPT + Your documents)
$relevantDocs = VectorDB::search("company policy");  // Search your docs
$answer = ChatGPT::askWithContext($question, $relevantDocs);  // Smart answer
```

---

## Architecture Comparison

### Laravel MVC Structure

```
Laravel Project
├── routes/
│   ├── api.php                     → API route definitions
│   └── web.php                     → Web routes
├── app/
│   ├── Http/
│   │   ├── Controllers/            → Handle requests
│   │   ├── Middleware/             → Request filters
│   │   └── Requests/               → Validation rules
│   ├── Services/                   → Business logic
│   └── Models/                     → Eloquent models (DB)
├── config/                         → Configuration
└── database/
    └── migrations/                 → Database schema
```

### Python FastAPI RAG Structure

```
RAG Project
├── app/
│   ├── api/
│   │   ├── routes/                 → API endpoints (like Laravel routes + controllers)
│   │   │   ├── documents.py        → DocumentController
│   │   │   └── query.py            → QueryController
│   │   └── dependencies/           → Middleware (like Laravel middleware)
│   │       └── rate_limit.py       → Rate limiting (disabled for simplicity)
│   ├── services/                   → Business logic (same as Laravel!)
│   │   ├── vector_store.py         → THE CORE: Embeddings + ChromaDB
│   │   ├── document_service.py     → Handle document ingestion
│   │   ├── rag_service.py          → Orchestrate search + AI
│   │   └── llm_service.py          → Talk to OpenAI/Claude/Ollama
│   ├── utils/                      → Helper functions
│   │   └── document_processor.py   → Text chunking
│   ├── models/
│   │   └── schemas.py              → Validation (like Form Requests)
│   └── core/
│       ├── config.py               → Settings (like config/)
│       └── logging.py              → Logger
├── storage/
│   └── chromadb/                   → Vector Database (like database/)
├── .env                            → Environment config
└── main.py                         → App entry point
```

---

## Key Concepts Explained

### 1. What is "Ingesting"?

**Ingesting = Adding/Importing data into the system**

#### Laravel Comparison

```php
// Laravel - Seeding database
php artisan db:seed

DB::table('products')->insert([
    'name' => 'Laptop',
    'description' => 'A powerful laptop...'
]);
```

```python
# RAG - Ingesting documents
POST /api/v1/documents/ingest

{
    "content": "Python is a programming language created by Guido van Rossum in 1991."
}
```

**What happens during ingestion:**
1. Take your text/document
2. Split into smaller chunks (1000 characters each)
3. Convert each chunk to **embeddings** (numbers)
4. Save to **ChromaDB** (vector database)

---

### 2. What are Embeddings?

**Embeddings = Converting text into numbers that represent meaning**

#### Laravel Comparison

```php
// Laravel - Hashing passwords
$password = "mypassword123";
$hash = Hash::make($password);
// Result: "$2y$10$92IXUNpkjO0rOQ5byMi.Oe/..."

// Purpose: Security, one-way encryption, can't reverse
```

```python
# RAG - Embedding text
text = "Python is a great programming language"
embedding = embed(text)
# Result: [0.0234, -0.1234, 0.5678, 0.9012, ..., 0.4567]  (384 numbers)

# Purpose: Capture meaning, can compare similarity
```

#### Why 384 numbers?

The AI model `sentence-transformers/all-MiniLM-L6-v2` outputs 384 dimensions.

Think of it like GPS coordinates:
- **GPS**: 2 numbers (latitude, longitude) represent a location
- **Embeddings**: 384 numbers represent text meaning

#### Example: Similar Texts Have Similar Numbers

```python
# Text 1
"Python is great" → [0.5, 0.3, 0.8, ...]

# Text 2 (Similar meaning)
"Python is awesome" → [0.52, 0.31, 0.82, ...]  # Very close numbers!

# Text 3 (Different meaning)
"I love pizza" → [-0.2, 0.9, -0.4, ...]  # Different numbers!
```

---

### 3. What is ChromaDB?

**ChromaDB = A specialized database for storing embeddings (vectors)**

#### Database Comparison

```php
// Laravel - MySQL/PostgreSQL
// Stores: Structured data (rows, columns)

users table:
| id | name  | email           |
|----|-------|-----------------|
| 1  | John  | john@email.com  |
| 2  | Sarah | sarah@email.com |

// Search: Exact matches or LIKE queries
SELECT * FROM users WHERE name LIKE '%John%';
```

```python
# RAG - ChromaDB (Vector Database)
# Stores: Text + Embeddings (vectors of numbers)

documents collection:
| id  | text                      | embedding                    |
|-----|---------------------------|------------------------------|
| 1   | "Python is great..."      | [0.5, 0.3, 0.8, ...]        |
| 2   | "Laravel is awesome..."   | [0.6, -0.2, 0.4, ...]       |

# Search: Similarity search (find similar meanings)
search("programming language")  # Returns both Python & Laravel docs!
```

---

### 4. How Does Similarity Search Work?

**Similarity Search = Find text with similar meaning (not exact words)**

#### Concept: Cosine Similarity

Imagine vectors as arrows pointing in space:
- Similar meaning = Arrows point in same direction
- Different meaning = Arrows point in different directions

```
Query: "Who created Python?"
Embedding: [0.5, 0.5, 0.1, ...]  (Arrow pointing Northeast)

Document 1: "Python was created by Guido van Rossum"
Embedding: [0.52, 0.48, 0.12, ...]  (Arrow pointing Northeast) → SIMILAR! ✓

Document 2: "I love eating pizza"
Embedding: [-0.3, 0.9, -0.5, ...]  (Arrow pointing Northwest) → DIFFERENT ✗
```

#### Laravel Analogy

```php
// MySQL - Exact search
SELECT * FROM documents
WHERE content LIKE '%Python creator%';
// Only finds if exact words "Python creator" exist

// ChromaDB - Semantic search
search("Who created Python?")
// Finds: "Guido van Rossum invented Python"
// Finds: "Python's founder is Guido"
// Finds: "Guido made Python in 1991"
// Even though words are different, meaning is similar!
```

---

## Complete Flow Diagrams

### Flow 1: Document Ingestion (Adding Documents)

```
┌─────────────────────────────────────────────────────────────────┐
│ User sends document                                             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ POST /api/v1/documents/ingest                                   │
│ File: app/api/routes/documents.py:35                            │
│                                                                  │
│ Laravel equivalent:                                              │
│ Route::post('/api/v1/documents/ingest',                        │
│     [DocumentController::class, 'ingest'])                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Document Service - Process Request                              │
│ File: app/services/document_service.py:46                       │
│                                                                  │
│ Laravel equivalent:                                              │
│ $documentService->ingestText($content, $metadata);              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Document Processor - Split into Chunks                          │
│ File: app/utils/document_processor.py:108                       │
│                                                                  │
│ Input:  "Python is a programming language created by Guido..." │
│ Output: ["Python is a programming...", "language created..."]  │
│                                                                  │
│ Chunks: 1000 characters each, 200 character overlap             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ ⭐ MAGIC STEP: Convert to Embeddings                            │
│ File: app/services/vector_store.py:77                           │
│                                                                  │
│ embeddings = self.embeddings.embed_documents(chunks)             │
│                                                                  │
│ Input:  ["Python is great", "Guido created Python"]            │
│ Output: [[0.02, -0.12, 0.56, ...],  # 384 numbers              │
│          [0.15, -0.08, 0.72, ...]]  # 384 numbers              │
│                                                                  │
│ Uses: sentence-transformers/all-MiniLM-L6-v2 AI model           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Save to ChromaDB                                                │
│ File: app/services/vector_store.py:92                           │
│                                                                  │
│ collection.add(                                                  │
│     embeddings=[[0.02, -0.12, ...]],  # The numbers            │
│     documents=["Python is great"],     # Original text         │
│     metadatas=[{...}],                 # Metadata               │
│     ids=["doc-123-chunk-1"]            # Unique ID              │
│ )                                                                │
│                                                                  │
│ Laravel equivalent:                                              │
│ DB::table('embeddings')->insert([...]);                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ ✅ Success! Document is now searchable                          │
│                                                                  │
│ Return: {                                                        │
│   "document_id": "doc-uuid-123",                                │
│   "chunks_created": 5                                            │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

### Flow 2: Query (Asking Questions)

```
┌─────────────────────────────────────────────────────────────────┐
│ User asks question                                              │
│ "Who created Python?"                                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ POST /api/v1/query                                              │
│ File: app/api/routes/query.py:24                                │
│                                                                  │
│ Laravel equivalent:                                              │
│ Route::post('/api/v1/query', [QueryController::class, 'ask']); │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ RAG Service - Orchestrate Search + Generation                   │
│ File: app/services/rag_service.py:23                            │
│                                                                  │
│ This service coordinates two steps:                              │
│ 1. Search vector database for relevant docs                     │
│ 2. Send docs + question to AI for answer                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Vector Store - Search Similar Documents                 │
│ File: app/services/rag_service.py:59                            │
│                                                                  │
│ context_documents = vector_store.search(                         │
│     query="Who created Python?",                                 │
│     top_k=5                                                      │
│ )                                                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ ⭐ MAGIC: Convert Question to Embedding                         │
│ File: app/services/vector_store.py:159                          │
│                                                                  │
│ query_embedding = self.embeddings.embed_query(query)             │
│                                                                  │
│ Input:  "Who created Python?"                                   │
│ Output: [0.12, -0.56, 0.90, 0.23, ...]  # 384 numbers           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ ⭐ MAGIC: Search ChromaDB for Similar Vectors                   │
│ File: app/services/vector_store.py:162                          │
│                                                                  │
│ results = collection.query(                                      │
│     query_embeddings=[[0.12, -0.56, 0.90, ...]],                │
│     n_results=5                                                  │
│ )                                                                │
│                                                                  │
│ How it works:                                                    │
│ 1. Compare query vector with all document vectors               │
│ 2. Calculate cosine similarity (0.0 to 1.0)                     │
│ 3. Return top 5 most similar documents                          │
│                                                                  │
│ Results:                                                         │
│ - "Python was created by Guido van Rossum" (score: 0.95)       │
│ - "Guido invented Python in 1991" (score: 0.89)                │
│ - "Python is a programming language" (score: 0.72)             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: LLM Service - Generate Answer with AI                   │
│ File: app/services/rag_service.py:83                            │
│                                                                  │
│ answer = llm_service.generate_response(                          │
│     query="Who created Python?",                                 │
│     context_documents=[found documents]                          │
│ )                                                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Build Prompt for GPT-4                                          │
│ File: app/services/llm_service.py:80                            │
│                                                                  │
│ Prompt:                                                          │
│ """                                                              │
│ Context information:                                             │
│ [1] Python was created by Guido van Rossum                      │
│ [2] Guido invented Python in 1991                               │
│ [3] Python is a programming language                            │
│                                                                  │
│ Question: Who created Python?                                   │
│                                                                  │
│ Answer based on the context provided above:                     │
│ """                                                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Send to OpenAI GPT-4                                            │
│ File: app/services/llm_service.py:93                            │
│                                                                  │
│ response = self.llm.invoke(messages)                             │
│                                                                  │
│ GPT-4 reads the context and generates:                          │
│ "Based on the provided context, Python was created by Guido     │
│  van Rossum in 1991."                                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ ✅ Return Complete Answer                                       │
│                                                                  │
│ {                                                                │
│   "success": true,                                               │
│   "query": "Who created Python?",                                │
│   "answer": "Python was created by Guido van Rossum in 1991.",  │
│   "sources": [                                                   │
│     {                                                            │
│       "content": "Python was created by Guido van Rossum",      │
│       "relevance_score": 0.95                                    │
│     }                                                            │
│   ],                                                             │
│   "processing_time_ms": 1250                                     │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## File-by-File Breakdown

### 1. Routes (Entry Points)

#### `app/api/routes/documents.py` - Document Management

**Purpose:** Handle document ingestion (like Laravel Controller)

**Laravel Equivalent:**
```php
// routes/api.php
Route::post('/api/v1/documents/ingest', [DocumentController::class, 'ingest']);
Route::get('/api/v1/documents', [DocumentController::class, 'list']);
Route::delete('/api/v1/documents/{id}', [DocumentController::class, 'delete']);
```

**Key Functions:**

| Function | Line | Description | Laravel Equivalent |
|----------|------|-------------|-------------------|
| `ingest_document()` | 35 | Add text/file/URL to database | `DocumentController@store` |
| `list_documents()` | 123 | List all ingested documents | `DocumentController@index` |
| `delete_document()` | 167 | Delete a document | `DocumentController@destroy` |

**Example Usage:**
```bash
# Ingest text
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -F 'content=Python is a programming language created by Guido van Rossum.'

# List documents
curl "http://localhost:8000/api/v1/documents"

# Delete document
curl -X DELETE "http://localhost:8000/api/v1/documents/doc-uuid-123"
```

---

#### `app/api/routes/query.py` - Query/Ask Questions

**Purpose:** Handle RAG queries (search + AI generation)

**Laravel Equivalent:**
```php
// routes/api.php
Route::post('/api/v1/query', [QueryController::class, 'ask']);
```

**Key Functions:**

| Function | Line | Description | Laravel Equivalent |
|----------|------|-------------|-------------------|
| `query()` | 24 | Ask question, get AI answer | `QueryController@ask` |

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who created Python?", "top_k": 5}'
```

---

### 2. Services (Business Logic)

#### `app/services/vector_store.py` - ⭐ THE MOST IMPORTANT FILE

**Purpose:** Handle embeddings and ChromaDB operations

**This is the CORE of the RAG system!**

**Key Functions:**

| Function | Line | What It Does | Laravel Equivalent |
|----------|------|--------------|-------------------|
| `__init__()` | 29-34 | Load embedding model | Constructor loading services |
| `add_documents()` | 41-97 | **Line 77: Text → Embeddings** | `DB::table()->insert()` |
| `search()` | 139-172 | **Line 159: Query → Embeddings**<br>**Line 162: Find similar** | `DB::table()->where()->get()` |
| `list_documents()` | 174-210 | List all documents | `DB::table()->paginate()` |
| `delete_document()` | 212-243 | Delete document | `DB::table()->delete()` |

**Critical Code - Line 77 (Text to Embeddings):**
```python
# This is where text becomes numbers!
embeddings = self.embeddings.embed_documents(chunks)

# Input:  ["Python is great", "Guido created Python"]
# Output: [[0.02, -0.12, 0.56, ...],    # 384 numbers
#          [0.15, -0.08, 0.72, ...]]    # 384 numbers
```

**Critical Code - Line 159-166 (Search):**
```python
# Convert question to embedding
query_embedding = self.embeddings.embed_query(query)
# "Who created Python?" → [0.12, -0.56, 0.90, ...]

# Search ChromaDB for similar vectors
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k  # Return top 5 most similar
)
```

---

#### `app/services/document_service.py` - Document Management

**Purpose:** Orchestrate document ingestion process

**Laravel Equivalent:**
```php
class DocumentService {
    public function ingestText($content, $metadata) {
        // 1. Process text
        // 2. Add to vector store
    }
}
```

**Key Functions:**

| Function | Line | What It Does |
|----------|------|--------------|
| `ingest_text()` | 25-78 | Process text content |
| `ingest_file()` | 80-158 | Process uploaded files (PDF, TXT, DOCX) |
| `ingest_url()` | 160-217 | Fetch and process URL content |

**Flow:**
```
User Input → Document Service → Document Processor → Vector Store → ChromaDB
```

---

#### `app/services/rag_service.py` - RAG Orchestration

**Purpose:** Combine vector search + LLM generation

**Laravel Equivalent:**
```php
class RAGService {
    public function query($question) {
        // 1. Search vector database
        $docs = $this->vectorStore->search($question);

        // 2. Send to AI with context
        $answer = $this->llm->generate($question, $docs);

        return $answer;
    }
}
```

**Key Functions:**

| Function | Line | What It Does |
|----------|------|--------------|
| `query()` | 23-109 | Main RAG logic: Search → Generate |

**Flow (Line 59 & 83):**
```python
# Step 1: Search for relevant documents
context_documents = self.vector_store.search(query, top_k)

# Step 2: Generate AI answer with context
answer = self.llm_service.generate_response(query, context_documents)
```

---

#### `app/services/llm_service.py` - AI Communication

**Purpose:** Talk to OpenAI, Anthropic (Claude), or Ollama

**Laravel Equivalent:**
```php
class LLMService {
    public function generate($question, $context) {
        return OpenAI::chat([
            'model' => 'gpt-4',
            'messages' => [
                ['role' => 'system', 'content' => 'You are helpful...'],
                ['role' => 'user', 'content' => $question]
            ]
        ]);
    }
}
```

**Key Functions:**

| Function | Line | What It Does |
|----------|------|--------------|
| `_initialize_llm()` | 26-50 | Load OpenAI/Claude/Ollama based on config |
| `generate_response()` | 52-103 | Send prompt to AI, get answer |
| `_build_context()` | 105-132 | Format documents for prompt |

**Current Config (from .env):**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=YOUR_ACTUAL_OPENAI_API_KEY_HERE
OPENAI_MODEL=gpt-4-turbo-preview
```

---

### 3. Utilities

#### `app/utils/document_processor.py` - Text Processing

**Purpose:** Extract text from files and split into chunks

**Key Functions:**

| Function | Line | What It Does | Config |
|----------|------|--------------|--------|
| `extract_text_from_file()` | 32-67 | Extract from PDF, TXT, DOCX | Supports: pdf, txt, md, doc, docx |
| `chunk_text()` | 98-110 | Split text into chunks | 1000 chars, 200 overlap |
| `process_document()` | 112-131 | Main processing function | - |

**Why Chunking?**

AI models have token limits. Instead of sending entire book:
- Split into 1000-character chunks
- Each chunk gets its own embedding
- More precise search results

**Example:**
```
Original text (5000 chars):
"Python is a high-level programming language... [long text] ...created in 1991."

After chunking:
- Chunk 1 (1000 chars): "Python is a high-level programming..."
- Chunk 2 (1000 chars): "...language that is easy to learn..." (200 chars overlap)
- Chunk 3 (1000 chars): "...created by Guido van Rossum..."
- Chunk 4 (1000 chars): "...in 1991 and has become..."
- Chunk 5 (1000 chars): "...very popular worldwide."
```

---

### 4. Configuration

#### `.env` - Environment Configuration

**Laravel Equivalent:** Same! Laravel also uses `.env`

**Key Settings:**

```env
# Document Processing
CHUNK_SIZE=1000              # How large each chunk is
CHUNK_OVERLAP=200            # Overlap between chunks
ALLOWED_FILE_TYPES=pdf,txt,md,doc,docx

# RAG Settings
TOP_K_RESULTS=5              # Return top 5 similar documents
SIMILARITY_THRESHOLD=0.7     # Minimum similarity score
ENABLE_QUERY_CACHE=false     # Cache results (disabled for simplicity)

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384      # Output 384 numbers per text

# LLM Provider (OpenAI, Anthropic, or Ollama)
LLM_PROVIDER=openai
OPENAI_API_KEY=YOUR_ACTUAL_OPENAI_API_KEY_HERE
OPENAI_MODEL=gpt-4-turbo-preview
```

---

## Code Examples with Laravel Equivalents

### Example 1: Ingesting a Document

#### Python (RAG)
```python
# app/services/document_service.py:46
def ingest_text(self, content: str, metadata: dict):
    # Step 1: Split into chunks
    chunks = self.processor.process_document(content)
    # chunks = ["Python is...", "created by..."]

    # Step 2: Add to vector store (converts to embeddings internally)
    document_id, chunk_count = self.vector_store.add_documents(
        chunks=chunks,
        metadata=metadata
    )

    return {
        "document_id": document_id,
        "chunks_created": chunk_count
    }
```

#### Laravel Equivalent
```php
// app/Services/DocumentService.php
public function ingestText(string $content, array $metadata): array
{
    // Step 1: Split into chunks
    $chunks = $this->processor->processDocument($content);
    // $chunks = ["Python is...", "created by..."]

    // Step 2: Add to vector store
    [$documentId, $chunkCount] = $this->vectorStore->addDocuments(
        chunks: $chunks,
        metadata: $metadata
    );

    return [
        'document_id' => $documentId,
        'chunks_created' => $chunkCount
    ];
}
```

---

### Example 2: Converting Text to Embeddings

#### Python (RAG)
```python
# app/services/vector_store.py:77
def add_documents(self, chunks: List[str], metadata: dict):
    # This is THE MAGIC LINE!
    embeddings = self.embeddings.embed_documents(chunks)

    # Input:  ["Python is great", "Guido created Python"]
    # Output: [[0.02, -0.12, 0.56, ...],  # 384 numbers
    #          [0.15, -0.08, 0.72, ...]]  # 384 numbers

    # Save to ChromaDB
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=[metadata] * len(chunks),
        ids=[f"{doc_id}-chunk-{i}" for i in range(len(chunks))]
    )
```

#### Laravel Equivalent (Conceptual)
```php
// If Laravel had embeddings...
public function addDocuments(array $chunks, array $metadata): void
{
    // Convert chunks to embeddings using AI
    $embeddings = $this->embeddingModel->embed($chunks);

    // Input:  ["Python is great", "Guido created Python"]
    // Output: [[0.02, -0.12, 0.56, ...],
    //          [0.15, -0.08, 0.72, ...]]

    // Save to database
    foreach ($chunks as $i => $chunk) {
        DB::table('embeddings')->insert([
            'id' => "{$docId}-chunk-{$i}",
            'text' => $chunk,
            'embedding' => json_encode($embeddings[$i]),
            'metadata' => json_encode($metadata)
        ]);
    }
}
```

---

### Example 3: Searching for Similar Documents

#### Python (RAG)
```python
# app/services/vector_store.py:159-166
def search(self, query: str, top_k: int = 5):
    # Step 1: Convert query to embedding
    query_embedding = self.embeddings.embed_query(query)
    # "Who created Python?" → [0.12, -0.56, 0.90, ...]

    # Step 2: Search ChromaDB for similar vectors
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Results contain most similar documents
    return self._format_results(results)
```

#### Laravel Equivalent (Conceptual)
```php
// If Laravel had vector search...
public function search(string $query, int $topK = 5): array
{
    // Step 1: Convert query to embedding
    $queryEmbedding = $this->embeddingModel->embedQuery($query);
    // "Who created Python?" → [0.12, -0.56, 0.90, ...]

    // Step 2: Calculate similarity with all documents
    $results = DB::table('embeddings')
        ->select('*')
        ->selectRaw('COSINE_SIMILARITY(embedding, ?) as similarity', [$queryEmbedding])
        ->orderBy('similarity', 'desc')
        ->limit($topK)
        ->get();

    return $results;
}
```

---

### Example 4: Generating AI Answer

#### Python (RAG)
```python
# app/services/llm_service.py:88-99
def generate_response(self, query: str, context_documents: list):
    # Build context from documents
    context_text = self._build_context(context_documents)

    # Create prompt
    prompt = f"""Context information:
{context_text}

Question: {query}

Answer based on the context provided above:"""

    # Send to OpenAI
    if self.provider == "openai":
        messages = [
            SystemMessage(content="You are a helpful assistant..."),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content
```

#### Laravel Equivalent
```php
// Using OpenAI PHP package
public function generateResponse(string $query, array $contextDocuments): string
{
    // Build context
    $contextText = $this->buildContext($contextDocuments);

    // Create prompt
    $prompt = "Context information:\n{$contextText}\n\n" .
              "Question: {$query}\n\n" .
              "Answer based on the context provided above:";

    // Send to OpenAI
    $response = OpenAI::chat()->create([
        'model' => 'gpt-4-turbo-preview',
        'messages' => [
            ['role' => 'system', 'content' => 'You are a helpful assistant...'],
            ['role' => 'user', 'content' => $prompt]
        ]
    ]);

    return $response->choices[0]->message->content;
}
```

---

## Database Comparison

### MySQL/PostgreSQL (Laravel)

```sql
-- Users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP
);

-- Search: Exact or LIKE queries
SELECT * FROM users WHERE name = 'John';
SELECT * FROM users WHERE email LIKE '%@gmail.com';
```

**Limitations:**
- Only exact matches or pattern matching
- Can't understand "meaning" or "similarity"
- Can't search: "Find users similar to John" (by interests, behavior, etc.)

---

### ChromaDB (RAG System)

```python
# Documents collection
collection = client.get_collection("documents")

# Data structure
{
    "id": "doc-123-chunk-1",
    "document": "Python is a programming language created by Guido van Rossum",
    "embedding": [0.0234, -0.1234, 0.5678, ..., 0.9012],  # 384 numbers
    "metadata": {
        "document_id": "doc-123",
        "title": "Python History",
        "source_type": "text"
    }
}

# Search: Semantic similarity
results = collection.query(
    query_texts=["Who invented Python?"],
    n_results=5
)
# Returns: Documents about Python's creator, even if they use different words!
```

**Advantages:**
- Understands meaning, not just words
- Finds similar content even with different phrasing
- Perfect for AI/RAG applications

---

## Testing the System

### 1. Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload

# Server runs at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

### 2. Ingest Documents

```bash
# Add text content
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -F 'content=Python is a high-level programming language created by Guido van Rossum in 1991. It emphasizes code readability and simplicity.' \
  -F 'metadata={"title": "Python History", "source": "tutorial"}'

# Add a file
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -F 'file=@document.pdf' \
  -F 'metadata={"title": "My Document"}'

# Add from URL
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -F 'url=https://example.com/article' \
  -F 'metadata={"title": "Web Article"}'
```

---

### 3. Query the System

```bash
# Ask a question
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who created Python?",
    "top_k": 5
  }'

# Response:
{
  "success": true,
  "query": "Who created Python?",
  "answer": "Based on the provided context, Python was created by Guido van Rossum in 1991.",
  "sources": [
    {
      "content": "Python is a high-level programming language created by Guido van Rossum in 1991...",
      "relevance_score": 0.95
    }
  ],
  "processing_time_ms": 1250
}
```

---

### 4. View Database Contents

```bash
# View all documents and embeddings
python3 vector_db_manager.py

# View specific collection stats
python3 vector_db_manager.py --stats

# View actual embedding vectors
python3 vector_db_manager.py --embeddings --limit 3

# Search the database
python3 vector_db_manager.py --search "Python programming"
```

---

### 5. List & Delete Documents

```bash
# List all documents
curl "http://localhost:8000/api/v1/documents"

# Delete a document
curl -X DELETE "http://localhost:8000/api/v1/documents/doc-uuid-123"
```

---

## Summary: Key Takeaways

### 1. **RAG = Search + AI**
```
Your Documents → Vector Database → AI reads them → Intelligent answers
```

### 2. **Ingesting = Adding Data**
```
Text → Chunks → Embeddings → ChromaDB
```

### 3. **Embeddings = Text as Numbers**
```
"Python is great" → [0.02, -0.12, 0.56, ...] (384 numbers)
```

### 4. **Similarity Search = Find Similar Meaning**
```
Query: "Who made Python?"
Finds: "Guido van Rossum created Python"
Even though words are different!
```

### 5. **ChromaDB = Vector Database**
```
Like MySQL, but stores embeddings + text
Searches by similarity, not exact matches
```

---

## Most Important Files (Focus Here)

1. **`app/services/vector_store.py`** - THE CORE
   - Line 77: Text → Embeddings
   - Line 159: Query → Embeddings
   - Line 162: Similarity search

2. **`app/services/rag_service.py`** - Orchestration
   - Line 59: Search documents
   - Line 83: Generate AI answer

3. **`app/services/llm_service.py`** - AI Communication
   - Line 88: Send to OpenAI/Claude

4. **`app/api/routes/documents.py`** - Document API
   - Line 35: Ingest endpoint

5. **`app/api/routes/query.py`** - Query API
   - Line 24: Ask questions

---

## Next Steps

1. **Add your OpenAI API key** to `.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Restart the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Test the complete flow**:
   ```bash
   # 1. Ingest
   curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
     -F 'content=Python was created by Guido van Rossum in 1991.'

   # 2. Query
   curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Who created Python?"}'
   ```

4. **Experiment!**
   - Add your own documents
   - Ask different questions
   - View the embeddings with `vector_db_manager.py`

---

## Questions?

If you need clarification on any part:
1. Check the line numbers referenced in this guide
2. Read the code comments in each file
3. Use `vector_db_manager.py` to see actual data
4. Test with simple examples first

Happy coding! 🚀
