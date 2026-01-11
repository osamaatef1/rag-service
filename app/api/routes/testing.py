"""
Testing routes for quick API testing.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/query", tags=["Testing"])


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify the API is working."""
    return {
        "success": True,
        "message": "Test endpoint is working!",
        "endpoint": "/api/v1/query/test"
    }
