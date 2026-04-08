"""
LLM service for generating answers using retrieved context.
"""
import logging
from typing import List, Dict, Any, Optional, Callable
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import Document, SystemMessage, HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.combine_documents import create_strict_rag_chain
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based question answering."""

    def __init__(self):
        """Initialize the LLM service."""
        self._llm: Optional[ChatOpenAI] = None
        self._chain: Optional[ConversationalRetrievalChain] = None

    @property
    def llm(self) -> ChatOpenAI:
        """Get or create the LLM client."""
        if self._llm is None:
            if not settings.openai_api_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Please set OPENAI_API_KEY in your environment."
                )

            self._llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=0.7,
                max_tokens=2000,
            )
            logger.info(f"Initialized LLM with model: {settings.openai_model}")

        return self._llm

    def is_configured(self) -> bool:
        """Check if the LLM service is properly configured."""
        return bool(settings.openai_api_key)

    def generate_answer(
        self,
        query: str,
        context_docs: List[Document],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an answer using the retrieved context.

        Args:
            query: User's question
            context_docs: Retrieved document chunks to use as context
            conversation_history: Optional previous conversation messages

        Returns:
            Dictionary with answer and source information
        """
        if not context_docs:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": [],
            }

        try:
            # Build the context string from retrieved documents
            context_parts = []
            for i, doc in enumerate(context_docs, 1):
                source_info = doc.metadata.get("filename", "Unknown")
                if "page_number" in doc.metadata:
                    source_info += f" (Page {doc.metadata['page_number']})"
                context_parts.append(f"[{i}] ({source_info}):\n{doc.page_content}")

            context_text = "\n\n".join(context_parts)

            # Build conversation history string if provided
            history_text = ""
            if conversation_history:
                history_lines = []
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    history_lines.append(f"{role.capitalize()}: {content}")
                history_text = "Previous conversation:\n" + "\n".join(history_lines) + "\n\n"

            # Create the prompt
            system_prompt = """You are a helpful AI assistant that answers questions based on the provided document excerpts.

Your task:
1. Read the provided context from documents carefully
2. Answer the user's question based ONLY on the information in the context
3. If the context contains relevant information, provide a detailed and accurate answer
4. If the context doesn't contain enough information, say so clearly
5. Cite your sources by referencing the document numbers (e.g., [1], [2])

Be thorough but concise. Don't make up information that isn't in the context."""

            human_prompt = f"""{history_text}Context from documents:
{context_text}

User question: {query}

Please answer based on the context provided."""

            # Generate response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]

            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)

            # Format sources
            sources = []
            for doc in context_docs:
                source = {
                    "chunk_id": doc.metadata.get("chunk_id", ""),
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "document_id": doc.metadata.get("document_id", ""),
                    "filename": doc.metadata.get("filename", ""),
                }
                if "page_number" in doc.metadata:
                    source["page_number"] = doc.metadata["page_number"]
                sources.append(source)

            return {
                "answer": answer,
                "sources": sources,
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def generate_summary(
        self,
        text: str,
        max_words: int = 200,
    ) -> str:
        """
        Generate a summary of the given text.

        Args:
            text: Text to summarize
            max_words: Maximum words in summary

        Returns:
            Summary string
        """
        try:
            prompt = f"""Please provide a concise summary of the following text in no more than {max_words} words:

{text}

Summary:"""

            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise


# Singleton instance
llm_service = LLMService()
