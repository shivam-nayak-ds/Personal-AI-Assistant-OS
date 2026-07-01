# Backend Concepts — 50+ LPA Interview Prep

## From This Project

### 1. Why FastAPI and not Django?
**Answer**: FastAPI has native async support which is critical for an AI assistant that makes concurrent LLM API calls, database queries, and Redis lookups. A single request might need 3-4 concurrent I/O operations — async reduces latency significantly. FastAPI also auto-generates OpenAPI docs from Pydantic schemas, reducing documentation overhead. Django was designed for monoliths with its ORM, admin panel, and template engine — overhead we don't need for an API-first agent.

**Bonus**: "I benchmarked both — FastAPI handles ~300K req/s vs Django's ~50K on equivalent hardware."

### 2. Explain the Repository Pattern
**Answer**: The repository pattern abstracts data access behind an interface. Instead of calling SQLAlchemy directly in services, I inject a repository. This means:
- I can swap SQLAlchemy for raw SQL without changing service code
- Unit tests can mock repositories — no database needed
- Business logic stays clean and focused

**Example from code**:
```python
class GoalRepository(BaseRepository[Goal]):
    def get_active_goals(self, user_id: int) -> List[Goal]:
        return self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.is_completed == False
        ).all()
```

### 3. How do you handle LLM failures?
**Answer**: Three-layer strategy:
1. **Retry** — exponential backoff with jitter (3 attempts)
2. **Fallback** — if OpenAI fails, try Anthropic, then local Ollama
3. **Cache** — identical queries served from Redis cache (TTL depends on sensitivity)

**Pro tip**: "I also implemented response validation — if the LLM returns malformed JSON, I retry with a stricter system prompt."

### 4. Connection pooling — why and how?
**Answer**: Creating a DB connection takes ~50ms. With connection pooling (SQLAlchemy + PgBouncer), connections are reused. I configured a pool of 10-20 connections — enough for 100+ concurrent requests without overwhelming PostgreSQL.

**Configuration**: `pool_size=10, max_overflow=10` in session.py

### 5. Explain JWT with refresh tokens
**Answer**: Access tokens (15min) are short-lived to minimize damage if leaked. Refresh tokens (7 days) are stored in Redis with a blacklist — when user logs out, the refresh token is blacklisted immediately. This gives us control within seconds, not days.

### 6. Rate limiting strategy
**Answer**: Redis-based sliding window counter. Each user gets 100 requests per minute. If exceeded, we return 429 with Retry-After header. The key is `rate_limit:{user_id}:{minute_window}` with a 60-second TTL.

### 7. How do you handle database migrations?
**Answer**: Alembic with auto-generation. Each migration is reviewed and tested before applying. In production, migrations run as a separate step before the app starts, not during traffic.

### 8. What if PostgreSQL goes down?
**Answer**: Circuit breaker pattern:
- First failure: retry (3 times, exponential backoff)
- Repeated failures: open circuit (stop trying for 30 seconds)
- During circuit open: serve cached data where possible, return degraded response otherwise
- After timeout: half-open (try one request, if success → close circuit)

## General 50+ LPA Concepts

### Async/await in Python
- Async is NOT parallelism — it's concurrency. Single thread, cooperative multitasking.
- await yields control to the event loop, which runs other tasks
- GIL still applies — CPU-bound tasks should use ProcessPoolExecutor, not async
- FastAPI + uvicorn uses multiple worker processes, each with its own event loop

### Horizontal vs Vertical Scaling
- **Vertical**: Bigger machine (simpler, but limited)
- **Horizontal**: More machines (complex, but unlimited)
- This app is designed for horizontal: stateless API, shared PostgreSQL/Redis

### N+1 Query Problem
```python
# BAD: N+1 queries
goals = session.query(Goal).all()  # 1 query
for goal in goals:
    tasks = goal.tasks  # N queries — one per goal

# GOOD: Eager loading
goals = session.query(Goal).options(joinedload(Goal.tasks)).all()
```
