"""
Hermes AI OS - Main FastAPI Application

Personal AI Assistant with multi-agent system, RAG, memory, and more.
"""

import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import get_logger
from app.db.session import (
    check_database_health,
    get_pool_stats,
)

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles resource initialization and cleanup.
    """
    # ===== STARTUP =====
    logger.info(
        "Starting Hermes AI OS",
        extra={
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )
    
    logger.info("Hermes AI OS started successfully")
    
    yield  # Server running
    
    # ===== SHUTDOWN =====
    logger.info("Shutting down Hermes AI OS...")
    logger.info("Hermes AI OS shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Personal AI Assistant - Your intelligent companion for goals, tasks, and productivity",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ===== MIDDLEWARE =====

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS.split(","),
    allow_headers=settings.ALLOW_HEADERS.split(","),
)


# 2. Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every request with timing information.
    """
    # Generate request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Store request ID in state for later use
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


# ===== HEALTH CHECK ENDPOINTS =====

@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Welcome message.
    """
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check - returns server status.
    """
    return {
        "success": True,
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/db", tags=["Health"])
async def database_health():
    """
    Database health check - returns database status and pool stats.
    """
    db_healthy = check_database_health()
    pool_stats = get_pool_stats()
    
    return {
        "success": True,
        "database": "healthy" if db_healthy else "unhealthy",
        "pool": pool_stats,
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - for Kubernetes/Docker health checks.
    Returns 200 if ready, 503 if not.
    """
    db_healthy = check_database_health()
    
    if not db_healthy:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "not_ready",
                "reason": "Database not available",
            }
        )
    
    return {
        "success": True,
        "status": "ready",
    }


# ===== INFO ENDPOINTS =====

@app.get("/info", tags=["Info"])
async def app_info():
    """
    Application information and configuration summary.
    """
    return {
        "success": True,
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
        "features": {
            "multi_llm": True,
            "rag": settings.ENABLE_RAG,
            "memory": settings.ENABLE_MEMORY,
            "voice": settings.ENABLE_VOICE,
        },
        "links": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }
    }


# ===== STARTUP MESSAGE =====

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Server will be available at: http://localhost:8000")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )