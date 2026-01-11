#!/usr/bin/env python3
"""
Vector Database Manager - All-in-one tool for managing your vector database.
Combines: adding documents, viewing data, and inspecting embeddings.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np
import argparse


class VectorDBManager:
    """Manage ChromaDB vector database."""

    def __init__(self, db_path="./storage/chromadb"):
        self.db_path = db_path

        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            print("   Add documents first using the API")
            sys.exit(1)

        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=False)
        )

    def list_collections(self):
        """List all collections."""
        collections = self.client.list_collections()

        if not collections:
            print("📦 No collections found.")
            return

        print("\n" + "="*80)
        print("📦 COLLECTIONS")
        print("="*80)

        for col in collections:
            count = col.count()
            print(f"\n  • {col.name} ({count} chunks)")

    def show_stats(self, collection_name="documents"):
        """Show collection statistics."""
        try:
            collection = self.client.get_collection(collection_name)
        except:
            print(f"❌ Collection '{collection_name}' not found.")
            return

        total_chunks = collection.count()

        if total_chunks == 0:
            print(f"\n📊 Collection '{collection_name}' is empty.")
            return

        results = collection.get(include=["metadatas"])

        unique_docs = set()
        sources = {}

        for meta in results["metadatas"]:
            doc_id = meta.get("document_id")
            if doc_id:
                unique_docs.add(doc_id)

            source = meta.get("source_type", "unknown")
            sources[source] = sources.get(source, 0) + 1

        print("\n" + "="*80)
        print(f"📊 STATISTICS - Collection '{collection_name}'")
        print("="*80)
        print(f"\n  Total Chunks:      {total_chunks}")
        print(f"  Unique Documents:  {len(unique_docs)}")
        print(f"\n  Sources:")
        for source, count in sources.items():
            print(f"    • {source}: {count} chunks")

    def list_documents(self, collection_name="documents", limit=10):
        """List documents."""
        try:
            collection = self.client.get_collection(collection_name)
        except:
            print(f"❌ Collection '{collection_name}' not found.")
            return

        results = collection.get(limit=limit, include=["metadatas", "documents"])

        if not results["documents"]:
            print(f"\n📄 No documents found.")
            return

        docs_map = {}
        for i, meta in enumerate(results["metadatas"]):
            doc_id = meta.get("document_id", "unknown")

            if doc_id not in docs_map:
                docs_map[doc_id] = {
                    "id": doc_id,
                    "title": meta.get("title", meta.get("filename", "Untitled")),
                    "source": meta.get("source_type", "unknown"),
                    "created": meta.get("created_at", "N/A")[:19],
                    "chunks": []
                }

            docs_map[doc_id]["chunks"].append(results["documents"][i])

        print("\n" + "="*80)
        print(f"📄 DOCUMENTS (showing up to {limit})")
        print("="*80)

        for idx, (doc_id, info) in enumerate(list(docs_map.items())[:limit], 1):
            print(f"\n[{idx}] {info['title']}")
            print(f"    ID: {doc_id[:30]}...")
            print(f"    Source: {info['source']} | Chunks: {len(info['chunks'])} | Created: {info['created']}")
            print(f"    Preview: {info['chunks'][0][:100]}...")

    def view_embeddings(self, collection_name="documents", limit=5):
        """View actual embedding vectors."""
        try:
            collection = self.client.get_collection(collection_name)
        except:
            print(f"❌ Collection '{collection_name}' not found.")
            return

        results = collection.get(
            limit=limit,
            include=["documents", "metadatas", "embeddings"]
        )

        if not results["documents"]:
            print(f"\n🔢 No embeddings found.")
            return

        print("\n" + "="*80)
        print(f"🔢 EMBEDDINGS - Collection '{collection_name}'")
        print("="*80)

        for i, (doc, meta, emb) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["embeddings"]
        ), 1):
            emb_array = np.array(emb)

            print(f"\n{'='*80}")
            print(f"CHUNK {i}")
            print(f"{'='*80}")

            print(f"\n📄 Text:")
            print(f"   {doc[:150]}...")

            print(f"\n📋 Metadata:")
            print(f"   Title: {meta.get('title', 'N/A')}")
            print(f"   Document ID: {meta.get('document_id', 'N/A')[:30]}...")

            print(f"\n🔢 Embedding Vector:")
            print(f"   Dimensions: {len(emb)}")
            print(f"   First 15 values: {[f'{x:.4f}' for x in emb[:15]]}")
            print(f"   Last 15 values:  {[f'{x:.4f}' for x in emb[-15:]]}")

            print(f"\n📊 Statistics:")
            print(f"   Min:       {np.min(emb_array):.6f}")
            print(f"   Max:       {np.max(emb_array):.6f}")
            print(f"   Mean:      {np.mean(emb_array):.6f}")
            print(f"   Std Dev:   {np.std(emb_array):.6f}")
            print(f"   Magnitude: {np.linalg.norm(emb_array):.6f}")

    def search(self, query, collection_name="documents", top_k=3):
        """Search using the vector store service."""
        try:
            from app.services.vector_store import vector_store

            print("\n" + "="*80)
            print(f"🔍 SEARCH: '{query}'")
            print("="*80)

            results = vector_store.search(
                query=query,
                top_k=top_k,
                collection_name=collection_name
            )

            if not results:
                print("\n❌ No results found.")
                return

            print(f"\n✅ Found {len(results)} results:\n")

            for i, result in enumerate(results, 1):
                print(f"[{i}] Relevance: {result['relevance_score']:.4f}")
                print(f"    Doc ID: {result['metadata'].get('document_id', 'N/A')[:30]}...")
                print(f"    Content: {result['content'][:200]}...")
                print()

        except ImportError:
            print("❌ Cannot search. Make sure the service is properly configured.")


def main():
    parser = argparse.ArgumentParser(
        description="Vector Database Manager - View and manage your ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vector_db_manager.py --list              # List all collections
  python vector_db_manager.py --stats             # Show statistics
  python vector_db_manager.py --documents         # List documents
  python vector_db_manager.py --embeddings        # View embedding vectors
  python vector_db_manager.py --search "Python"   # Search for documents
        """
    )

    parser.add_argument("--list", action="store_true", help="List all collections")
    parser.add_argument("--stats", action="store_true", help="Show collection statistics")
    parser.add_argument("--documents", action="store_true", help="List documents")
    parser.add_argument("--embeddings", action="store_true", help="View embeddings")
    parser.add_argument("--search", type=str, help="Search for similar documents")
    parser.add_argument("--collection", default="documents", help="Collection name")
    parser.add_argument("--limit", type=int, default=10, help="Limit results")
    parser.add_argument("--top-k", type=int, default=3, help="Number of search results")

    args = parser.parse_args()

    # If no arguments, show all info
    if not any([args.list, args.stats, args.documents, args.embeddings, args.search]):
        args.list = True
        args.stats = True
        args.documents = True

    print("\n" + "="*80)
    print("🔍 VECTOR DATABASE MANAGER")
    print("="*80)

    manager = VectorDBManager()

    if args.list:
        manager.list_collections()

    if args.stats:
        manager.show_stats(args.collection)

    if args.documents:
        manager.list_documents(args.collection, args.limit)

    if args.embeddings:
        manager.view_embeddings(args.collection, args.limit)

    if args.search:
        manager.search(args.search, args.collection, args.top_k)

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
