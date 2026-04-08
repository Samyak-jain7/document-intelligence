"""
Document Intelligence API - Main Application

A FastAPI-based RAG system for document upload, processing, and chat.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import documents_router, chat_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Document Intelligence API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"ChromaDB path: {settings.chroma_db_path}")

    yield

    # Shutdown
    logger.info("Shutting down Document Intelligence API...")


# Create FastAPI app
app = FastAPI(
    title="Document Intelligence API",
    description="""
    A RAG-based document intelligence platform for uploading PDFs,
    extracting text, and chatting with your documents.

    ## Features

    - **PDF Upload**: Upload and process PDF documents
    - **Text Extraction**: Extract text and tables from PDFs
    - **Semantic Search**: Find relevant content using embeddings
    - **RAG Chat**: Ask questions and get answers with citations

    ## Authentication

    Set your OpenAI API key via the `OPENAI_API_KEY` environment variable.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(chat_router)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "detail": "An unexpected error occurred",
        "status_code": 500,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
