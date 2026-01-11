"""
Core configuration module for RAG microservice.
Loads and validates all environment variables.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = "RAG Microservice"
    APP_ENV: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # API Security
    API_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost"

    # Vector Database Configuration
    VECTOR_DB_TYPE: str = "chromadb"
    CHROMADB_PATH: str = "./storage/chromadb"
    CHROMADB_COLLECTION_NAME: str = "documents"

    # Document Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "pdf,txt,md,doc,docx"

    # RAG Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    ENABLE_QUERY_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 3600

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # Embedding Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"  # openai, anthropic, or ollama

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Anthropic
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # Ollama (Local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Parse ALLOWED_FILE_TYPES string into list."""
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def validate_llm_config(self) -> None:
        """Validate that required LLM provider credentials are present."""
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        elif self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'anthropic'")
        elif self.LLM_PROVIDER not in ["openai", "anthropic", "ollama"]:
            raise ValueError(f"Invalid LLM_PROVIDER: {self.LLM_PROVIDER}")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    settings = Settings()
    settings.validate_llm_config()
    return settings
