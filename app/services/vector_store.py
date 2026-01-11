"""
Vector store service for document embeddings and similarity search.
"""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class VectorStore:
    """Vector database service using ChromaDB."""

    def __init__(self):
        """Initialize vector store with ChromaDB."""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMADB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        logger.info(f"Vector store initialized with ChromaDB at {settings.CHROMADB_PATH}")

    def get_or_create_collection(self, collection_name: Optional[str] = None):
        """
        Get or create a ChromaDB collection.

        Args:
            collection_name: Name of the collection (uses default if None)

        Returns:
            ChromaDB collection instance
        """
        name = collection_name or settings.CHROMADB_COLLECTION_NAME

        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        chunks: List[str],
        metadata: Dict[str, Any],
        collection_name: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> tuple[str, int]:
        """
        Add document chunks to vector store.

        Args:
            chunks: List of text chunks
            metadata: Document metadata
            collection_name: Collection to add to
            document_id: Optional custom document ID (generates UUID if not provided)

        Returns:
            Tuple of (document_id, number of chunks added)
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            document_id = document_id or str(uuid.uuid4())

            # Generate embeddings
            embeddings = self.embeddings.embed_documents(chunks)

            # Prepare data for insertion
            ids = [f"{document_id}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    **metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                    "created_at": datetime.utcnow().isoformat()
                }
                for i in range(len(chunks))
            ]

            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            return document_id, len(chunks)

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            top_k: Number of results to return
            metadata_filter: Filter by metadata
            collection_name: Collection to search in

        Returns:
            List of search results with content and metadata
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            k = top_k or settings.TOP_K_RESULTS

            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)

            # Prepare where clause for metadata filtering
            where = metadata_filter if metadata_filter else None

            # Perform search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    # Convert distance to similarity score (cosine similarity: 1 - distance)
                    similarity = 1 - results["distances"][0][i]

                    # Filter by similarity threshold
                    if similarity >= settings.SIMILARITY_THRESHOLD:
                        formatted_results.append({
                            "content": doc,
                            "metadata": results["metadatas"][0][i],
                            "relevance_score": float(similarity)
                        })

            logger.info(f"Found {len(formatted_results)} relevant documents for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise

    def delete_document(
        self,
        document_id: str,
        collection_name: Optional[str] = None
    ) -> int:
        """
        Delete all chunks of a document.

        Args:
            document_id: ID of document to delete
            collection_name: Collection to delete from

        Returns:
            Number of chunks deleted
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            # Get all chunk IDs for this document
            results = collection.get(
                where={"document_id": document_id},
                include=[]
            )

            if not results["ids"]:
                return 0

            # Delete all chunks
            collection.delete(ids=results["ids"])

            chunks_deleted = len(results["ids"])
            logger.info(f"Deleted {chunks_deleted} chunks for document {document_id}")
            return chunks_deleted

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def list_documents(
        self,
        collection_name: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        List documents with pagination.

        Args:
            collection_name: Collection to list from
            metadata_filter: Filter by metadata
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            Tuple of (list of document metadata, total count)
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            # Get all documents (or filtered)
            where = metadata_filter if metadata_filter else None
            results = collection.get(
                where=where,
                include=["metadatas"]
            )

            # Group by document_id
            documents_map = {}
            for metadata in results["metadatas"]:
                doc_id = metadata.get("document_id")
                if doc_id and doc_id not in documents_map:
                    documents_map[doc_id] = {
                        "document_id": doc_id,
                        "collection": collection_name or settings.CHROMADB_COLLECTION_NAME,
                        "created_at": metadata.get("created_at"),
                        "metadata": {k: v for k, v in metadata.items()
                                   if k not in ["document_id", "chunk_index", "created_at"]},
                        "chunk_count": 0
                    }
                if doc_id:
                    documents_map[doc_id]["chunk_count"] += 1

            # Convert to list and apply pagination
            documents = list(documents_map.values())
            total = len(documents)
            documents = documents[offset:offset + limit]

            return documents, total

        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    def get_stats(self, collection_name: Optional[str] = None) -> Dict[str, int]:
        """
        Get collection statistics.

        Args:
            collection_name: Collection to get stats for

        Returns:
            Dictionary with total_chunks and total_documents
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            total_chunks = collection.count()

            # Count unique documents
            results = collection.get(include=["metadatas"])
            unique_docs = set(
                m.get("document_id") for m in results["metadatas"]
                if m.get("document_id")
            )

            return {
                "total_chunks": total_chunks,
                "total_documents": len(unique_docs)
            }

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"total_chunks": 0, "total_documents": 0}


# Global vector store instance
vector_store = VectorStore()
