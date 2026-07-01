# ADR-001: Why FastAPI?

## Context
Need a web framework for the Personal Hermes Agent — an API-first AI assistant with heavy I/O operations (LLM calls, database queries, Redis caching, voice processing).

## Options Considered

| Framework | Async | Performance | Type Safety | Ecosystem |
|-----------|-------|-------------|-------------|-----------|
| **FastAPI** | ✅ Native async | ~300K req/s | ✅ Pydantic + auto OpenAPI | Growing fast |
| Django + DRF | ❌ Sync (ASGI bolted on) | ~50K req/s | ❌ Manual serializers | Mature |
| Flask | ❌ Sync | ~10K req/s | ❌ No built-in validation | Large |
| Starlette | ✅ Native async | ~400K req/s | ❌ No built-in | Small |

## Decision
**FastAPI** — chosen for native async, automatic OpenAPI docs, and Pydantic validation.

## Tradeoffs

| Pro | Con |
|-----|-----|
| Async I/O handles concurrent LLM/DB calls | Less mature than Django |
| Auto-generated Swagger docs | Fewer built-in features |
| Pydantic = type safety + validation | Must design own project structure |
| Fast (Starlette under the hood) | Smaller job market vs Django in India |

## Mitigations
- Project structure follows Clean Architecture (services, repositories, models)
- Pydantic schemas serve as both validation and documentation
- Repository pattern ensures testability without framework coupling

## Related
- ADR-002: Why PostgreSQL?
- ADR-003: Why Redis?
