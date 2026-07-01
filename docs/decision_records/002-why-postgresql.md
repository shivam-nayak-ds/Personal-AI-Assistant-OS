# ADR-002: Why PostgreSQL

## Context
Need a primary database for user data, goals, tasks, memories, conversations, and documents. Must support ACID transactions, JSON storage, and full-text search.

## Options Considered

| Database | ACID | JSON | FTS | Vector | Cost |
|----------|------|------|-----|--------|------|
| **PostgreSQL** | ✅ Full | ✅ JSONB | ✅ Built-in | ✅ pgvector | Free |
| MongoDB | ⚠️ Document-level | ✅ Native | ❌ Atlas paid | ❌ Atlas paid | Free/Paid |
| MySQL | ✅ Full | ❌ Limited | ⚠️ Built-in | ❌ No | Free |

## Decision
**PostgreSQL** — full ACID compliance, JSONB for flexible storage, built-in full-text search, and pgvector extension option.

## Tradeoffs

| Pro | Con |
|-----|-----|
| ACID = data integrity guaranteed | Schema migrations required |
| JSONB = flexible document storage | Slower than MongoDB for document-only queries |
| Built-in FTS = no extra service | SETUP complexity vs SQLite |
| pgvector = future vector search | PostgreSQL expertise less common than MySQL |

## Decision Context
SQLite with FTS5 handles LOCAL memory search (90% of queries). PostgreSQL handles AUTHORITATIVE data (user accounts, goals, tasks) where ACID matters.
