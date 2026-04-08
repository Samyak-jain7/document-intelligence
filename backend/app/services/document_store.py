"""
Document store service for managing document metadata.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
from app.models.schemas import ProcessingStatus

logger = logging.getLogger(__name__)


class DocumentStore:
    """In-memory document metadata store with JSON persistence."""

    def __init__(self):
        """Initialize the document store."""
        self._store_path = settings.base_dir / "document_store.json"
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load documents from disk."""
        if self._store_path.exists():
            try:
                with open(self._store_path, "r") as f:
                    data = json.load(f)
                    self._documents = {
                        k: v for k, v in data.items()
                    }
                logger.info(f"Loaded {len(self._documents)} documents from store")
            except Exception as e:
                logger.error(f"Error loading document store: {e}")
                self._documents = {}

    def _save(self) -> None:
        """Save documents to disk."""
        try:
            with open(self._store_path, "w") as f:
                json.dump(self._documents, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving document store: {e}")

    def add_document(
        self,
        document_id: str,
        filename: str,
        file_size: int,
        status: ProcessingStatus = ProcessingStatus.PENDING,
    ) -> Dict[str, Any]:
        """
        Add a new document to the store.

        Args:
            document_id: Unique document ID
            filename: Original filename
            file_size: File size in bytes
            status: Initial processing status

        Returns:
            Document info dictionary
        """
        now = datetime.utcnow()
        doc_info = {
            "document_id": document_id,
            "filename": filename,
            "file_size": file_size,
            "status": status.value if isinstance(status, ProcessingStatus) else status,
            "num_chunks": 0,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "error_message": None,
            "file_path": str(settings.upload_dir / filename),
        }

        self._documents[document_id] = doc_info
        self._save()

        logger.info(f"Added document {document_id} to store")
        return doc_info

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document info by ID.

        Args:
            document_id: Document ID

        Returns:
            Document info or None
        """
        return self._documents.get(document_id)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents.

        Returns:
            List of document info dictionaries
        """
        return list(self._documents.values())

    def update_document(
        self,
        document_id: str,
        **updates,
    ) -> Optional[Dict[str, Any]]:
        """
        Update document fields.

        Args:
            document_id: Document ID
            **updates: Fields to update

        Returns:
            Updated document info or None
        """
        if document_id not in self._documents:
            return None

        updates["updated_at"] = datetime.utcnow().isoformat()

        # Handle status enum
        if "status" in updates and isinstance(updates["status"], ProcessingStatus):
            updates["status"] = updates["status"].value

        self._documents[document_id].update(updates)
        self._save()

        logger.info(f"Updated document {document_id}: {list(updates.keys())}")
        return self._documents[document_id]

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the store.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if document_id in self._documents:
            del self._documents[document_id]
            self._save()
            logger.info(f"Deleted document {document_id}")
            return True
        return False

    def get_documents_by_status(
        self,
        status: ProcessingStatus,
    ) -> List[Dict[str, Any]]:
        """
        Get all documents with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of matching documents
        """
        status_value = status.value if isinstance(status, ProcessingStatus) else status
        return [
            doc for doc in self._documents.values()
            if doc["status"] == status_value
        ]

    def exists(self, document_id: str) -> bool:
        """Check if a document exists."""
        return document_id in self._documents


# Singleton instance
document_store = DocumentStore()
