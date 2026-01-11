#!/usr/bin/env python3
"""
Google Sheets to Vector Database Importer
Import Google Sheets data directly into the RAG vector database.
Supports both public sheets and automatic updates.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import pandas as pd
import argparse
from datetime import datetime
from app.services.vector_store import vector_store
from app.utils.document_processor import document_processor


def extract_sheet_id_and_gid(url: str):
    """
    Extract spreadsheet ID and sheet GID from Google Sheets URL.

    Example URL:
    https://docs.google.com/spreadsheets/d/120N5P6w0mhP0DdzjaOTlNUWe1jkbPoT0/edit?gid=2084436400#gid=2084436400

    Returns:
        tuple: (spreadsheet_id, gid)
    """
    # Extract spreadsheet ID
    if '/d/' in url:
        sheet_id = url.split('/d/')[1].split('/')[0]
    else:
        print("❌ Error: Invalid Google Sheets URL")
        sys.exit(1)

    # Extract GID (sheet tab ID)
    gid = '0'  # Default first sheet
    if 'gid=' in url:
        gid = url.split('gid=')[1].split('&')[0].split('#')[0]

    return sheet_id, gid


def read_google_sheet(url: str):
    """
    Read Google Sheets data as CSV.
    Works only with PUBLIC sheets (anyone with link can view).

    Args:
        url: Google Sheets URL

    Returns:
        pandas DataFrame
    """
    print(f"\n📖 Reading Google Sheet...")

    # Extract IDs
    sheet_id, gid = extract_sheet_id_and_gid(url)

    # Build CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    print(f"   Sheet ID: {sheet_id}")
    print(f"   GID: {gid}")

    try:
        # Download as CSV
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()

        # Parse CSV
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))

        print(f"✅ Successfully loaded sheet")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")

        return df, sheet_id

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403 or e.response.status_code == 401:
            print("\n❌ Error: Sheet is PRIVATE")
            print("\n💡 Solution:")
            print("   1. Open your Google Sheet")
            print("   2. Click 'Share' button (top right)")
            print("   3. Click 'Anyone with the link' can view")
            print("   4. Click 'Done'")
            print("   5. Try again\n")
        else:
            print(f"\n❌ Error downloading sheet: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def format_row_as_text(row, columns):
    """
    Convert a DataFrame row to formatted text.

    For your case with Header + Details:
    "Header: [value]. Details: [value]."
    """
    parts = []
    for col in columns:
        value = row[col]
        # Skip empty values
        if pd.notna(value) and str(value).strip():
            parts.append(f"{col}: {value}")

    return ". ".join(parts) + "."


def preview_data(df, num_rows=5):
    """Show preview of data that will be imported."""
    print("\n" + "="*80)
    print("📋 DATA PREVIEW")
    print("="*80)
    print(f"\nShowing first {min(num_rows, len(df))} rows:\n")

    for idx, row in df.head(num_rows).iterrows():
        text = format_row_as_text(row, df.columns)
        print(f"Row {idx + 1}:")
        print(f"  {text[:300]}{'...' if len(text) > 300 else ''}")
        print()


def import_google_sheet(
    url: str,
    title: str = None,
    collection: str = "documents",
    preview_only: bool = False,
    auto_confirm: bool = False
):
    """
    Import Google Sheets data into vector database.

    Args:
        url: Google Sheets URL
        title: Document title for metadata
        collection: ChromaDB collection name
        preview_only: If True, only show preview
        auto_confirm: If True, skip confirmation prompt
    """
    # Read Google Sheet
    df, sheet_id = read_google_sheet(url)

    if len(df) == 0:
        print("❌ Error: Google Sheet is empty")
        sys.exit(1)

    # Show preview
    preview_data(df)

    if preview_only:
        print("\n✅ Preview mode - no data imported")
        return

    # Confirm import
    if not auto_confirm:
        print("="*80)
        response = input(f"Import {len(df)} rows into vector database? (y/n): ")
        if response.lower() != 'y':
            print("❌ Import cancelled")
            return

    print("\n" + "="*80)
    print("📥 IMPORTING TO VECTOR DATABASE")
    print("="*80)

    # Convert each row to text
    all_texts = []
    for idx, row in df.iterrows():
        text = format_row_as_text(row, df.columns)
        all_texts.append(text)

        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(df)} rows...")

    print(f"✅ Processed all {len(df)} rows")

    # Combine all texts
    combined_text = "\n\n".join(all_texts)

    # Process into chunks
    print("\n🔧 Chunking text...")
    chunks = document_processor.process_document(combined_text)
    print(f"   Created {len(chunks)} chunks")

    # Prepare metadata
    metadata = {
        "source_type": "google_sheets",
        "sheet_id": sheet_id,
        "sheet_url": url,
        "title": title or "Google Sheet Data",
        "total_rows": len(df),
        "columns_list": ", ".join([str(col) for col in df.columns]),  # Convert list to string
        "ingested_at": datetime.utcnow().isoformat()
    }

    # Check if this sheet was imported before (for updates)
    document_id = f"google-sheet-{sheet_id}"

    # Delete old version if exists
    try:
        vector_store.delete_document(document_id, collection)
        print(f"   Deleted old version of this sheet")
    except:
        pass  # First time import

    # Add to vector store
    print("\n⚡ Converting to embeddings and storing...")
    document_id, chunk_count = vector_store.add_documents(
        chunks=chunks,
        metadata=metadata,
        collection_name=collection,
        document_id=document_id  # Use consistent ID for updates
    )

    print("\n" + "="*80)
    print("✅ IMPORT COMPLETE!")
    print("="*80)
    print(f"\n  Document ID: {document_id}")
    print(f"  Total Rows: {len(df)}")
    print(f"  Chunks Created: {chunk_count}")
    print(f"  Collection: {collection}")
    print(f"\n💡 You can now query this data:")
    print(f"   curl -X POST 'http://localhost:8000/api/v1/query' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"query\": \"Tell me about [your topic]\"}}'")
    print(f"\n💡 To update when sheet changes:")
    print(f"   python google_sheets_to_vectordb.py \"{url}\" --auto-confirm")
    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Import Google Sheets into RAG Vector Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview data (no import)
  python google_sheets_to_vectordb.py "YOUR_SHEET_URL" --preview

  # Import with confirmation
  python google_sheets_to_vectordb.py "YOUR_SHEET_URL"

  # Import with custom title
  python google_sheets_to_vectordb.py "YOUR_SHEET_URL" --title "Product Catalog"

  # Auto-import (no confirmation) - good for updates
  python google_sheets_to_vectordb.py "YOUR_SHEET_URL" --auto-confirm

  # View imported data
  python vector_db_manager.py --documents

IMPORTANT:
  Your Google Sheet must be PUBLIC (anyone with link can view)

  To make it public:
  1. Open your Google Sheet
  2. Click 'Share' button (top right)
  3. Select 'Anyone with the link' can view
  4. Click 'Done'
        """
    )

    parser.add_argument("url", help="Google Sheets URL")
    parser.add_argument("--title", help="Document title for metadata")
    parser.add_argument("--collection", default="documents", help="ChromaDB collection")
    parser.add_argument("--preview", action="store_true", help="Preview without importing")
    parser.add_argument("--auto-confirm", action="store_true", help="Skip confirmation (useful for updates)")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("📊 GOOGLE SHEETS TO VECTOR DATABASE")
    print("="*80)

    import_google_sheet(
        url=args.url,
        title=args.title,
        collection=args.collection,
        preview_only=args.preview,
        auto_confirm=args.auto_confirm
    )


if __name__ == "__main__":
    main()
