# 🚀 Setup Guide - Hermes AI OS

## Prerequisites

Before starting, ensure you have installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads/)
- **OpenAI API Key** - [Get one](https://platform.openai.com/api-keys)
- **Pinecone Account** (for vector DB) - [Sign up](https://www.pinecone.io/)

---

## Step 1: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` and add your API keys:**
   - `OPENAI_API_KEY` - Your OpenAI API key (REQUIRED)
   - `PINECONE_API_KEY` - Your Pinecone API key (REQUIRED for Phase 6)
   - Other keys can be added later

3. **Generate secure secret keys:**
   ```bash
   # For SECRET_KEY and JWT_SECRET_KEY, generate random strings:
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

---

## Step 2: Install Dependencies

### Option A: Using Docker (Recommended)

Docker will handle all dependencies automatically.

```bash
# Build and start all services
docker-compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI application (port 8000)
- Celery worker
- Celery beat scheduler
- Flower monitoring (port 5555)

### Option B: Local Development (Without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install PostgreSQL and Redis locally**
   - PostgreSQL: [Download](https://www.postgresql.org/download/)
   - Redis: [Download](https://redis.io/download/)

5. **Create database:**
   ```bash
   createdb hermes_ai
   ```

---

## Step 3: Verify Setup

### Check Services

1. **API Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"healthy"}`

2. **API Documentation:**
   Open in browser: http://localhost:8000/docs

3. **Flower (Celery Monitoring):**
   Open in browser: http://localhost:5555

### Check Logs

```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs app
docker-compose logs postgres
docker-compose logs redis
```

---

## Step 4: Database Setup

### Run Migrations

```bash
# If using Docker
docker-compose exec app alembic upgrade head

# If local development
alembic upgrade head
```

### Create Admin User (After Phase 3)

```bash
# If using Docker
docker-compose exec app python scripts/create_admin.py

# If local
python scripts/create_admin.py
```

---

## Common Commands

### Docker Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild containers
docker-compose up --build

# View logs
docker-compose logs -f

# Access app container shell
docker-compose exec app bash

# Restart specific service
docker-compose restart app
```

### Development Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Start development server (without Docker)
uvicorn app.main:app --reload

# Run Celery worker (without Docker)
celery -A app.workers.celery_app worker --loglevel=info
```

---

## Troubleshooting

### Port Already in Use

```bash
# Windows - Find process using port
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Linux/Mac - Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check database credentials in `.env`

3. Recreate database:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

### Redis Connection Error

1. Check if Redis is running:
   ```bash
   docker-compose ps redis
   ```

2. Test Redis connection:
   ```bash
   docker-compose exec redis redis-cli ping
   ```
   Expected: `PONG`

### OpenAI API Error

1. Verify API key in `.env`:
   ```bash
   echo %OPENAI_API_KEY%
   ```

2. Test API key:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

---

## Next Steps

✅ Environment setup complete!

Now proceed to:
1. **Phase 1.2**: Core Configuration (`app/core/`)
2. **Phase 1.3**: Database Foundation (`app/db/`)
3. **Phase 1.4**: FastAPI Application (`app/main.py`)
4. **Phase 1.5**: LLM Client Setup (`app/clients/`)

See `ROADMAP.md` for detailed implementation steps!

---

## Environment Checklist

- [ ] `.env` file created with API keys
- [ ] Docker Desktop installed and running
- [ ] `docker-compose up` runs without errors
- [ ] http://localhost:8000/health returns `{"status":"healthy"}`
- [ ] http://localhost:8000/docs shows API documentation
- [ ] PostgreSQL accessible on port 5432
- [ ] Redis accessible on port 6379
- [ ] No errors in `docker-compose logs`

**All green?** Proceed to Phase 1.2! 🚀
