"""
Core configuration for the Document Intelligence API.
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""

    # Environment
    environment: str = Field(default="development", description="Environment mode")
    debug: bool = Field(default=False, description="Debug mode")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            return "development"
        return v.lower()

    @field_validator("debug")
    @classmethod
    def validate_debug(cls, v: bool) -> bool:
        return v if isinstance(v, bool) else str(v).lower() in {"true", "1", "yes"}

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")

    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    upload_dir: Path = Field(default=Path("/app/uploads"), description="Upload storage path")
    chroma_db_path: Path = Field(default=Path("/app/chromadb"), description="ChromaDB data path")

    @property
    def resolved_upload_dir(self) -> Path:
        return Path(os.getenv("UPLOAD_DIR", str(self.upload_dir)))

    @property
    def resolved_chroma_db_path(self) -> Path:
        return Path(os.getenv("CHROMA_DB_PATH", str(self.chroma_db_path)))

    # File Upload
    max_file_size_mb: int = Field(default=50, ge=1, le=500, description="Max upload size (MB)")
    max_file_size_bytes: int = Field(default=50 * 1024 * 1024)

    @field_validator("max_file_size_bytes", mode="before")
    @classmethod
    def compute_max_file_size_bytes(cls, v: int, info) -> int:
        mb = info.data.get("max_file_size_mb", 50)
        return mb * 1024 * 1024

    # LLM Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="GPT model for chat")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")

    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        return v.strip()

    # Chunking Configuration
    chunk_size: int = Field(default=1000, ge=100, le=4000, description="Text chunk size")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Chunk overlap")

    # ChromaDB Collection
    chroma_collection_name: str = Field(default="document_chunks", description="ChromaDB collection name")

    # CORS
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend URL")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
        description="CORS allowed origins"
    )

    # Security
    app_api_key: Optional[str] = Field(default=None, description="Optional API key for authentication")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()

# Override paths from environment if provided
settings.upload_dir = settings.resolved_upload_dir
settings.chroma_db_path = settings.resolved_chroma_db_path

# Ensure directories exist
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_db_path.mkdir(parents=True, exist_ok=True)
