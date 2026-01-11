# Quick Start: Vector Database Usage

## 🎯 What You Need to Do (3 Simple Steps)

### **STEP 1: Add Documents to Vector Database**

#### Method A: Run the Example Script (Easiest)
```bash
# Add sample documents and search
python add_document_example.py

# Add your own file
python add_document_example.py /path/to/your/file.txt
```

#### Method B: Use the API (After starting service)
```bash
# Start the service first
./run.sh

# Then add text
curl -X POST "http://localhost:8000/api/v1/documents/text" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your text here...",
    "metadata": {"title": "My Document"}
  }'
```

---

### **STEP 2: Preview/Inspect the Database**

```bash
# View all documents
python inspect_database.py

# View specific document details
python inspect_database.py --document-id abc-123-def-456

# Search the database
python inspect_database.py --search "What is Python?"
```

**Output Example:**
```
================================================================================
🔍 ChromaDB Vector Database Inspector
================================================================================
Database Path: ./storage/chromadb

📦 Collections (1):
================================================================================
  • documents (15 chunks)

📊 Statistics for Collection 'documents':
================================================================================
  Total Chunks:      15
  Unique Documents:  3

  Sources Breakdown:
    • text: 15 chunks

📄 Documents Preview (showing up to 10 documents):
================================================================================
+----------------------+--------------------------------+--------+--------+---------------------+
| Document ID          | Title                          | Source | Chunks | Created At          |
+======================+================================+========+========+=====================+
| abc-123-def-456...   | Python Programming Language    | text   |      5 | 2024-01-05T12:00:00 |
+----------------------+--------------------------------+--------+--------+---------------------+
| def-456-ghi-789...   | Machine Learning Introduction  | text   |      5 | 2024-01-05T12:01:00 |
+----------------------+--------------------------------+--------+--------+---------------------+
```

---

### **STEP 3: Search and Query**

#### Option A: Direct Python Script
```python
from app.services.vector_store import vector_store

# Search
results = vector_store.search(query="What is Python?", top_k=3)

for result in results:
    print(f"Score: {result['relevance_score']:.2f}")
    print(f"Content: {result['content']}")
```

#### Option B: Use the API
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "X-API-Key: your-secret-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "top_k": 3
  }'
```

---

## 📁 Where is the Database Stored?

Your vector database is stored at:
```
./storage/chromadb/
```

This directory contains:
- **Embeddings**: 384-dimensional vectors for each text chunk
- **Documents**: Original text chunks
- **Metadata**: Document information, titles, timestamps, etc.

---

## 🔍 What's Inside the Database?

Each document in the database contains:

1. **Original Text** - Your sentence/paragraph
2. **Embedding Vector** - 384 numbers representing the meaning
3. **Metadata** - Title, author, category, timestamps, etc.

Example:
```
Document ID: abc-123-def-456
Text: "Python is a programming language..."
Embedding: [0.123, -0.456, 0.789, ... ] (384 dimensions)
Metadata: {
  "title": "Python Introduction",
  "category": "programming",
  "created_at": "2024-01-05T12:00:00"
}
```

---

## 🎨 Visual Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Your Text or File                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Split into Chunks                                  │
│  "Python is..." | "Machine learning..." | "Vector DB..."    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Convert to Embeddings (Vectors)                    │
│  [0.12, -0.45, ...] | [0.89, 0.23, ...] | [-0.67, ...]     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Store in ChromaDB                                  │
│  ./storage/chromadb/                                        │
│  ✓ Text + Vector + Metadata                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Search                                             │
│  Query: "What is Python?" → Vector → Find Similar → Result │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Commands Cheat Sheet

```bash
# Add sample documents
python add_document_example.py

# Add your file
python add_document_example.py myfile.txt

# View database
python inspect_database.py

# Search database
python inspect_database.py --search "your query here"

# View specific document
python inspect_database.py --document-id abc-123

# Start API service
./run.sh

# View API docs (after starting service)
# Open: http://localhost:8000/docs
```

---

## 🛠️ Configuration

Database settings in `.env` file:
```env
# Where to store the database
CHROMADB_PATH=./storage/chromadb

# Collection name
CHROMADB_COLLECTION_NAME=documents

# Embedding model (converts text to vectors)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# How many chunks to split documents into
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Search settings
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

---

## ❓ Common Questions

**Q: Where are my vectors stored?**
A: In `./storage/chromadb/` - it's a folder with database files

**Q: Can I view the raw vectors?**
A: Yes! Run `python inspect_database.py --document-id <id>` to see embedding dimensions

**Q: How do I delete a document?**
A: Use the API: `curl -X DELETE http://localhost:8000/api/v1/documents/<doc-id>` or use Python:
```python
from app.services.vector_store import vector_store
vector_store.delete_document("doc-id")
```

**Q: Can I use a different embedding model?**
A: Yes! Change `EMBEDDING_MODEL` in `.env` file. Options:
- `sentence-transformers/all-MiniLM-L6-v2` (384 dim, fast)
- `sentence-transformers/all-mpnet-base-v2` (768 dim, better quality)

**Q: How does similarity search work?**
A: Your query is converted to a vector, then ChromaDB finds the closest vectors using cosine similarity.

---

## 🚀 Next Steps

1. ✅ Run `python add_document_example.py` to add sample documents
2. ✅ Run `python inspect_database.py` to see what's stored
3. ✅ Run `python inspect_database.py --search "your question"` to test search
4. ✅ Start the API with `./run.sh` and visit http://localhost:8000/docs
5. ✅ Add your own documents via API or Python scripts

---

Need help? Check:
- [step_by_step_guide.md](step_by_step_guide.md) - API usage guide
- [README.md](README.md) - Full documentation
- API Docs: http://localhost:8000/docs (when service is running)
