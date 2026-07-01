"""
Hermes AI OS - Main FastAPI Application
Personal AI Assistant with RAG, Memory, Multi-Agent, Deep Thinking, and Guardrails.
"""

import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import get_logger
from app.core.exceptions import register_exception_handlers
from app.db.session import check_database_health, get_pool_stats, init_db

# ── API Routers ────────────────────────────────────────────────────────────────
from app.api.auth          import router as auth_router
from app.api.users         import router as users_router
from app.api.goals         import router as goals_router
from app.api.tasks         import router as tasks_router
from app.api.chat          import router as chat_router
from app.api.documents     import router as documents_router
from app.api.memories      import router as memories_router
from app.api.voice         import router as voice_router
from app.api.schedules     import router as schedules_router
from app.api.routines      import router as routines_router
from app.api.notifications import router as notifications_router
from app.api.analytics     import router as analytics_router

settings = settings
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    # ── STARTUP ────────────────────────────────────────────────────────────────
    logger.info("🚀 Starting Hermes AI OS", extra={
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    })

    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database init skipped: {e}")

    # Verify LLM providers
    try:
        from app.clients.llm_client import get_llm_client
        llm = get_llm_client()
        logger.info(f"✅ LLM providers: {llm.status}")
    except Exception as e:
        logger.warning(f"⚠️ LLM client init: {e}")

    logger.info("✅ Hermes AI OS started successfully")
    yield

    # ── SHUTDOWN ───────────────────────────────────────────────────────────────
    logger.info("🛑 Shutting down Hermes AI OS...")
    logger.info("✅ Shutdown complete")


# ── App Instance ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="Personal AI Assistant — Goals · Tasks · RAG · Memory · Voice · Agents",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────

# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else settings.CORS_ORIGINS.split(","),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Exception handlers
register_exception_handlers(app)

# 3. Request ID + logging middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    request.state.request_id = request_id

    response = await call_next(request)

    duration_ms = round((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms}ms"

    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms) [{request_id}]")
    return response


# ── Routers ────────────────────────────────────────────────────────────────────
v1 = settings.API_V1_PREFIX

app.include_router(auth_router,          prefix=f"{v1}/auth",          tags=["🔐 Auth"])
app.include_router(users_router,         prefix=f"{v1}/users",         tags=["👤 Users"])
app.include_router(goals_router,         prefix=f"{v1}/goals",         tags=["🎯 Goals"])
app.include_router(tasks_router,         prefix=f"{v1}/tasks",         tags=["✅ Tasks"])
app.include_router(chat_router,          prefix=f"{v1}/chat",          tags=["💬 Chat"])
app.include_router(documents_router,     prefix=f"{v1}/documents",     tags=["📚 Documents"])
app.include_router(memories_router,      prefix=f"{v1}/memories",      tags=["🧠 Memory"])
app.include_router(voice_router,         prefix=f"{v1}/voice",         tags=["🎤 Voice"])
app.include_router(schedules_router,     prefix=f"{v1}/schedules",     tags=["🗓️ Schedules"])
app.include_router(routines_router,      prefix=f"{v1}/routines",      tags=["🔁 Routines"])
app.include_router(notifications_router, prefix=f"{v1}/notifications", tags=["🔔 Notifications"])
app.include_router(analytics_router,     prefix=f"{v1}/analytics",     tags=["📊 Analytics"])


# ── Health Endpoints ───────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "phases_complete": {
            "infrastructure": True,
            "auth": True,
            "goals_tasks": True,
            "rag": False,
            "chat_memory": False,
            "agents": False,
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health/db", tags=["Health"])
async def database_health():
    db_ok = check_database_health()
    return {"database": "healthy" if db_ok else "unhealthy", "pool": get_pool_stats()}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    if not check_database_health():
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": "DB unavailable"})
    return {"status": "ready"}


@app.get("/health/providers", tags=["Health"])
async def provider_health():
    """Check which LLM providers are configured and available"""
    try:
        from app.clients.llm_client import get_llm_client
        llm = get_llm_client()
        return {"status": "ok", "providers": llm.status}
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)