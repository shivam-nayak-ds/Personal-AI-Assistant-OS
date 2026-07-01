import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration — all settings from .env"""

    # ─────────────────────────────────────
    # Application
    # ─────────────────────────────────────
    APP_NAME: str = "Hermes AI OS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # ─────────────────────────────────────
    # Database (PostgreSQL)
    # ─────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hermes_ai"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://postgres:password@localhost:5432/hermes_ai"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # ─────────────────────────────────────
    # Redis
    # ─────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    # ─────────────────────────────────────
    # Authentication (JWT)
    # ─────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "hermes-super-secret-key-change-in-production-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TOKEN_REFRESH_URL: str = "/api/v1/auth/refresh"

    # ─────────────────────────────────────
    # LLM Providers
    # ─────────────────────────────────────

    # Groq — ultra-fast chat + Whisper STT (primary)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"       # quick tasks
    GROQ_MODEL_SMART: str = "llama-3.1-70b-versatile"   # complex reasoning
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"

    # OpenRouter — access Claude, GPT-4o via one API
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL_CRITIQUE: str = "anthropic/claude-3.5-sonnet"   # self-critique
    OPENROUTER_MODEL_COMPLEX: str = "openai/gpt-4o"                   # escalation

    # Google Gemini — embeddings + fallback LLM (free)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_MODEL: str = "gemini-1.5-flash"               # fast fallback

    # OpenAI (optional — for TTS voice)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "alloy"

    # Anthropic (direct — optional fallback)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ─────────────────────────────────────
    # LLM Routing Strategy
    # ─────────────────────────────────────
    # Which provider to use for each task
    LLM_CHAT_PROVIDER: str = "groq"           # groq / openrouter / gemini
    LLM_CRITIQUE_PROVIDER: str = "openrouter" # best for self-critique
    LLM_EMBEDDING_PROVIDER: str = "gemini"    # free embeddings
    LLM_ESCALATION_PROVIDER: str = "openrouter"
    LLM_CONFIDENCE_THRESHOLD: float = 0.5    # below this → escalate

    # ─────────────────────────────────────
    # Vector Database (Pinecone)
    # ─────────────────────────────────────
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "hermes-vectors")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_DIMENSION: int = 768  # Gemini embedding-001 dimensions

    # ─────────────────────────────────────
    # RAG Pipeline
    # ─────────────────────────────────────
    RAG_CHUNK_SIZE: int = 512        # tokens per chunk
    RAG_CHUNK_OVERLAP: int = 50      # overlap between chunks
    RAG_TOP_K: int = 10              # candidates before reranking
    RAG_FINAL_K: int = 3             # chunks sent to LLM after rerank
    RAG_BM25_WEIGHT: float = 0.4    # hybrid: 0.4×BM25 + 0.6×Vector
    RAG_VECTOR_WEIGHT: float = 0.6

    # ─────────────────────────────────────
    # Memory System
    # ─────────────────────────────────────
    MEMORY_MAX_PER_USER: int = 500           # max memories stored
    MEMORY_CONTEXT_LIMIT: int = 5            # injected into each prompt
    MEMORY_CLEANUP_THRESHOLD: float = 0.2   # delete below this score
    MEMORY_CLEANUP_DAYS: int = 30            # age before cleanup check

    # ─────────────────────────────────────
    # File Upload
    # ─────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_FILE_TYPES: str = "pdf,doc,docx,txt,md"

    # ─────────────────────────────────────
    # CORS
    # ─────────────────────────────────────
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # ─────────────────────────────────────
    # Pagination
    # ─────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ─────────────────────────────────────
    # Rate Limiting
    # ─────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_CHAT_PER_MIN: int = 20      # expensive LLM calls
    RATE_LIMIT_VOICE_PER_MIN: int = 5      # very expensive
    RATE_LIMIT_GENERAL_PER_MIN: int = 100  # general API

    # ─────────────────────────────────────
    # Observability
    # ─────────────────────────────────────
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    OTEL_SERVICE_NAME: str = "hermes-ai"
    OTEL_EXPORTER_ENDPOINT: str = "http://localhost:4317"

    # ─────────────────────────────────────
    # Guardrails
    # ─────────────────────────────────────
    GUARDRAILS_ENABLED: bool = True
    GUARDRAIL_TOXICITY_THRESHOLD: float = 0.8
    GUARDRAIL_INJECTION_THRESHOLD: float = 0.7
    GUARDRAIL_MAX_INPUT_CHARS: int = 4000
    GUARDRAIL_MAX_OUTPUT_CHARS: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()