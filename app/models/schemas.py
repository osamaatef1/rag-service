"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


# ===== Request Models =====

class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion."""
    content: Optional[str] = Field(None, description="Raw text content (for direct text input)")
    url: Optional[HttpUrl] = Field(None, description="URL to fetch and ingest")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom metadata to attach to the document"
    )
    collection: Optional[str] = Field(
        None,
        description="Collection/namespace to store document in"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "This is a sample document content...",
                "metadata": {
                    "source": "user_upload",
                    "category": "documentation",
                    "author": "John Doe"
                },
                "collection": "my_documents"
            }
        }


class QueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., min_length=1, description="The question or query text")
    collection: Optional[str] = Field(
        None,
        description="Collection/namespace to search in"
    )
    top_k: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Number of relevant documents to retrieve"
    )
    metadata_filter: Optional[Dict[str, Any]] = Field(
        None,
        description="Filter documents by metadata"
    )
    stream: bool = Field(
        False,
        description="Enable streaming response"
    )
    include_sources: bool = Field(
        True,
        description="Include source documents in response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the refund policy?",
                "top_k": 5,
                "metadata_filter": {"category": "policies"},
                "include_sources": True
            }
        }


class DocumentFilter(BaseModel):
    """Filter parameters for listing documents."""
    collection: Optional[str] = None
    metadata_filter: Optional[Dict[str, Any]] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ===== Response Models =====

class DocumentMetadata(BaseModel):
    """Document metadata information."""
    document_id: str
    filename: Optional[str] = None
    collection: str
    created_at: datetime
    chunk_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    """Response model for document ingestion."""
    success: bool
    document_id: str
    message: str
    chunks_created: int
    metadata: DocumentMetadata

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_123456",
                "message": "Document ingested successfully",
                "chunks_created": 15,
                "metadata": {
                    "document_id": "doc_123456",
                    "filename": "policy.pdf",
                    "collection": "documents",
                    "created_at": "2024-01-15T10:30:00Z",
                    "chunk_count": 15,
                    "metadata": {}
                }
            }
        }


class SourceDocument(BaseModel):
    """Source document with relevance information."""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    relevance_score: float = Field(..., ge=0, le=1)


class QueryResponse(BaseModel):
    """Response model for RAG query."""
    success: bool
    query: str
    answer: str
    sources: Optional[List[SourceDocument]] = None
    processing_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "What is the refund policy?",
                "answer": "According to our refund policy, customers can request a full refund within 30 days of purchase...",
                "sources": [
                    {
                        "document_id": "doc_123",
                        "content": "Refund policy: Full refund within 30 days...",
                        "metadata": {"filename": "policy.pdf", "page": 5},
                        "relevance_score": 0.95
                    }
                ],
                "processing_time_ms": 1234.56,
                "metadata": {"model": "gpt-4", "tokens_used": 450}
            }
        }


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""
    success: bool
    total: int
    documents: List[DocumentMetadata]
    limit: int
    offset: int


class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion."""
    success: bool
    document_id: str
    message: str
    chunks_deleted: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    uptime_seconds: float
    vector_db_status: str
    total_documents: int
    total_chunks: int

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "uptime_seconds": 3600.5,
                "vector_db_status": "connected",
                "total_documents": 150,
                "total_chunks": 2340
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Document not found",
                "detail": "No document exists with ID: doc_123",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
