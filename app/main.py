"""
FastAPI main application entry point.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import time

from app.core.config import get_settings
from app.core.logging import logger
from app.api.routes import documents, query, health, testing

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="RAG (Retrieval-Augmented Generation) Microservice API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred" if not settings.DEBUG else str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(testing.router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Vector DB: {settings.VECTOR_DB_TYPE}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("Shutting down application")
