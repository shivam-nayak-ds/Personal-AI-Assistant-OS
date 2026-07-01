# ADR-003: Why Redis

## Context
Need caching, session storage, rate limiting, and a message broker for Celery background tasks.

## Options Considered

| Solution | Data Types | Persistence | Pub/Sub | Celery Broker |
|----------|-----------|-------------|---------|---------------|
| **Redis** | Rich (strings, lists, sets, sorted sets, streams) | ✅ RDB/AOF | ✅ Native | ✅ Native |
| Memcached | Strings only | ❌ None | ❌ No | ❌ No |
| RabbitMQ | Queue only | ✅ Yes | ✅ Yes | ✅ Native |

## Decision
**Redis** — richest data structure support, built-in persistence, pub/sub, AND serves as Celery broker. Single dependency for 4 use cases.

## Tradeoffs

| Pro | Con |
|-----|-----|
| Single infra for cache + broker + session + rate limit | In-memory = data lost if no persistence |
| Extremely fast (~1ms reads) | Memory-bound (not for large datasets) |
| Rich data types enable complex features | No built-in query language |

## Usage in Hermes Agent
- **Cache**: LLM response cache, frequent DB query cache
- **Session**: JWT blacklist, user sessions
- **Rate Limiting**: Sliding window counter
- **Pub/Sub**: Real-time notifications
- **Celery Broker**: Task queue for background jobs
