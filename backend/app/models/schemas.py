"""
Pydantic models for request/response schemas.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ProcessingStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    """Response after uploading a document."""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    status: ProcessingStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    file_size: int = Field(..., description="File size in bytes")


class DocumentInfo(BaseModel):
    """Document information."""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    status: ProcessingStatus = Field(..., description="Processing status")
    file_size: int = Field(..., description="File size in bytes")
    num_chunks: int = Field(default=0, description="Number of text chunks")
    created_at: datetime = Field(..., description="Upload timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class DocumentListResponse(BaseModel):
    """Response for listing documents."""
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    sources: Optional[List[Dict[str, Any]]] = Field(
        None, description="Source documents used for response"
    )


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    query: str = Field(..., description="User query", min_length=1)
    document_ids: Optional[List[str]] = Field(
        None, description="Filter by specific document IDs"
    )
    top_k: int = Field(default=5, description="Number of relevant chunks to retrieve")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[], description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(
        default=[], description="Source chunks used"
    )
    conversation_id: str = Field(..., description="Conversation ID for context")


class SearchRequest(BaseModel):
    """Request for semantic search."""
    query: str = Field(..., description="Search query", min_length=1)
    document_ids: Optional[List[str]] = Field(
        None, description="Filter by specific document IDs"
    )
    top_k: int = Field(default=10, description="Number of results to return")


class SearchResult(BaseModel):
    """Single search result."""
    chunk_id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="Chunk content")
    document_id: str = Field(..., description="Parent document ID")
    filename: str = Field(..., description="Parent document filename")
    score: float = Field(..., description="Relevance score")


class SearchResponse(BaseModel):
    """Response from search endpoint."""
    results: List[SearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original query")


class ProcessingStatusResponse(BaseModel):
    """Status of document processing."""
    document_id: str = Field(..., description="Document ID")
    status: ProcessingStatus = Field(..., description="Current status")
    progress: int = Field(default=0, description="Progress percentage 0-100")
    message: str = Field(..., description="Status message")
    num_chunks: int = Field(default=0, description="Chunks processed so far")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    chroma_connected: bool = Field(..., description="ChromaDB connection status")
    openai_configured: bool = Field(..., description="OpenAI API configured")
