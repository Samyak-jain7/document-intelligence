"""
Health check and system information API routes.
"""
import logging
from fastapi import APIRouter
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


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Document Intelligence API",
        "version": "1.0.0",
        "description": "RAG-based document intelligence platform",
        "endpoints": {
            "health": "/health",
            "documents": "/documents",
            "chat": "/chat",
            "search": "/chat/search",
        },
    }
