"""
Vector store service using ChromaDB for document retrieval.
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document as LangchainDocument
from langchain_community.vectorstores import Chroma
from app.core.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing the ChromaDB vector store."""

    def __init__(self):
        """Initialize the vector store service."""
        self._client: Optional[chromadb.PersistentClient] = None
        self._vectorstore: Optional[Chroma] = None

    @property
    def client(self) -> chromadb.PersistentClient:
        """Get or create the ChromaDB client."""
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=str(settings.chroma_db_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            logger.info(
                f"Initialized ChromaDB client at: {settings.chroma_db_path}"
            )
        return self._client

    @property
    def vectorstore(self) -> Chroma:
        """Get or create the LangChain Chroma vectorstore."""
        if self._vectorstore is None:
            if not embedding_service.is_configured():
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Cannot initialize vector store."
                )

            # Create the vector store with the embedding function
            self._vectorstore = Chroma(
                client=self.client,
                collection_name=settings.chroma_collection_name,
                embedding_function=embedding_service.embeddings,
            )
            logger.info(
                f"Initialized Chroma vector store with collection: "
                f"{settings.chroma_collection_name}"
            )
        return self._vectorstore

    def is_connected(self) -> bool:
        """Check if the vector store is properly connected."""
        try:
            # Try to access the collection
            self.client.get_collection(settings.chroma_collection_name)
            return True
        except Exception as e:
            logger.warning(f"Vector store connection check failed: {e}")
            return False

    def add_documents(
        self,
        documents: List[LangchainDocument],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of LangChain documents to add
            ids: Optional list of IDs (generated if not provided)

        Returns:
            List of document IDs
        """
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [doc.metadata.get("chunk_id", f"doc_{i}")
                       for i, doc in enumerate(documents)]

            # Add to vector store
            self.vectorstore.add_documents(documents, ids=ids)
            logger.info(f"Added {len(documents)} documents to vector store")

            return ids

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[LangchainDocument]:
        """
        Perform similarity search on the vector store.

        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant documents
        """
        try:
            docs = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter_dict,
            )
            logger.debug(f"Found {len(docs)} similar documents for query")
            return docs

        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[LangchainDocument, float]]:
        """
        Perform similarity search with relevance scores.

        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict,
            )
            logger.debug(f"Found {len(results)} scored results for query")
            return results

        except Exception as e:
            logger.error(f"Error performing scored similarity search: {e}")
            raise

    def get_by_document_id(
        self,
        document_id: str,
    ) -> List[LangchainDocument]:
        """
        Get all chunks for a specific document.

        Args:
            document_id: Document ID to filter by

        Returns:
            List of documents from that document
        """
        try:
            docs = self.vectorstore.get(
                where={"document_id": document_id},
            )
            return docs

        except Exception as e:
            logger.error(f"Error getting documents by ID: {e}")
            raise

    def delete_by_document_id(self, document_id: str) -> None:
        """
        Delete all chunks for a specific document.

        Args:
            document_id: Document ID to delete
        """
        try:
            self.vectorstore.delete(
                where={"document_id": document_id},
            )
            logger.info(f"Deleted all chunks for document: {document_id}")

        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection metadata
        """
        try:
            collection = self.client.get_collection(
                settings.chroma_collection_name
            )
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata,
            }

        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}


# Singleton instance
vector_store_service = VectorStoreService()
