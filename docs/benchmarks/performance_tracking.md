# Performance Benchmarks

## Baseline (Current State)

| Endpoint | Avg Response | P95 | P99 | Status |
|----------|-------------|-----|-----|--------|
| `GET /health` | ~5ms | ~10ms | ~20ms | ✅ Good |
| `GET /api/users/me` | ~15ms | ~30ms | ~50ms | ✅ Good |
| `POST /api/auth/login` | ~50ms | ~100ms | ~200ms | ⚠️ bcrypt cost 12 |
| `GET /api/goals` | ~25ms | ~50ms | ~100ms | ✅ Good |
| `POST /api/chat` | ~2-5s | ~8s | ~15s | ❌ Depends on LLM API |

## Targets (50+ LPA Level)

| Metric | Current | Target | How |
|--------|---------|--------|-----|
| Health check | 5ms | <5ms | Already good |
| Auth (login) | 50ms | <30ms | Reduce bcrypt rounds to 10? Security tradeoff |
| DB queries (list) | 25ms | <10ms | Add DB indexes, optimize joins |
| LLM response | 2-5s | <2s | Streaming + caching common queries |
| Memory search | N/A | <50ms | FTS5 indexing |
| RAG retrieval | N/A | <200ms | Hybrid search with caching |

## Tools for Measurement

- **Locust** — Load testing (simulate 100+ concurrent users)
- **Prometheus** — Request duration histograms
- **Grafana** — Real-time dashboards
- **Python cProfile** — Code-level profiling

## Indexes to Add

```sql
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_is_completed ON goals(is_completed);
CREATE INDEX idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_memories_user_id ON memories(user_id);
CREATE INDEX idx_memories_importance ON memories(importance_score DESC);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

## Optimization Log

| Date | Change | Before | After | Improvement |
|------|--------|--------|-------|-------------|
| — | Add eager loading for Goal.tasks | N+1 queries | 2 queries total | — |
| — | Add Redis caching for goal list | 25ms | ~2ms (cached) | 12x |
| — | Connection pooling | 50ms/conn | ~1ms/conn (pooled) | 50x |
