"""
Core configuration for the Document Intelligence API.
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = "development"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
    chroma_db_path: Path = Path(os.getenv("CHROMA_DB_PATH", "/app/chromadb"))

    # File Upload
    max_file_size_mb: int = 50

    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]

    # ChromaDB Collection
    chroma_collection_name: str = "document_chunks"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure directories exist
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_db_path.mkdir(parents=True, exist_ok=True)
