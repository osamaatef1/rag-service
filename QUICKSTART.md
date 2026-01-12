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
