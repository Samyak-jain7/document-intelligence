"""
Chat and Q&A API routes.
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.vector_store import vector_store_service
from app.services.llm_service import llm_service
from app.services.document_store import document_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with your documents using RAG (Retrieval-Augmented Generation).

    The system will:
    1. Retrieve relevant chunks from your documents
    2. Generate an answer based on the retrieved context
    3. Cite the sources used in the answer
    """
    try:
        # Check if LLM is configured
        if not llm_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="LLM service not configured. Please set OPENAI_API_KEY."
            )

        # Build filter if specific documents are requested
        filter_dict = None
        if request.document_ids:
            filter_dict = {"document_id": {"$in": request.document_ids}}

        # Retrieve relevant documents
        retrieved_docs = vector_store_service.similarity_search(
            query=request.query,
            k=request.top_k,
            filter_dict=filter_dict,
        )

        if not retrieved_docs:
            return ChatResponse(
                answer="I couldn't find any relevant information in the documents to answer your question. Try rephrasing or uploading more documents.",
                sources=[],
                conversation_id=str(uuid.uuid4()),
            )

        # Convert conversation history to proper format
        history = []
        if request.conversation_history:
            for msg in request.conversation_history:
                if msg.role == "user":
                    history.append({"role": "user", "content": msg.content})
                elif msg.role == "assistant":
                    history.append({"role": "assistant", "content": msg.content})

        # Generate answer
        result = llm_service.generate_answer(
            query=request.query,
            context_docs=retrieved_docs,
            conversation_history=history if history else None,
        )

        conversation_id = str(uuid.uuid4())

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=conversation_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Perform semantic search across your documents.

    Returns the most relevant chunks ranked by similarity score.
    """
    try:
        # Build filter if specific documents are requested
        filter_dict = None
        if request.document_ids:
            filter_dict = {"document_id": {"$in": request.document_ids}}

        # Perform search with scores
        results_with_scores = vector_store_service.similarity_search_with_score(
            query=request.query,
            k=request.top_k,
            filter_dict=filter_dict,
        )

        # Format results
        search_results = []
        for doc, score in results_with_scores:
            search_results.append(SearchResult(
                chunk_id=doc.metadata.get("chunk_id", ""),
                content=doc.page_content,
                document_id=doc.metadata.get("document_id", ""),
                filename=doc.metadata.get("filename", ""),
                score=round(score, 4),
            ))

        return SearchResponse(
            results=search_results,
            query=request.query,
        )

    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.get("/conversations/{document_id}")
async def get_document_conversations(document_id: str):
    """
    Get conversation history for a specific document.
    Note: This is a placeholder - in production, you'd want persistent storage.
    """
    doc_info = document_store.get_document(document_id)

    if not doc_info:
        raise HTTPException(status_code=404, detail="Document not found")

    # Placeholder - return empty list
    # In production, implement conversation storage
    return {
        "document_id": document_id,
        "conversations": [],
    }
