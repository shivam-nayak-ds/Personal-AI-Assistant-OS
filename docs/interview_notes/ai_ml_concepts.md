# AI/ML Concepts — 50+ LPA Interview Prep

## RAG Pipeline (From This Project)

### Chunking Strategy
- **Size**: 512 tokens per chunk (balance between context and precision)
- **Overlap**: 50 tokens (ensure no context lost at boundaries)
- **Strategy**: Recursive character split (respects paragraph/sentence boundaries)

### Embedding Model
- **Local**: Sentence-Transformers `all-MiniLM-L6-v2` (384 dims, ~50ms per chunk)
- **Cloud**: OpenAI `text-embedding-3-small` (1536 dims, higher quality, paid)
- **Tradeoff**: Local for speed/cost, cloud for accuracy. Hybrid approach — local for daily queries, cloud for complex ones.

### Hybrid Search
```python
# BM25 (keyword) + Vector (semantic) = Hybrid
def hybrid_search(query: str, alpha: float = 0.5):
    bm25_score = bm25_search(query)       # Exact keyword match
    vector_score = vector_search(query)   # Semantic similarity
    return alpha * bm25_score + (1-alpha) * vector_score
```

### Reranking
Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) re-ranks top-20 results for precision. Slower but more accurate than bi-encoder alone.

### Citation Builder
Every LLM response includes source references:
> "Your next task is 'Finish report' (from goal 'Q4 Review', created Jan 15)"

## Memory System

### Importance Scoring
```python
def score_memory(memory: Memory) -> float:
    score = 0.0
    score += memory.recency_weight * recency(hours_ago)   # 0-1
    score += memory.frequency_weight * frequency(count)     # 0-1
    score += memory.relevance_weight * relevance(current_context)  # 0-1
    score += memory.emotional_weight * emotional_impact     # 0-1 (user tagged as important)
    return score  # Higher = more important, kept longer
```

### Memory Tiers
| Tier | Importance | Retention | Storage |
|------|-----------|-----------|---------|
| Core | >0.8 | Forever | PostgreSQL + Vector DB |
| Working | 0.5-0.8 | 7 days | PostgreSQL |
| Ephemeral | <0.5 | 24 hours | Redis (volatile) |

## Agent Architecture

### Tool Use
```python
tools = [
    Tool(name="search_memory", fn=search_memory),
    Tool(name="get_goals", fn=get_active_goals),
    Tool(name="create_task", fn=create_task),
    Tool(name="read_document", fn=read_document),
]
agent = ReActAgent(llm=llm, tools=tools)
```

### Multi-Agent Communication
- **Orchestrator Agent**: Routes tasks to specialized agents
- **Goal Agent**: Manages goals, habits, reviews
- **Memory Agent**: Handles retrieval and storage
- **Voice Agent**: STT/TTS pipeline

## Common Interview Questions

**Q**: How do you evaluate RAG quality?  
**A**: Three metrics — hit rate (did we retrieve the right doc?), MRR (was it ranked first?), and answer faithfulness (did the LLM use retrieved context or hallucinate?).

**Q**: How do you handle hallucination?  
**A**: Citation constraints ("only answer from provided context"), confidence thresholds (<0.7 = "I don't know"), and human-in-the-loop for critical decisions.

**Q**: Embedding model choice?  
**A**: Tradeoff between speed (local MiniLM, 384d) and accuracy (OpenAI text-embedding-3-small, 1536d). Use local for 90% of queries, cloud for complex ones.

**Q**: How do you keep memory relevant?  
**A**: Importance scoring decay — memories lose relevance over time unless reinforced. Core memories (user's name, goals, preferences) never decay.
