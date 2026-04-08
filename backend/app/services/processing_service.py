"""
Main processing service that orchestrates document processing.
"""
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import ProcessingStatus
from app.services.pdf_processor import pdf_processor
from app.services.text_chunker import text_chunker
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store_service
from app.services.document_store import document_store

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for processing uploaded documents."""

    def __init__(self):
        """Initialize the processing service."""
        pass

    async def process_document(
        self,
        file_path: Path,
        filename: str,
        file_size: int,
    ) -> Dict[str, Any]:
        """
        Process a PDF document through the entire pipeline.

        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            file_size: File size in bytes

        Returns:
            Processing result dictionary
        """
        document_id = str(uuid.uuid4())

        try:
            # Step 1: Create document record
            document_store.add_document(
                document_id=document_id,
                filename=filename,
                file_size=file_size,
                status=ProcessingStatus.PROCESSING,
            )

            logger.info(f"Starting processing for document: {document_id}")

            # Step 2: Validate PDF
            validation = pdf_processor.validate_pdf(file_path)
            if not validation["valid"]:
                raise ValueError(f"Invalid PDF: {validation.get('error', 'Unknown error')}")

            # Step 3: Extract text
            logger.info(f"Extracting text from: {filename}")
            text = pdf_processor.extract_text(file_path)

            if not text or len(text.strip()) < 50:
                raise ValueError("Extracted text is too short or empty")

            logger.info(f"Extracted {len(text)} characters from {filename}")

            # Step 4: Chunk text
            logger.info(f"Chunking text into segments...")
            chunks = text_chunker.chunk_text(
                text=text,
                document_id=document_id,
                filename=filename,
                metadata={
                    "page_count": validation["page_count"],
                    "file_size": file_size,
                },
            )

            if not chunks:
                raise ValueError("No chunks created from document")

            logger.info(f"Created {len(chunks)} chunks")

            # Step 5: Create LangChain documents
            langchain_docs = embedding_service.create_langchain_documents(chunks)

            # Step 6: Generate embeddings and store
            logger.info(f"Generating embeddings and storing in vector DB...")
            chunk_ids = vector_store_service.add_documents(langchain_docs)

            # Step 7: Update document record
            document_store.update_document(
                document_id=document_id,
                status=ProcessingStatus.COMPLETED,
                num_chunks=len(chunks),
            )

            logger.info(f"Successfully processed document: {document_id}")

            return {
                "document_id": document_id,
                "filename": filename,
                "status": ProcessingStatus.COMPLETED.value,
                "num_chunks": len(chunks),
                "char_count": len(text),
                "page_count": validation["page_count"],
            }

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")

            document_store.update_document(
                document_id=document_id,
                status=ProcessingStatus.FAILED,
                error_message=str(e),
            )

            raise

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks.

        Args:
            document_id: Document ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            # Delete from vector store
            vector_store_service.delete_by_document_id(document_id)

            # Delete from document store
            doc_info = document_store.get_document(document_id)
            if doc_info:
                # Delete the uploaded file
                file_path = Path(doc_info.get("file_path", ""))
                if file_path.exists():
                    file_path.unlink()

            document_store.delete_document(document_id)

            logger.info(f"Deleted document: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    def get_document_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the processing status of a document.

        Args:
            document_id: Document ID

        Returns:
            Status info or None
        """
        return document_store.get_document(document_id)


# Singleton instance
processing_service = ProcessingService()
