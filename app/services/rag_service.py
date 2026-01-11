"""
RAG (Retrieval-Augmented Generation) service combining vector search and LLM.
"""
import time
from typing import Dict, Any, Optional, List
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.utils.cache import query_cache
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class RAGService:
    """Main RAG service orchestrating retrieval and generation."""

    def __init__(self):
        """Initialize RAG service."""
        self.vector_store = vector_store
        self.llm_service = llm_service

    def query(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Process a RAG query: retrieve context and generate response.

        Args:
            query: User's question
            collection: Collection to search in
            top_k: Number of documents to retrieve
            metadata_filter: Filter documents by metadata
            include_sources: Whether to include source documents in response

        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = time.time()

        try:
            # Check cache if enabled
            cache_key = f"{query}:{collection}:{top_k}:{str(metadata_filter)}"
            if settings.ENABLE_QUERY_CACHE:
                cached_result = query_cache.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for query: {query[:50]}...")
                    cached_result["processing_time_ms"] = (time.time() - start_time) * 1000
                    cached_result["metadata"]["cached"] = True
                    return cached_result

            # Step 1: Retrieve relevant documents
            logger.info(f"Retrieving context for query: {query[:50]}...")
            context_documents = self.vector_store.search(
                query=query,
                top_k=top_k,
                metadata_filter=metadata_filter,
                collection_name=collection
            )

            if not context_documents:
                logger.warning("No relevant documents found")
                result = {
                    "success": True,
                    "query": query,
                    "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing or ask something else.",
                    "sources": [],
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "metadata": {
                        "documents_retrieved": 0,
                        "model": self.llm_service.provider
                    }
                }
                return result

            # Step 2: Generate response using LLM
            logger.info(f"Generating response with {len(context_documents)} context documents")
            answer = self.llm_service.generate_response(
                query=query,
                context_documents=context_documents
            )

            # Prepare response
            processing_time = (time.time() - start_time) * 1000

            result = {
                "success": True,
                "query": query,
                "answer": answer,
                "sources": self._format_sources(context_documents) if include_sources else None,
                "processing_time_ms": processing_time,
                "metadata": {
                    "documents_retrieved": len(context_documents),
                    "model": self.llm_service.provider,
                    "cached": False
                }
            }

            # Cache the result
            if settings.ENABLE_QUERY_CACHE:
                query_cache.set(cache_key, result, settings.CACHE_TTL_SECONDS)

            logger.info(f"Query processed successfully in {processing_time:.2f}ms")
            return result

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format source documents for response.

        Args:
            documents: Raw document results from vector store

        Returns:
            Formatted source documents
        """
        sources = []
        for doc in documents:
            sources.append({
                "document_id": doc["metadata"].get("document_id", "unknown"),
                "content": doc["content"][:500],  # Truncate for response size
                "metadata": {
                    k: v for k, v in doc["metadata"].items()
                    if k not in ["document_id", "chunk_index"]
                },
                "relevance_score": doc["relevance_score"]
            })
        return sources


# Global RAG service instance
rag_service = RAGService()
