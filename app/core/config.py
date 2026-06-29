"""
Configuration Management
Load and validate environment variables using Pydantic Settings.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = Field(default="Hermes AI OS")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    API_VERSION: str = Field(default="v1")
    SECRET_KEY: str = Field(..., description="Secret key for JWT")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # ============================================
    # Database Configuration
    # ============================================
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_DB: str = Field(default="hermes_ai")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    
    # Database Pool
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=30)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=3600)
    
    # ============================================
    # Redis Configuration
    # ============================================
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    # ============================================
    # LLM Configuration
    # ============================================
    DEFAULT_LLM_PROVIDER: str = Field(default="openai")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4")
    OPENAI_TEMPERATURE: float = Field(default=0.7)
    OPENAI_MAX_TOKENS: int = Field(default=2000)
    
    # Anthropic (optional)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    
    # Google (optional)
    GOOGLE_API_KEY: Optional[str] = Field(default=None)
    
    # Groq (optional)
    GROQ_API_KEY: Optional[str] = Field(default=None)
    
    # OpenRouter (optional)
    OPENROUTER_API_KEY: Optional[str] = Field(default=None)
    
    # ============================================
    # Embeddings Configuration
    # ============================================
    EMBEDDING_PROVIDER: str = Field(default="openai")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    EMBEDDING_DIMENSIONS: int = Field(default=1536)
    HF_EMBEDDING_MODEL: str = Field(default="BAAI/bge-small-en-v1.5")
    
    # ============================================
    # Vector Database
    # ============================================
    VECTOR_DB: str = Field(default="qdrant")
    
    # Qdrant
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = Field(default=None)
    QDRANT_COLLECTION_NAME: str = Field(default="hermes-knowledge")
    
    # Pinecone
    PINECONE_API_KEY: Optional[str] = Field(default=None)
    PINECONE_ENVIRONMENT: Optional[str] = Field(default="us-east-1")
    PINECONE_INDEX_NAME: Optional[str] = Field(default="hermes-knowledge")
    
    # ============================================
    # Agent Configuration
    # ============================================
    MAX_AGENT_ITERATIONS: int = Field(default=10)
    MAX_CONTEXT_LENGTH: int = Field(default=16000)
    ENABLE_MEMORY: bool = Field(default=True)
    ENABLE_RAG: bool = Field(default=True)
    ENABLE_STREAMING: bool = Field(default=True)
    
    # ============================================
    # Security
    # ============================================
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    PASSWORD_MIN_LENGTH: int = Field(default=8)
    BCRYPT_ROUNDS: int = Field(default=12)
    
    COOKIE_SECURE: bool = Field(default=False)
    COOKIE_HTTPONLY: bool = Field(default=True)
    COOKIE_SAMESITE: str = Field(default="lax")
    
    # ============================================
    # Logging
    # ============================================
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    LOG_FILE: str = Field(default="logs/app.log")
    LOG_ROTATION: str = Field(default="10MB")
    LOG_RETENTION_DAYS: int = Field(default=30)
    
    # ============================================
    # Cache
    # ============================================
    CACHE_TTL: int = Field(default=3600)
    CACHE_ENABLED: bool = Field(default=True)
    CACHE_PREFIX: str = Field(default="hermes:")
    
    # ============================================
    # CORS
    # ============================================
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000")
    ALLOW_CREDENTIALS: bool = Field(default=True)
    ALLOW_METHODS: str = Field(default="*")
    ALLOW_HEADERS: str = Field(default="*")
    
    # ============================================
    # Rate Limiting
    # ============================================
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_PER_HOUR: int = Field(default=1000)
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    
    # ============================================
    # File Upload
    # ============================================
    MAX_FILE_SIZE_MB: int = Field(default=20)
    MAX_UPLOAD_SIZE_MB: int = Field(default=20)
    ALLOWED_FILE_TYPES: str = Field(default="pdf,docx,txt,md,png,jpg,jpeg,csv,json")
    UPLOAD_DIR: str = Field(default="./uploads")
    
    # ============================================
    # Celery
    # ============================================
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")
    CELERY_TASK_ALWAYS_EAGER: bool = Field(default=False)
    CELERY_TASK_TRACK_STARTED: bool = Field(default=True)
    
    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_VOICE: bool = Field(default=True)
    ENABLE_IMAGE: bool = Field(default=True)
    ENABLE_DOCUMENT_CHAT: bool = Field(default=True)
    ENABLE_WEB_SEARCH: bool = Field(default=True)
    ENABLE_CODE_INTERPRETER: bool = Field(default=True)
    
    # ============================================
    # Monitoring
    # ============================================
    PROMETHEUS_ENABLED: bool = Field(default=True)
    PROMETHEUS_PORT: int = Field(default=9090)
    GRAFANA_ENABLED: bool = Field(default=True)
    GRAFANA_PORT: int = Field(default=3000)
    SENTRY_DSN: Optional[str] = Field(default=None)
    ENABLE_TELEMETRY: bool = Field(default=False)
    
    @validator("ALLOWED_ORIGINS")
    def parse_origins(cls, v):
        """Convert comma-separated origins to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES")
    def parse_file_types(cls, v):
        """Convert comma-separated file types to list."""
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Helper functions
def get_settings() -> Settings:
    """
    Get application settings.
    
    This function can be used as a FastAPI dependency.
    
    Returns:
        Settings: Application settings instance
    """
    return settings


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.is_development


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.is_production
