"""
Health check and system information API routes.
"""
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.schemas import HealthResponse
from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the API and its dependencies.

    Returns:
        HealthResponse with status of ChromaDB and OpenAI configuration
    """
    chroma_connected = False
    openai_configured = embedding_service.is_configured()

    try:
        chroma_connected = vector_store_service.is_connected()
    except Exception as e:
        logger.warning(f"ChromaDB health check failed: {e}")

    status = "healthy" if (chroma_connected and openai_configured) else "degraded"

    return HealthResponse(
        status=status,
        version="1.0.0",
        chroma_connected=chroma_connected,
        openai_configured=openai_configured,
    )


@router.get("/health/live", include_in_schema=False)
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the application is running.
    This does not check dependencies - only that the process is alive.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "alive"}
    )


@router.get("/health/ready", response_model=HealthResponse, include_in_schema=False)
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if the application is ready to serve traffic.
    Checks that ChromaDB and OpenAI are properly configured.
    """
    return await health_check()


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Document Intelligence API",
        "version": "1.0.0",
        "description": "RAG-based document intelligence platform",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "health": "/health",
            "documents": "/documents",
            "chat": "/chat",
            "search": "/chat/search",
        },
    }
