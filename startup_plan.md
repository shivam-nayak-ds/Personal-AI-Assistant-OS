# 🚀 Hermes AI OS — Startup Product Plan
### Next.js + FastAPI · Vercel + Railway · Real Users · 50+ LPA Portfolio

---

## 🎯 Product Vision

> **Hermes AI OS** is a personal AI assistant that knows everything about you —
> your goals, documents, habits, and preferences —
> and helps you achieve more every single day.

**Tagline:** *Your Personal AI that actually remembers you.*

**Target users:**
- Students preparing for job interviews
- Developers wanting an AI that knows their notes/projects
- Productivity-obsessed people who want a smarter daily planner

---

## 🏗️ Final Tech Stack Decision

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14 (App Router) | Portfolio standard, SSR, beautiful UI |
| **Backend** | FastAPI (Python) | Already built, async, fast |
| **Database** | PostgreSQL 15 | Reliable, relational |
| **Cache** | Redis 7 | Rate limiting, sessions, caching |
| **Vector DB** | Pinecone | Scalable, interview-friendly |
| **Primary LLM** | OpenRouter | One API → GPT-4, Claude, Gemini |
| **Fast LLM** | Groq (Llama 3) | Ultra-fast responses for chat |
| **Embeddings** | Gemini `embedding-001` | Free, 768 dims, works great |
| **Background Jobs** | Celery + Redis | Morning briefings, doc processing |
| **Frontend Deploy** | Vercel | Free tier, CDN, instant |
| **Backend Deploy** | Railway | Easy Docker deploy, $5/mo |
| **Auth** | JWT (already built) | Secure, stateless |

---

## 🤖 LLM Strategy (Multi-Provider)

You have: **OpenRouter + Groq + Gemini**

```
Chat (general)     → Groq (llama-3.1-70b)   ← Fastest, free tier
Chat (complex)     → OpenRouter → GPT-4o    ← Best quality
Goal decompose     → OpenRouter → Claude    ← Best reasoning
Embeddings         → Gemini embedding-001  ← Free, accurate
Voice STT          → Groq (Whisper)        ← Fastest transcription
Fallback           → Gemini 1.5 Flash      ← Free, reliable
```

**Interview story:** *"I built a multi-provider LLM router — Groq for speed, OpenRouter for quality, Gemini for free embeddings. I pick the right model for each task based on latency vs cost tradeoff."*

---

## 🌐 What the Product Looks Like

### Landing Page (public, for real users)
```
┌──────────────────────────────────────────────┐
│  🤖 Hermes AI OS                    [Sign Up] │
│                                               │
│  "Your Personal AI that actually              │
│   remembers you."                            │
│                                               │
│  [Get Started Free]  [Watch Demo]             │
│                                               │
│  ✓ Chat with AI that knows your goals        │
│  ✓ Ask questions from your documents         │
│  ✓ Morning briefings, goal tracking          │
└──────────────────────────────────────────────┘
```

### Dashboard (after login)
```
┌─────────────────────────────────────────────────┐
│  Hermes AI OS        [Shivam ▾]    [Settings]   │
├────────┬────────────────────────────────────────┤
│        │                                        │
│  📊    │   Good morning, Shivam! 🌅             │
│  Home  │   Today: 3 tasks due · 1 goal overdue  │
│        │                                        │
│  💬    │   ┌─────────────────────────────────┐  │
│  Chat  │   │ 💬 Chat with Hermes             │  │
│        │   │                                 │  │
│  🎯    │   │ You: What should I focus on?    │  │
│  Goals │   │ AI: Based on your goals and...  │  │
│        │   │                                 │  │
│  ✅    │   └─────────────────────────────────┘  │
│  Tasks │                                        │
│        │   📈 Goal Progress    📋 Today's Tasks  │
│  📚    │   Get 50 LPA ▓▓▓░ 60% ✅ Study DSA     │
│  Docs  │   Launch App ▓░░░ 20% ☐ Write ADR      │
│        │                                        │
│  🧠    │                                        │
│  Memory│                                        │
└────────┴────────────────────────────────────────┘
```

---

## 📁 Final Folder Structure

### Backend (FastAPI) — already at `d:\Personal-AI-Assistant`
```
app/
├── main.py              ← register ALL 14 routers
├── core/                ✅ config, security, logger, dependencies
├── db/                  ✅ PostgreSQL setup
├── models/              ✅ 11 models (after cleanup)
├── schemas/             ← add: chat, memory, document, voice
├── api/                 ← build: chat, documents, memories, voice
├── services/            ← build: chat, memory, document, voice
├── repositories/        ← build: memory, document, conversation
├── rag/                 ← build entirely (chunker, embedder, retriever)
├── agents/              ← create + build (orchestrator, planner)
├── clients/
│   ├── llm_client.py    ✅ update to support Groq + OpenRouter + Gemini
│   └── base_client.py   ✅
└── cache/
    └── redis_client.py  ✅
```

### Frontend (Next.js) — new project at `d:\Personal-AI-Assistant\frontend`
```
frontend/
├── app/
│   ├── page.tsx              ← Landing page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── (dashboard)/
│       ├── chat/page.tsx     ← Real-time streaming chat
│       ├── goals/page.tsx    ← Goal board + progress
│       ├── tasks/page.tsx    ← Task kanban board
│       ├── documents/page.tsx← Upload + ask questions
│       └── memories/page.tsx ← View what AI knows about you
├── components/
│   ├── ChatWindow.tsx        ← streaming chat with SSE
│   ├── GoalCard.tsx
│   ├── TaskBoard.tsx
│   └── DocumentUpload.tsx
├── lib/
│   └── api.ts                ← API client (calls FastAPI backend)
└── ...
```

---

## 📋 6 Phases — Build Order

---

### Phase 0 — Cleanup ✅ DONE
- [x] Deleted 4 duplicate model files
- [x] Deleted 3 empty client files
- [x] Fixed Docker port 8001 → 8000
- [ ] Update LLM client to support Groq + OpenRouter + Gemini
- [ ] Register all 14 routers in main.py

---

### Phase 1 — RAG + Document Q&A
**Time: 3 days**

Build the pipeline that lets you ask questions from your uploaded files.

```
What gets built:
├── app/rag/chunker.py        ← split text into 512-token chunks
├── app/rag/embedder.py       ← Gemini embedding-001
├── app/rag/vector_store.py   ← Pinecone upsert + query
├── app/rag/retriever.py      ← BM25 + vector hybrid search
├── app/rag/pipeline.py       ← full flow: upload → process → answer
├── app/services/document_service.py
├── app/repositories/document_repo.py
└── app/api/documents.py      ← POST /documents/upload
                              ← POST /documents/query
                              ← GET  /documents
```

**User experience after Phase 1:**
```
Upload "System Design Notes.pdf"
Ask: "What did I write about database sharding?"
Get: "In your notes, you mentioned sharding is..."
       [Source: System Design Notes.pdf, Page 3]
```

---

### Phase 2 — Chat + Memory
**Time: 3 days**

Build the AI chat that remembers you across sessions.

```
What gets built:
├── app/services/chat_service.py    ← full chat with context injection
├── app/services/memory_service.py  ← importance scoring
├── app/repositories/memory_repo.py ← SQL queries
├── app/repositories/conversation_repo.py
├── app/api/chat.py                 ← POST /chat/message
│                                   ← GET  /chat/stream (SSE)
│                                   ← GET  /chat/conversations
└── app/api/memories.py             ← GET/POST /memories
```

**User experience after Phase 2:**
```
You: "I prefer bullet-point answers"
AI:  [remembers → applies to all future responses]

You: "What are my active goals?"
AI:  "Based on your profile:
      • Get 50 LPA job (60% done, 30 days left)
      • Launch Hermes app (20% done)"
```

---

### Phase 3 — Agent System
**Time: 3 days**

Build the orchestrator that routes to the right AI agent.

```
What gets built:
├── app/agents/__init__.py
├── app/agents/orchestrator.py     ← routes messages to right agent
├── app/agents/planner_agent.py    ← goal → weekly tasks breakdown
├── app/agents/memory_agent.py     ← extracts facts from chat
└── app/agents/tools/
    ├── web_search.py              ← DuckDuckGo search
    └── datetime_tool.py           ← current date/time
```

**User experience after Phase 3:**
```
You: "Help me plan: Get a 50 LPA job in 90 days"
AI:  "Here's your 90-day plan:
      Week 1-2: DSA fundamentals (arrays, strings)
      Week 3-4: System Design basics
      Week 5-6: Behavioral interviews..."
      [Automatically creates 12 weekly tasks in your dashboard]
```

---

### Phase 4 — Voice + Smart Automation
**Time: 2 days**

Voice commands + automated daily briefings.

```
What gets built:
├── app/services/voice_service.py     ← Groq Whisper STT + TTS
├── app/api/voice.py                  ← POST /voice/transcribe
│                                     ← POST /voice/speak
├── app/workers/morning_briefing.py   ← Celery task @ 8 AM
└── Goals API update                  ← POST /goals/:id/decompose (AI)
```

**User experience after Phase 4:**
```
08:00 AM → You get an email/notification:
"Good morning Shivam! Today:
 • 3 tasks due (DSA practice, System Design notes, Mock interview)
 • Goal 'Get 50 LPA' is 60% complete with 30 days left
 • Yesterday's streak: ✅ Coding (Day 14!)"

Voice: [Record audio] "Add task: Review LLD patterns today"
AI: "Done! Added to your tasks."
```

---

### Phase 5 — Next.js Frontend
**Time: 4 days | Makes it a real product for real users**

Build the web app that real users will use.

```
What gets built:
├── Landing page (beautiful, convincing)
├── Auth pages (login + register)
├── Chat dashboard (streaming responses)
├── Goals + Tasks board
├── Document upload + Q&A
└── Memory viewer ("What does Hermes know about me?")
```

**This is what gets shared with real users for feedback.**

---

### Phase 6 — Deploy + Portfolio
**Time: 2 days**

```
Deploy:
├── Frontend → Vercel (vercel.com, free)
├── Backend  → Railway (railway.app, $5/mo)
├── Database → Railway PostgreSQL
└── Redis    → Railway Redis

Portfolio:
├── 5 ADRs (Architecture Decision Records)
├── System design document
├── README with demo GIF
└── Blog post on dev.to / LinkedIn
```

**End result:** A live URL you can share with real users and interviewers.

---

## 🔑 .env Updates Needed

Add these to your `.env` file before we start:

```env
# LLM Providers (add your keys)
OPENROUTER_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Pinecone
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=hermes-vectors
PINECONE_ENVIRONMENT=gcp-starter

# Primary LLM routing
PRIMARY_LLM=groq          # groq / openrouter / gemini
GROQ_MODEL=llama-3.1-70b-versatile
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
EMBEDDING_MODEL=models/embedding-001   # Gemini
```

---

## ✅ Approve This Plan?

Once approved, I'll start **Phase 0 final tasks** immediately:
1. Update LLM client to support Groq + OpenRouter + Gemini
2. Register all 14 routers in main.py
3. Then move to Phase 1 — RAG Pipeline

**One phase at a time. No jumping around.**
