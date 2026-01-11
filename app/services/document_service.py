"""
Document service for managing document ingestion and lifecycle.
"""
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
from app.services.vector_store import vector_store
from app.utils.document_processor import document_processor
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class DocumentService:
    """Service for document operations."""

    def __init__(self):
        """Initialize document service."""
        self.vector_store = vector_store
        self.processor = document_processor

    def ingest_text(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest raw text content.

        Args:
            content: Text content to ingest
            metadata: Optional metadata
            collection: Collection to store in

        Returns:
            Ingestion result with document_id and chunk count
        """
        try:
            logger.info("Processing text content for ingestion")

            # Process document into chunks
            chunks = self.processor.process_document(content)

            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "source_type": "text",
                "ingested_at": datetime.utcnow().isoformat()
            })

            # Add to vector store
            document_id, chunk_count = self.vector_store.add_documents(
                chunks=chunks,
                metadata=doc_metadata,
                collection_name=collection
            )

            logger.info(f"Successfully ingested text document: {document_id}")

            return {
                "document_id": document_id,
                "chunks_created": chunk_count,
                "metadata": {
                    "document_id": document_id,
                    "collection": collection or settings.CHROMADB_COLLECTION_NAME,
                    "created_at": doc_metadata["ingested_at"],
                    "chunk_count": chunk_count,
                    "metadata": doc_metadata
                }
            }

        except Exception as e:
            logger.error(f"Error ingesting text: {str(e)}")
            raise

    def ingest_file(
        self,
        file: BinaryIO,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a file.

        Args:
            file: File object
            filename: Original filename
            metadata: Optional metadata
            collection: Collection to store in

        Returns:
            Ingestion result
        """
        try:
            # Get file extension
            file_ext = Path(filename).suffix.lstrip('.').lower()

            if file_ext not in settings.allowed_file_types_list:
                raise ValueError(f"File type '{file_ext}' is not allowed")

            logger.info(f"Processing file: {filename}")

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
                tmp_file.write(file.read())
                tmp_path = tmp_file.name

            try:
                # Extract text from file
                text_content = self.processor.extract_text_from_file(tmp_path, file_ext)

                # Process and ingest
                chunks = self.processor.process_document(text_content)

                # Prepare metadata
                doc_metadata = metadata or {}
                doc_metadata.update({
                    "source_type": "file",
                    "filename": filename,
                    "file_type": file_ext,
                    "ingested_at": datetime.utcnow().isoformat()
                })

                # Add to vector store
                document_id, chunk_count = self.vector_store.add_documents(
                    chunks=chunks,
                    metadata=doc_metadata,
                    collection_name=collection
                )

                logger.info(f"Successfully ingested file {filename}: {document_id}")

                return {
                    "document_id": document_id,
                    "chunks_created": chunk_count,
                    "metadata": {
                        "document_id": document_id,
                        "filename": filename,
                        "collection": collection or settings.CHROMADB_COLLECTION_NAME,
                        "created_at": doc_metadata["ingested_at"],
                        "chunk_count": chunk_count,
                        "metadata": doc_metadata
                    }
                }

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Error ingesting file {filename}: {str(e)}")
            raise

    def ingest_url(
        self,
        url: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest content from URL.

        Args:
            url: URL to fetch
            metadata: Optional metadata
            collection: Collection to store in

        Returns:
            Ingestion result
        """
        try:
            logger.info(f"Fetching content from URL: {url}")

            # Fetch and extract text
            text_content = self.processor.extract_text_from_url(url)

            # Process and ingest
            chunks = self.processor.process_document(text_content)

            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "source_type": "url",
                "url": url,
                "ingested_at": datetime.utcnow().isoformat()
            })

            # Add to vector store
            document_id, chunk_count = self.vector_store.add_documents(
                chunks=chunks,
                metadata=doc_metadata,
                collection_name=collection
            )

            logger.info(f"Successfully ingested URL {url}: {document_id}")

            return {
                "document_id": document_id,
                "chunks_created": chunk_count,
                "metadata": {
                    "document_id": document_id,
                    "collection": collection or settings.CHROMADB_COLLECTION_NAME,
                    "created_at": doc_metadata["ingested_at"],
                    "chunk_count": chunk_count,
                    "metadata": doc_metadata
                }
            }

        except Exception as e:
            logger.error(f"Error ingesting URL {url}: {str(e)}")
            raise

    def list_documents(
        self,
        collection: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List documents with pagination.

        Args:
            collection: Collection to list from
            metadata_filter: Filter by metadata
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of documents with pagination info
        """
        try:
            documents, total = self.vector_store.list_documents(
                collection_name=collection,
                metadata_filter=metadata_filter,
                limit=limit,
                offset=offset
            )

            return {
                "success": True,
                "total": total,
                "documents": documents,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    def delete_document(
        self,
        document_id: str,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a document.

        Args:
            document_id: ID of document to delete
            collection: Collection to delete from

        Returns:
            Deletion result
        """
        try:
            chunks_deleted = self.vector_store.delete_document(
                document_id=document_id,
                collection_name=collection
            )

            if chunks_deleted == 0:
                raise ValueError(f"Document not found: {document_id}")

            logger.info(f"Successfully deleted document: {document_id}")

            return {
                "success": True,
                "document_id": document_id,
                "message": "Document deleted successfully",
                "chunks_deleted": chunks_deleted
            }

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise


# Global document service instance
document_service = DocumentService()
