"""
Document management API routes.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.core.config import settings
from app.models.schemas import (
    UploadResponse,
    DocumentInfo,
    DocumentListResponse,
    ProcessingStatus,
    ProcessingStatusResponse,
)
from app.services.processing_service import processing_service
from app.services.document_store import document_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Only PDF files are accepted."
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a PDF document for processing.

    The document will be processed in the background. Use the status
    endpoint to check processing progress.
    """
    # Validate file
    validate_file(file)

    # Generate unique filename to avoid conflicts
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = settings.upload_dir / unique_filename

    # Save file
    try:
        content = await file.read()

        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
            )

        # Write to disk
        with open(file_path, "wb") as f:
            f.write(content)

        file_size = len(content)
        document_id = unique_filename.split(".")[0]

        # Create document record
        doc_info = document_store.add_document(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            status=ProcessingStatus.PENDING,
        )

        # Update file path in store
        document_store.update_document(
            document_id=document_id,
            file_path=str(file_path),
        )

        # Start background processing
        background_tasks.add_task(
            processing_service.process_document,
            file_path,
            file.filename,
            file_size,
        )

        logger.info(f"Uploaded document: {file.filename} ({document_id})")

        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            status=ProcessingStatus.PENDING,
            message="Document uploaded successfully. Processing started.",
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/status/{document_id}", response_model=ProcessingStatusResponse)
async def get_document_status(document_id: str):
    """Get the processing status of a document."""
    doc_info = document_store.get_document(document_id)

    if not doc_info:
        raise HTTPException(status_code=404, detail="Document not found")

    status = doc_info.get("status", ProcessingStatus.PENDING)
    progress = 0

    if status == ProcessingStatus.COMPLETED.value:
        progress = 100
    elif status == ProcessingStatus.PROCESSING.value:
        progress = 50
    elif status == ProcessingStatus.FAILED.value:
        progress = 0

    return ProcessingStatusResponse(
        document_id=document_id,
        status=status,
        progress=progress,
        message=doc_info.get("error_message") or "Processing in progress...",
        num_chunks=doc_info.get("num_chunks", 0),
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    documents = document_store.get_all_documents()

    doc_infos = []
    for doc in documents:
        doc_infos.append(DocumentInfo(
            document_id=doc["document_id"],
            filename=doc["filename"],
            status=doc["status"],
            file_size=doc["file_size"],
            num_chunks=doc.get("num_chunks", 0),
            created_at=doc["created_at"],
            error_message=doc.get("error_message"),
        ))

    # Sort by creation date, newest first
    doc_infos.sort(key=lambda x: x.created_at, reverse=True)

    return DocumentListResponse(
        documents=doc_infos,
        total=len(doc_infos),
    )


@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get details of a specific document."""
    doc_info = document_store.get_document(document_id)

    if not doc_info:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc_info


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its associated data."""
    doc_info = document_store.get_document(document_id)

    if not doc_info:
        raise HTTPException(status_code=404, detail="Document not found")

    success = processing_service.delete_document(document_id)

    if not success:
        raise HTTPException(status_code=500, detail="Error deleting document")

    return {"message": "Document deleted successfully", "document_id": document_id}
