# System Design: Personal Hermes Agent

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Client Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Web UI  │  │  CLI     │  │  Voice   │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │                     │
│       └──────────────┼──────────────┘                     │
│                      │ HTTP/WS                            │
└──────────────────────┼───────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────┐
│                 API Layer (FastAPI)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Auth    │ │  Goals   │ │  Memory  │ │  Voice   │   │
│  │  Routes  │ │  Routes  │ │  Routes  │ │  Routes  │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       │              │              │              │     │
│  ┌────▼──────────────▼──────────────▼──────────────▼──┐ │
│  │              Service Layer (Business Logic)         │ │
│  │  auth  goal  memory  voice  rag  planner  review   │ │
│  └────────────────────┬────────────────────────────────┘ │
│                       │                                  │
│  ┌────────────────────▼────────────────────────────────┐ │
│  │              Repository Layer (Data Access)          │ │
│  │         user_repo  goal_repo  task_repo  ...         │ │
│  └────────────────────┬────────────────────────────────┘ │
└───────────────────────┼────────────────────────────────┘
                        │
┌───────────────────────┼────────────────────────────────┐
│                  Data Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │PostgreSQL│  │  Redis   │  │  SQLite  │             │
│  │ (ACID)   │  │ (Cache)  │  │ (FTS5)   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Vector DB (Qdrant / Pinecone for public queries)│  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### Why FastAPI over Django?
| Criteria | FastAPI | Django |
|----------|---------|--------|
| Async support | Native async | Async via ASGI (bolted on) |
| Performance | ~300K req/s | ~50K req/s |
| Type safety | Pydantic + auto OpenAPI | DRF serializers |
| Learning curve | Moderate | Steep (batteries included) |
| Best for | API-first, microservices | Monolith, full-stack |

**Decision**: FastAPI. The agent is API-first with heavy I/O (LLM calls, DB, Redis). Async is critical.

### Why PostgreSQL over MongoDB?
| Criteria | PostgreSQL | MongoDB |
|----------|-----------|---------|
| ACID | Full ACID | Document-level only |
| JSON support | JSONB (indexed, performant) | Native document model |
| Full-text search | FTS (built-in) | Atlas Search (paid) |
| Vector support | pgvector extension | Atlas Vector Search (paid) |
| Maturity | 30+ years | 15+ years |

**Decision**: PostgreSQL for structured data (users, goals, tasks). SQLite FTS5 for local memory (90% of queries stay local).

### Why Redis over Memcached?
| Criteria | Redis | Memcached |
|----------|-------|-----------|
| Data types | Strings, lists, sets, sorted sets, streams | Strings only |
| Persistence | RDB/AOF snapshots | No persistence |
| Pub/Sub | Native | Not supported |
| Celery broker | Native support | Requires additional config |

**Decision**: Redis for caching, session store, rate limiting, AND Celery message broker — single infrastructure dependency.

### Why Repository Pattern?
- **Testability**: Mock repositories in tests without touching DB
- **Separation**: Business logic (services) doesn't know about DB implementation
- **Flexibility**: Swap SQLAlchemy for raw SQL without changing service code

## Data Flow: User Query to Response

```
User: "What's my priority today?"
  │
  ▼
FastAPI → AuthMiddleware → Route Handler
  │
  ▼
Service Layer calls:
  1. MemoryService → Retrieve relevant context (FTS5 + vector)
  2. GoalService → Get active goals + tasks
  3. PlannerService → Priority ranking
  │
  ▼
LLM Call (OpenAI/Anthropic) with:
  - System prompt (agent personality)
  - Retrieved context
  - Current goals/tasks
  │
  ▼
Response → TTS (Edge TTS) → Audio to user
```

## Database Schema

```sql
-- 14 tables across domains:
-- User & Profile
users, user_profiles

-- Goals & Tasks
goals, tasks, habits, routines, schedules

-- Memory & Learning
memories, reviews, notifications

-- Knowledge
documents, conversations, messages

-- System
agent_runs
```

Full schema: See `app/models/` directory (16 model files).

## API Design

All routes follow REST principles:
```
POST   /api/auth/register    → Create user
POST   /api/auth/login       → JWT token pair
GET    /api/goals            → List goals (paginated)
POST   /api/goals            → Create goal with tasks
PUT    /api/tasks/{id}       → Update task status
GET    /api/memories         → Search memories (FTS5)
POST   /api/chat             → Chat with agent
POST   /api/voice/transcribe → STT
POST   /api/voice/speak      → TTS
```

## Security Architecture

- **JWT**: Access token (15min) + Refresh token (7 days) with Redis blacklist
- **Password**: bcrypt (12 rounds)
- **Rate Limiting**: Redis-based, 100 req/min per user
- **Input Validation**: Pydantic schemas on all endpoints
- **CORS**: Whitelist origins only
- **Secrets**: .env file, never committed

## Scalability Considerations

| Bottleneck | Solution |
|------------|----------|
| DB queries | Connection pooling (10-20), indexing on all FK/query columns |
| LLM latency | Response streaming, caching common queries |
| Voice processing | Async task queue (Celery), WebSocket streaming |
| Memory retrieval | FTS5 for local (fast), vector DB only for public queries |
| API throughput | Horizontal scaling with Docker Compose → Swarm/K8s |

## Failure Modes

| Failure | Mitigation |
|---------|-----------|
| PostgreSQL down | Connection retry (3 attempts), fail-open for reads from cache |
| Redis down | Graceful degradation (no cache, no rate limiting) |
| OpenAI API down | Fallback to local model (Ollama) |
| TTS failure | Fallback to text response |
| STT failure | Fallback to text input |
