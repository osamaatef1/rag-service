"""
API routes for health checks and system status.
"""
import time
from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthResponse
from app.services.vector_store import vector_store
from app.core.logging import logger

router = APIRouter(tags=["Health"])

# Store start time
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status.

    Returns system status including:
    - Overall health status
    - Service version
    - Uptime
    - Vector database connectivity
    - Document and chunk counts
    """
    try:
        # Check vector database connectivity
        stats = vector_store.get_stats()
        vector_db_status = "connected"

        uptime = time.time() - start_time

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime_seconds=uptime,
            vector_db_status=vector_db_status,
            total_documents=stats.get("total_documents", 0),
            total_chunks=stats.get("total_chunks", 0)
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            uptime_seconds=time.time() - start_time,
            vector_db_status="disconnected",
            total_documents=0,
            total_chunks=0
        )
