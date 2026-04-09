"""
Text chunking service for splitting documents into manageable pieces.
"""
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """Service for splitting text into overlapping chunks."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None,
    ):
        """
        Initialize the text chunker.

        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Number of overlapping characters between chunks
            separators: List of separator strings to try splitting on
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap

        if separators is None:
            separators = [
                "\n\n",
                "\n",
                ". ",
                ", ",
                " ",
                "",
            ]

        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_text(
        self,
        text: str,
        document_id: str,
        filename: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Args:
            text: Full text content to chunk
            document_id: Unique identifier for the document
            filename: Original filename
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text or not text.strip():
            logger.warning(f"Empty text provided for document {document_id}")
            return []

        try:
            # Split the text
            texts = self.text_splitter.split_text(text)

            # Create chunk documents with metadata
            chunks = []
            for idx, chunk_text in enumerate(texts):
                chunk_id = f"{document_id}_chunk_{idx}"

                chunk_data = {
                    "chunk_id": chunk_id,
                    "content": chunk_text,
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": idx,
                    "total_chunks": len(texts),
                    "char_count": len(chunk_text),
                }

                # Add any additional metadata
                if metadata:
                    chunk_data["metadata"] = metadata

                chunks.append(chunk_data)

            logger.info(
                f"Created {len(chunks)} chunks for document {document_id}"
            )
            return chunks

        except Exception as e:
            logger.error(f"Error chunking text for document {document_id}: {e}")
            raise

    def chunk_by_pages(
        self,
        page_texts: List[str],
        document_id: str,
        filename: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk text while respecting page boundaries when possible.

        Args:
            page_texts: List of text content from each page
            document_id: Unique identifier for the document
            filename: Original filename
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        total_pages = len(page_texts)

        for page_idx, page_text in enumerate(page_texts):
            if not page_text or not page_text.strip():
                continue

            # Split each page into chunks
            page_chunks = self.chunk_text(
                page_text,
                document_id,
                filename,
                metadata={
                    **(metadata or {}),
                    "page_number": page_idx + 1,
                    "total_pages": total_pages,
                },
            )

            # Update chunk indices to be global
            for chunk in page_chunks:
                chunk["page_number"] = page_idx + 1
                all_chunks.append(chunk)

        return all_chunks


# Singleton instance
text_chunker = TextChunker()
