"""
API routes for document management.
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.models.schemas import (
    DocumentIngestResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    ErrorResponse
)
from app.services.document_service import document_service
# Simplified: Removed authentication and rate limiting for easier understanding
# from app.core.security import verify_api_key
# from app.api.dependencies.rate_limit import check_rate_limit
from app.core.logging import logger
import json

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def ingest_document(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    collection: Optional[str] = Form(None)
):
    """
    Ingest a document from file upload, raw text, or URL.

    At least one of: file, content, or url must be provided.

    - **file**: Upload a file (PDF, TXT, MD, DOC, DOCX)
    - **content**: Raw text content
    - **url**: URL to fetch content from
    - **metadata**: JSON string with custom metadata
    - **collection**: Collection/namespace to store in
    """
    try:
        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON in metadata field"
                )

        # Handle file upload
        if file:
            result = document_service.ingest_file(
                file=file.file,
                filename=file.filename,
                metadata=doc_metadata,
                collection=collection
            )

        # Handle raw text
        elif content:
            result = document_service.ingest_text(
                content=content,
                metadata=doc_metadata,
                collection=collection
            )

        # Handle URL
        elif url:
            result = document_service.ingest_url(
                url=url,
                metadata=doc_metadata,
                collection=collection
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either file, content, or url"
            )

        return DocumentIngestResponse(
            success=True,
            document_id=result["document_id"],
            message="Document ingested successfully",
            chunks_created=result["chunks_created"],
            metadata=result["metadata"]
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest document"
        )


@router.get(
    "",
    response_model=DocumentListResponse,
    responses={401: {"model": ErrorResponse}}
)
async def list_documents(
    collection: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List all indexed documents with pagination.

    - **collection**: Filter by collection name
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Number of results to skip
    """
    try:
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000"
            )

        result = document_service.list_documents(
            collection=collection,
            limit=limit,
            offset=offset
        )

        return DocumentListResponse(**result)

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    }
)
async def delete_document(
    document_id: str,
    collection: Optional[str] = None
):
    """
    Delete a specific document by ID.

    - **document_id**: Unique document identifier
    - **collection**: Collection to delete from (optional)
    """
    try:
        result = document_service.delete_document(
            document_id=document_id,
            collection=collection
        )

        return DocumentDeleteResponse(**result)

    except ValueError as e:
        logger.error(f"Document not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )
