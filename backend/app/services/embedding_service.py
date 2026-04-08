"""
Embedding service for generating vector representations of text.
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document as LangchainDocument
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        """Initialize the embedding service."""
        self._embeddings: Optional[OpenAIEmbeddings] = None

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """Get or create the embeddings client."""
        if self._embeddings is None:
            if not settings.openai_api_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Please set OPENAI_API_KEY in your environment."
                )

            self._embeddings = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model=settings.openai_embedding_model,
            )
            logger.info(
                f"Initialized embeddings with model: {settings.openai_embedding_model}"
            )

        return self._embeddings

    def is_configured(self) -> bool:
        """Check if the embedding service is properly configured."""
        return bool(settings.openai_api_key)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def create_langchain_documents(
        self,
        chunks: List[Dict[str, Any]],
    ) -> List[LangchainDocument]:
        """
        Convert internal chunk format to LangChain documents.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of LangChain Document objects
        """
        documents = []

        for chunk in chunks:
            # Build metadata (exclude content)
            metadata = {
                "chunk_id": chunk.get("chunk_id", ""),
                "document_id": chunk.get("document_id", ""),
                "filename": chunk.get("filename", ""),
                "chunk_index": chunk.get("chunk_index", 0),
                "total_chunks": chunk.get("total_chunks", 1),
            }

            # Add optional metadata
            if "page_number" in chunk:
                metadata["page_number"] = chunk["page_number"]
            if "metadata" in chunk:
                metadata.update(chunk["metadata"])

            doc = LangchainDocument(
                page_content=chunk.get("content", ""),
                metadata=metadata,
            )
            documents.append(doc)

        return documents


# Singleton instance
embedding_service = EmbeddingService()
