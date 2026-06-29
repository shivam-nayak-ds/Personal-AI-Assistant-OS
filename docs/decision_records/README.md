# Architecture Decision Records (ADR)

## What is an ADR?
Architecture Decision Records document important architectural decisions made during the project.

## Format:
Each ADR follows this structure:
1. **Context** - What is the issue we're seeing?
2. **Decision** - What did we decide?
3. **Rationale** - Why did we choose this?
4. **Consequences** - What are the impacts?
5. **Alternatives** - What else did we consider?

---

## Decision Records:

### Infrastructure
- [001-why-fastapi.md](001-why-fastapi.md) - Web framework choice
- [002-why-postgresql.md](002-why-postgresql.md) - Database choice
- [003-why-redis.md](003-why-redis.md) - Caching strategy

### AI/ML
- 004-why-openai.md - LLM provider choice
- 005-why-qdrant.md - Vector database choice
- 006-multi-agent-architecture.md - Agent system design

### Patterns
- 007-repository-pattern.md - Data access pattern
- 008-service-layer.md - Business logic organization
- 009-async-design.md - Async vs sync decisions

---

## How to Add a New ADR:
1. Copy the template below
2. Create a new file: `XXX-title.md`
3. Fill in all sections
4. Add link to this README

## Template:
```markdown
# [Number] - [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision or change?

## Decision
What is the change that we're proposing and/or doing?

## Rationale
Why are we making this decision? What are the technical and business reasons?

## Consequences
What becomes easier or more difficult to do because of this change?

## Alternatives Considered
What other options did we evaluate?

## Related Decisions
Link to related ADRs

## References
Links to documentation, discussions, etc.
```
