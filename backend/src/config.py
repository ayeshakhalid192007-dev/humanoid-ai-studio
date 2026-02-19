"""
Configuration management for RAG Chatbot backend.

Loads and validates environment variables using Pydantic Settings.
Provides centralized access to API keys and service URLs.

Author: Physical AI Platform Team
Date: 2026-02-09
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================================
# Configuration Class
# ============================================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables using Pydantic BaseSettings.

    Required variables:
    - OPENAI_API_KEY: OpenAI API key for embeddings and chat
    - QDRANT_URL: Qdrant Cloud URL (e.g., https://xyz.cloud.qdrant.io)
    - QDRANT_API_KEY: Qdrant API key
    - NEON_DATABASE_URL: Neon Postgres connection string

    Optional variables:
    - BACKEND_CORS_ORIGINS: Comma-separated list of allowed CORS origins
    - ENV: Environment name (development, staging, production)
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ========================================================================
    # OpenAI Configuration
    # ========================================================================

    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model (1536 dimensions)"
    )
    OPENAI_CHAT_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI chat model (FR-041)"
    )
    OPENAI_MAX_TOKENS: int = Field(
        default=2000,
        ge=100,
        le=4000,
        description="Max response token length"
    )
    OPENAI_TEMPERATURE: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Temperature for factual answers"
    )

    # ========================================================================
    # Qdrant Configuration
    # ========================================================================

    QDRANT_URL: str = Field(..., description="Qdrant Cloud URL")
    QDRANT_API_KEY: str = Field(..., description="Qdrant API key")
    QDRANT_COLLECTION_NAME: str = Field(
        default="curriculum",
        description="Qdrant collection name"
    )
    QDRANT_VECTOR_SIZE: int = Field(
        default=1536,
        description="Vector size (must match embedding model)"
    )
    QDRANT_SEARCH_LIMIT: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Top-K chunks to retrieve"
    )
    QDRANT_SCORE_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Cosine similarity threshold (FR-039)"
    )

    # ========================================================================
    # Neon Postgres Configuration
    # ========================================================================

    NEON_DATABASE_URL: str = Field(..., description="Neon Postgres connection string")
    NEON_POOL_MIN_SIZE: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Minimum connection pool size"
    )
    NEON_POOL_MAX_SIZE: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Maximum connection pool size"
    )
    NEON_COMMAND_TIMEOUT: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Query timeout in seconds"
    )

    # ========================================================================
    # Rate Limiting Configuration
    # ========================================================================

    RATE_LIMIT_MAX_QUERIES: int = Field(
        default=20,
        ge=1,
        description="Max queries per hour (FR-048)"
    )
    RATE_LIMIT_WINDOW_HOURS: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Sliding window duration"
    )

    # ========================================================================
    # AI Generation Rate Limiting (Personalization & Translation)
    # ========================================================================

    PERSONALIZE_RATE_LIMIT_MAX: int = Field(
        default=10,
        ge=1,
        description="Max personalization requests per hour per user"
    )
    TRANSLATE_RATE_LIMIT_MAX: int = Field(
        default=20,
        ge=1,
        description="Max translation requests per hour per session/IP"
    )
    AI_RATE_LIMIT_WINDOW_HOURS: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Sliding window duration for AI rate limits"
    )

    # ========================================================================
    # CORS Configuration
    # ========================================================================

    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # ========================================================================
    # Application Configuration
    # ========================================================================

    ENV: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    MOCK_MODE: bool = Field(
        default=False,
        description="Use mock services instead of real APIs"
    )

    # ========================================================================
    # RAG Pipeline Configuration
    # ========================================================================

    MAX_CONTEXT_TOKENS: int = Field(
        default=8000,
        ge=1000,
        le=100000,
        description="Context window limit (FR-040)"
    )
    MAX_QUERY_LENGTH: int = Field(
        default=500,
        ge=1,
        le=2000,
        description="Max characters in user query"
    )
    MIN_QUERY_LENGTH: int = Field(
        default=1,
        ge=1,
        description="Min characters in user query"
    )
    MAX_RETRIEVED_CHUNKS: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Max chunks in response"
    )
    CHUNK_PREVIEW_LENGTH: int = Field(
        default=200,
        ge=50,
        le=1000,
        description="Max chars in chunk preview"
    )

    # ========================================================================
    # Better Auth Configuration
    # ========================================================================

    BETTER_AUTH_URL: str = Field(
        default="http://localhost:3002",
        description="Better Auth server URL for session validation"
    )

    # ========================================================================
    # Session Configuration
    # ========================================================================

    SESSION_STORAGE_MAX_MESSAGES: int = Field(
        default=500,
        ge=10,
        le=10000,
        description="Max messages in sessionStorage (FR-055)"
    )

    # ========================================================================
    # Cleanup Configuration
    # ========================================================================

    CONVERSATION_RETENTION_DAYS: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Conversation retention period (FR-019, FR-047)"
    )
    RATE_LIMIT_CLEANUP_HOURS: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Delete rate limit records older than N hours"
    )

    # ========================================================================
    # Validators
    # ========================================================================

    @field_validator("QDRANT_URL")
    @classmethod
    def validate_qdrant_url(cls, v: str) -> str:
        """Validate Qdrant URL starts with http/https."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("QDRANT_URL must start with http:// or https://")
        return v

    @field_validator("NEON_DATABASE_URL")
    @classmethod
    def validate_neon_url(cls, v: str) -> str:
        """Validate Neon database URL starts with postgres."""
        if not v.startswith(("postgres://", "postgresql://")):
            raise ValueError("NEON_DATABASE_URL must start with postgres:// or postgresql://")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

    @field_validator("ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        """Validate environment name."""
        valid_envs = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"ENV must be one of {valid_envs}")
        return v_lower

    @property
    def DEBUG(self) -> bool:
        """Check if running in development mode."""
        return self.ENV == "development"


# ============================================================================
# Settings Instance (Singleton)
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance (singleton pattern).

    Returns:
        Settings: Validated configuration object

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return Settings()


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """Test configuration loading and validation."""
    from pydantic import ValidationError

    print("=" * 70)
    print("Configuration Validation")
    print("=" * 70)

    try:
        settings = get_settings()

        print("\n✅ Configuration loaded successfully\n")
        print(f"Environment: {settings.ENV}")
        print(f"Debug mode: {settings.DEBUG}")
        print(f"Log level: {settings.LOG_LEVEL}")
        print(f"\nOpenAI:")
        print(f"  - API key: {'*' * 20}{settings.OPENAI_API_KEY[-8:]}")
        print(f"  - Embedding model: {settings.OPENAI_EMBEDDING_MODEL}")
        print(f"  - Chat model: {settings.OPENAI_CHAT_MODEL}")
        print(f"\nQdrant:")
        print(f"  - URL: {settings.QDRANT_URL}")
        print(f"  - Collection: {settings.QDRANT_COLLECTION_NAME}")
        print(f"  - Score threshold: {settings.QDRANT_SCORE_THRESHOLD}")
        print(f"\nNeon Postgres:")
        print(f"  - URL: {settings.NEON_DATABASE_URL[:30]}...")
        print(f"  - Pool size: {settings.NEON_POOL_MIN_SIZE}-{settings.NEON_POOL_MAX_SIZE}")
        print(f"\nRate Limiting:")
        print(f"  - Max queries: {settings.RATE_LIMIT_MAX_QUERIES}/hour")
        print(f"\nCORS Origins:")
        print(f"  - {settings.BACKEND_CORS_ORIGINS}")

    except ValidationError as e:
        print(f"\n❌ Configuration validation failed:")
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            print(f"  - {field}: {error['msg']}")
        exit(1)
