# Google Sheets Import Guide

## ✅ Successfully Imported Your Sheet!

Your Google Sheet about Environmental Management (الإدارة البيئية) has been imported into the vector database.

**Stats:**
- 📊 Rows: 60
- 📦 Chunks: 25
- 🆔 Document ID: `google-sheet-120N5P6w0mhP0DdzjaOTlNUWe1jkbPoT0`

---

## How to Use

### 1. Query Your Data (Arabic or English)

```bash
# Arabic query example
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "ما هي الثدييات البرية؟", "top_k": 3}'

# English query example
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about environmental management", "top_k": 3}'
```

### 2. View Your Data

```bash
# View all documents
python vector_db_manager.py --documents

# View embeddings
python vector_db_manager.py --embeddings --limit 5

# Search in the database
python vector_db_manager.py --search "البيئة"
```

### 3. Update When Sheet Changes

When you update your Google Sheet, simply run:

```bash
python google_sheets_to_vectordb.py \
  "https://docs.google.com/spreadsheets/d/120N5P6w0mhP0DdzjaOTlNUWe1jkbPoT0/edit?gid=2084436400#gid=2084436400" \
  --auto-confirm
```

This will:
- ✅ Delete the old version
- ✅ Import the new version
- ✅ Keep the same document ID

---

## How It Works

### Your Google Sheet Structure

```
| Header Column | Details Column |
|---------------|----------------|
| الثدييات البرية | تلعب الثدييات البرية دوراً حيوياً... |
| الطيور         | تعد الطيور البرية مؤشراً حيوياً... |
```

### What Happens During Import

1. **Read Sheet**: Downloads your Google Sheet as CSV
2. **Format Data**: Each row becomes: "Header: [value]. Details: [value]."
3. **Chunk Text**: Splits into 1000-character chunks (25 chunks from your 60 rows)
4. **Create Embeddings**: Converts each chunk to 384 numbers using AI
5. **Store in ChromaDB**: Saves text + embeddings for semantic search

### Example of One Row After Processing

**Original Row:**
| الإدارة البيئية | الثدييات البرية | تلعب الثدييات البرية دوراً حيوياً... |

**Becomes:**
```
الإدارة البيئية: الثدييات البرية. Unnamed: 3: تلعب الثدييات البرية دوراً حيوياً...
```

**Then converted to embedding:**
```
[0.0234, -0.1234, 0.5678, ..., 0.9012]  (384 numbers)
```

---

## Requirements for Google Sheets

### ⚠️ IMPORTANT: Sheet Must Be PUBLIC

Your sheet must be set to "Anyone with the link can view"

**To make your sheet public:**
1. Open your Google Sheet
2. Click **Share** button (top right)
3. Click **"Anyone with the link"**
4. Select **"Viewer"**
5. Click **Done**

---

## Common Commands

### Import New Sheet

```bash
# Preview first (don't import)
python google_sheets_to_vectordb.py "YOUR_SHEET_URL" --preview

# Import with title
python google_sheets_to_vectordb.py "YOUR_SHEET_URL" --title "My Data"

# Import (asks confirmation)
python google_sheets_to_vectordb.py "YOUR_SHEET_URL"

# Import (no confirmation - for automation)
python google_sheets_to_vectordb.py "YOUR_SHEET_URL" --auto-confirm
```

### View Database

```bash
# List all collections
python vector_db_manager.py --list

# Show statistics
python vector_db_manager.py --stats

# List documents
python vector_db_manager.py --documents --limit 10

# View embeddings
python vector_db_manager.py --embeddings --limit 3

# Search
python vector_db_manager.py --search "البيئة"
```

### Delete Document

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/google-sheet-120N5P6w0mhP0DdzjaOTlNUWe1jkbPoT0"
```

---

## Automate Updates

### Option 1: Manual Script

Create `update_sheet.sh`:
```bash
#!/bin/bash
source venv/bin/activate
python google_sheets_to_vectordb.py \
  "YOUR_SHEET_URL" \
  --auto-confirm
```

Run: `bash update_sheet.sh`

### Option 2: Cron Job (Auto-update every hour)

```bash
# Edit crontab
crontab -e

# Add this line (update every hour)
0 * * * * cd /path/to/rag-service && source venv/bin/activate && python google_sheets_to_vectordb.py "YOUR_URL" --auto-confirm
```

---

## Example Queries for Your Environmental Data

```bash
# Query 1: About mammals
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "أخبرني عن الثدييات البرية", "top_k": 3}'

# Query 2: About birds
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "ما هي الطيور؟", "top_k": 3}'

# Query 3: Environmental management
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "ما هي الإدارة البيئية؟", "top_k": 5}'
```

---

## Troubleshooting

### Error: "Sheet is PRIVATE"

**Solution**: Make your sheet public (see Requirements section above)

### Error: "Module not found"

```bash
# Install dependencies
source venv/bin/activate
pip install pandas openpyxl requests
```

### Error: "Invalid URL"

Make sure your URL looks like:
```
https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=GID#gid=GID
```

---

## Files Created

- `google_sheets_to_vectordb.py` - Import script
- `vector_db_manager.py` - View/manage database
- `storage/chromadb/` - Your vector database

---

## Next Steps

1. ✅ **Test queries** with your Arabic environmental data
2. ✅ **View the database** to see how chunks are stored
3. ✅ **Update the sheet** and re-import to test updates
4. ✅ **Automate** with cron job if needed

---

## Support

- View all documents: `python vector_db_manager.py --documents`
- Search database: `python vector_db_manager.py --search "keyword"`
- Check API docs: `http://localhost:8000/docs`

Happy querying! 🚀
