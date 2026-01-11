"""
API routes for RAG queries.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import QueryRequest, QueryResponse, ErrorResponse
from app.services.rag_service import rag_service
# Simplified: Removed authentication and rate limiting for easier understanding
# from app.core.security import verify_api_key
# from app.api.dependencies.rate_limit import check_rate_limit
from app.core.logging import logger

router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def query(request: QueryRequest):
    """
    Submit a question and get an AI-generated answer based on indexed documents.

    The RAG system will:
    1. Search for relevant documents in the vector database
    2. Use retrieved context to generate an accurate answer
    3. Return the answer with source documents

    - **query**: The question or query text
    - **collection**: Optional collection to search in
    - **top_k**: Number of relevant documents to retrieve (1-20)
    - **metadata_filter**: Filter documents by metadata
    - **include_sources**: Include source documents in response
    """
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        result = rag_service.query(
            query=request.query,
            collection=request.collection,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
            include_sources=request.include_sources
        )

        return QueryResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )
