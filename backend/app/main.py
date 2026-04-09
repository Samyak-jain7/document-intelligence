"""
Document Intelligence API - Main Application

A FastAPI-based RAG system for document upload, processing, and chat.
"""
import logging
import sys
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import documents_router, chat_router, health_router


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "environment"):
            log_data["environment"] = record.environment
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# Configure structured logging
_log_handler = logging.StreamHandler(sys.stdout)
_log_handler.setFormatter(JSONFormatter())
logger = logging.getLogger("document_intelligence")
logger.setLevel(logging.INFO if settings.environment == "production" else logging.DEBUG)
logger.addHandler(_log_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(
        "Starting Document Intelligence API",
        extra={
            "environment": settings.environment,
            "upload_dir": str(settings.upload_dir),
            "chroma_db_path": str(settings.chroma_db_path),
            "host": settings.host,
            "port": settings.port,
        }
    )

    yield

    # Shutdown
    logger.info("Shutting down Document Intelligence API")


# Configure FastAPI app
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
origins = settings.cors_origins
if settings.frontend_url and settings.frontend_url not in origins:
    origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True if origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their responses."""
    request_id = request.headers.get("X-Request-ID", str(id(request)))
    start_time = time.time()

    logger.info(
        f"Incoming request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
        }
    )

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        f"Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "request_id": request_id,
        }
    )
    return response


# API Key Middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Validate API key for protected endpoints."""
    # Skip auth for health, docs, and root
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc", "/"]:
        return await call_next(request)

    if settings.app_api_key:
        api_key = request.headers.get("X-API-Key")
        if api_key != settings.app_api_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API Key"}
            )

    return await call_next(request)

# Include routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(chat_router)


# Root endpoint - liveness probe for Kubernetes/load balancers
@app.get("/", tags=["health"])
async def root():
    """Root endpoint - returns API info and acts as liveness probe."""
    return {
        "name": "Document Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler - always returns JSONResponse."""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__,
        },
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_type": type(exc).__name__,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
