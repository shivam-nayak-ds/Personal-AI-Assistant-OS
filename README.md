# 🤖 Hermes AI OS - Personal AI Assistant

> An intelligent, autonomous AI assistant that knows everything about you and helps you achieve your goals.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What is Hermes AI OS?

Hermes AI OS is a **Personal AI Operating System** designed to be your intelligent companion that:

- 🎯 **Manages Your Goals** - Track 180-day goals with AI-powered decomposition
- ✅ **Organizes Your Tasks** - Smart task management linked to your goals  
- 🧠 **Remembers Everything** - Advanced memory system that learns about you
- 📚 **Knows Your Documents** - Personal knowledge base with semantic search
- 🗓️ **Optimizes Your Schedule** - Calendar integration and time blocking
- 🎤 **Responds to Voice** - "What's my progress on my goals?"
- 📊 **Provides Insights** - AI-powered analytics and recommendations
- 🤝 **Coordinates Agents** - 6 specialized AI agents working together

---

## ✨ Key Features

### Core Features
- **Goal Management** - Set, track, and achieve long-term goals (180-day planning)
- **Task Management** - Smart task system with auto-prioritization
- **Memory System** - Episodic, semantic, and procedural memory
- **Conversational AI** - Natural language chat interface with context
- **Document RAG** - Upload docs, ask questions, get answers with citations

### Intelligence
- **Multi-Agent System** - Planner, Researcher, Memory, Knowledge, Review, Orchestrator
- **AI Goal Decomposition** - Break complex goals into actionable tasks
- **Context-Aware** - Remembers previous conversations and preferences
- **Adaptive Personalization** - Learns your communication style

### Productivity
- **Daily Schedule** - Calendar sync (Google Calendar, Outlook)
- **Routines & Habits** - Morning/evening routines with streak tracking
- **Smart Notifications** - Morning briefings, evening reflections
- **Time Blocking** - Optimize your day with AI-powered scheduling

### Advanced
- **Voice Interface** - Speech-to-text and text-to-speech
- **Analytics Dashboard** - Goal progress, productivity insights
- **Integrations** - Notion, GitHub, Calendar, Email

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Hermes AI OS                            │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Optional)    │  Voice Interface                  │
│  - React/Next.js        │  - Speech-to-Text                 │
│  - Mobile App           │  - Text-to-Speech                 │
├─────────────────────────────────────────────────────────────┤
│                    FastAPI REST API                         │
│  /goals  /tasks  /chat  /docs  /schedule  /voice           │
├─────────────────────────────────────────────────────────────┤
│                    Multi-Agent System                       │
│  Orchestrator → Planner → Research → Memory → Knowledge    │
├─────────────────────────────────────────────────────────────┤
│        Services Layer (Business Logic)                      │
│  Goal  Task  Memory  RAG  Schedule  Analytics               │
├─────────────────────────────────────────────────────────────┤
│  LLM Clients    │   Vector DB    │   Background Workers    │
│  - OpenAI       │   - Pinecone   │   - Celery              │
│  - Embeddings   │   - Weaviate   │   - Redis Queue         │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis Cache  │  File Storage               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Personal-AI-Assistant.git
   cd Personal-AI-Assistant
   ```

2. **Setup environment:**
   ```bash
   copy .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Flower: http://localhost:5555

For detailed setup instructions, see [SETUP.md](SETUP.md)

---

## 📚 Documentation

- **[ROADMAP.md](ROADMAP.md)** - 10-phase development plan
- **[SETUP.md](SETUP.md)** - Detailed setup instructions  
- **[FEATURES.md](docs/FEATURES.md)** - Complete feature list
- **[TIMELINE.md](TIMELINE.md)** - Development timeline
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (async API framework)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Redis (cache & message broker)
- Celery (background jobs)

**AI/ML:**
- OpenAI GPT-4 (LLM)
- OpenAI Embeddings (text-embedding-3)
- OpenAI Whisper (speech-to-text)
- Pinecone/Weaviate (vector database)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Prometheus (metrics)
- Sentry (error tracking)

---

## 🗂️ Project Structure

```
Personal-AI-Assistant/
├── app/
│   ├── agents/          # AI agents (orchestrator, planner, etc.)
│   ├── api/             # FastAPI endpoints
│   ├── core/            # Config, logging, security
│   ├── db/              # Database setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── memory/          # Memory system
│   ├── rag/             # RAG pipeline
│   ├── schedule/        # Schedule management
│   ├── voice/           # Voice interface
│   ├── workers/         # Celery tasks
│   └── main.py          # FastAPI app
├── tests/               # Test suite
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
└── docker-compose.yml  # Multi-container setup
```

---

## 🎯 Development Roadmap

### ✅ Phase 1: Infrastructure (Week 1)
- FastAPI, Docker, PostgreSQL, Redis, LLM setup

### 🔄 Phase 2: Core Models (Week 2)
- User, Goal, Task, Memory, Document models

### 🔄 Phase 3: Authentication (Week 3)
- JWT auth, user profiles

### ⏳ Phase 4: Goals & Tasks (Weeks 4-5)
- CRUD operations, AI goal decomposition

### ⏳ Phase 5: Memory System (Weeks 6-7)
- Store, retrieve, rank, summarize

### ⏳ Phase 6: RAG Pipeline (Weeks 8-9)
- Document processing, semantic search

### ⏳ Phase 7: Multi-Agent System (Weeks 10-11)
- 6 specialized agents, orchestration

### ⏳ Phase 8: Schedule & Routines (Weeks 12-13)
- Calendar, time blocking, habits

### ⏳ Phase 9: Voice & Analytics (Weeks 13-14)
- Voice interface, insights

### ⏳ Phase 10: Production (Weeks 14-16)
- Testing, deployment, polish

See [ROADMAP.md](ROADMAP.md) for details.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific module
pytest tests/test_goals.py
```

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 and Embeddings API
- FastAPI for the amazing web framework
- The open-source community

---

## 📧 Contact

**Your Name** - [your.email@example.com](mailto:your.email@example.com)

**Project Link:** [https://github.com/yourusername/Personal-AI-Assistant](https://github.com/yourusername/Personal-AI-Assistant)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ for AI Engineer roles at 50 LPA+**
