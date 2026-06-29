# 🔧 Environment Configuration Guide

## 📋 Environment Files Overview

| File | Purpose | Git Tracked | When to Use |
|------|---------|-------------|-------------|
| `.env` | Your actual config | ❌ No | Local development |
| `.env.example` | Template | ✅ Yes | First-time setup |
| `.env.development` | Dev defaults | ✅ Yes | Development |
| `.env.production` | Prod defaults | ✅ Yes | Production deployment |

---

## 🚀 Quick Setup

### For Development:
```bash
# Copy development template
copy .env.development .env

# Add your API keys
# Edit .env and set:
# - OPENAI_API_KEY
# - Other required keys
```

### For Production:
```bash
# Copy production template
copy .env.production .env

# Configure all production values
# IMPORTANT: Change all SECRET_KEY values!
```

---

## 📊 Configuration Priority Levels

### ⭐ Priority 1: Must Configure (Required for Basic Functionality)

#### 1. **Application Settings**
```env
ENVIRONMENT=development          # development, production, staging
APP_NAME=Hermes AI OS
APP_VERSION=1.0.0
DEBUG=True                       # Set to False in production!
SECRET_KEY=<random-string>       # Generate secure key
```

**How to generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 2. **Database Configuration**
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DB_POOL_SIZE=20                  # Connection pool size
DB_MAX_OVERFLOW=30               # Max additional connections
DB_POOL_TIMEOUT=30               # Timeout in seconds
DB_POOL_RECYCLE=3600             # Recycle connections after 1 hour
```

#### 3. **Multi-LLM Support**
```env
DEFAULT_LLM_PROVIDER=openai      # openai, anthropic, google, groq

# OpenAI (GPT-4, GPT-3.5)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google (Gemini)
GOOGLE_API_KEY=AI...

# Groq (Fast inference)
GROQ_API_KEY=gsk_...

# OpenRouter (Multi-model gateway)
OPENROUTER_API_KEY=sk-or-...
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google AI: https://makersuite.google.com/app/apikey
- Groq: https://console.groq.com/
- OpenRouter: https://openrouter.ai/keys

#### 4. **Embeddings Configuration**
```env
EMBEDDING_PROVIDER=openai        # openai or huggingface
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
HF_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

#### 5. **Vector Database**
```env
VECTOR_DB=qdrant                 # qdrant or pinecone

# Qdrant (Local or Cloud)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                  # Optional for local
QDRANT_COLLECTION_NAME=hermes-knowledge

# Pinecone (Cloud only)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=hermes-knowledge
```

**Setup Qdrant:**
```bash
# Local with Docker
docker run -p 6333:6333 qdrant/qdrant
```

**Setup Pinecone:**
- Sign up: https://www.pinecone.io/
- Create index with dimension 1536

#### 6. **Agent Configuration**
```env
MAX_AGENT_ITERATIONS=10          # Max reasoning steps
MAX_CONTEXT_LENGTH=16000         # Max tokens in context
ENABLE_MEMORY=true               # Enable memory system
ENABLE_RAG=true                  # Enable document retrieval
ENABLE_STREAMING=true            # Stream responses
```

#### 7. **Redis (Cache & Queue)**
```env
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=                  # Empty for local
```

#### 8. **Logging**
```env
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                  # json or text
LOG_FILE=logs/app.log
LOG_ROTATION=10MB                # Rotate when file reaches size
LOG_RETENTION_DAYS=30
```

#### 9. **Security**
```env
# API Security
API_KEY=                         # Optional API key for endpoints
ENCRYPTION_KEY=                  # For encrypting sensitive data

# Cookies
COOKIE_SECURE=false              # true in production
COOKIE_HTTPONLY=true
COOKIE_SAMESITE=lax

# JWT
JWT_SECRET_KEY=<random-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Passwords
PASSWORD_MIN_LENGTH=8
BCRYPT_ROUNDS=12                 # Higher = more secure, slower
```

#### 10. **Object Storage**
```env
# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_BUCKET=hermes-uploads
AWS_REGION=us-east-1

# MinIO (Local S3-compatible)
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
MINIO_BUCKET=hermes-uploads
```

#### 11. **Monitoring**
```env
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000
SENTRY_DSN=https://...@sentry.io/...
OTEL_EXPORTER_OTLP_ENDPOINT=
ENABLE_TELEMETRY=false
```

#### 12. **Feature Flags**
```env
ENABLE_VOICE=true                # Voice interface
ENABLE_IMAGE=true                # Image processing
ENABLE_DOCUMENT_CHAT=true        # Document Q&A
ENABLE_WEB_SEARCH=true           # Web search capability
ENABLE_CODE_INTERPRETER=true     # Code execution
```

---

### 🔵 Priority 2: Very Useful (Recommended)

#### Cache
```env
CACHE_TTL=3600                   # Cache time-to-live (seconds)
CACHE_ENABLED=true
CACHE_PREFIX=hermes:
```

#### File Uploads
```env
MAX_FILE_SIZE_MB=20
MAX_UPLOAD_SIZE_MB=20
ALLOWED_FILE_TYPES=pdf,docx,txt,md,png,jpg,jpeg,csv,json
UPLOAD_DIR=./uploads
```

#### Session Management
```env
SESSION_TIMEOUT=30               # Minutes
MAX_CONCURRENT_USERS=100
SESSION_COOKIE_NAME=hermes_session
```

#### CORS
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOW_CREDENTIALS=true
ALLOW_METHODS=*
ALLOW_HEADERS=*
```

#### WebSocket
```env
WEBSOCKET_TIMEOUT=300            # Seconds
WEBSOCKET_MAX_CONNECTIONS=1000
WEBSOCKET_PING_INTERVAL=30
```

#### Rate Limiting
```env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_ENABLED=true
```

#### Celery (Background Jobs)
```env
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TASK_ALWAYS_EAGER=false   # true for debugging
CELERY_TASK_TRACK_STARTED=true
```

---

### 🟢 Priority 3: Production (Optional but Important for Production)

#### Docker
```env
DOCKER_ENV=development
```

#### Background Jobs
```env
ENABLE_BACKGROUND_JOBS=true
SCHEDULER_TIMEZONE=UTC
```

#### Email
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@hermesai.com
EMAIL_VERIFICATION=true
RESET_PASSWORD_EXPIRY=15         # Minutes
```

#### AI Limits
```env
MAX_CHAT_HISTORY=20              # Messages to keep in context
MAX_UPLOAD_FILES=10              # Per request
MAX_RAG_DOCUMENTS=5              # Documents to retrieve
MAX_TOKENS_PER_REQUEST=4000
MAX_MEMORY_ITEMS=100
```

---

## 🔗 Integrations (Optional)

### Google Calendar
```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google/callback
```

### Notion
```env
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
```

### GitHub
```env
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=yourusername
```

### Slack
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
```

---

## 🎤 Voice & Speech

```env
# Speech-to-Text
STT_PROVIDER=openai
WHISPER_MODEL=whisper-1

# Text-to-Speech
TTS_PROVIDER=openai
TTS_VOICE=shimmer                # alloy, echo, fable, onyx, nova, shimmer
TTS_SPEED=1.0                    # 0.25 to 4.0
```

---

## 🔍 Web Search

```env
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=tvly-...
SERP_API_KEY=...
BRAVE_API_KEY=...
```

---

## 🛡️ Security Best Practices

### Development
- ✅ Use weak passwords for local database
- ✅ Disable HTTPS requirements
- ✅ Allow all CORS origins
- ✅ Use DEBUG=True

### Production
- ❌ NEVER commit `.env` to Git
- ✅ Use strong, random SECRET_KEY
- ✅ Enable COOKIE_SECURE=true
- ✅ Restrict CORS origins
- ✅ Use environment-specific secrets
- ✅ Enable rate limiting
- ✅ Set DEBUG=False
- ✅ Use managed database services
- ✅ Enable monitoring and logging

---

## 📝 Environment Loading Order

The application loads environment variables in this order:

1. System environment variables
2. `.env` file (if exists)
3. `.env.development` or `.env.production` (based on ENVIRONMENT)
4. Command-line overrides

---

## ✅ Validation Checklist

### Before First Run:
- [ ] `.env` file created
- [ ] OPENAI_API_KEY set
- [ ] DATABASE_URL configured
- [ ] REDIS_URL configured
- [ ] SECRET_KEY generated
- [ ] JWT_SECRET_KEY generated

### Before Production Deployment:
- [ ] All SECRET_KEY values changed
- [ ] DEBUG=False
- [ ] COOKIE_SECURE=true
- [ ] Strong database password
- [ ] CORS origins restricted
- [ ] Monitoring enabled (Sentry)
- [ ] Rate limiting enabled
- [ ] Email SMTP configured
- [ ] Object storage configured (S3/MinIO)
- [ ] SSL/TLS certificates installed

---

## 🆘 Troubleshooting

### "Missing API Key" Error
- Check `.env` file exists
- Verify key is set: `echo %OPENAI_API_KEY%`
- Restart server after changing `.env`

### Database Connection Failed
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Test connection: `psql $DATABASE_URL`

### Redis Connection Failed
- Verify Redis is running: `redis-cli ping`
- Check REDIS_URL

### Vector DB Connection Failed
- For Qdrant: Check if running on port 6333
- For Pinecone: Verify API key and index name

---

**Next:** Once environment is configured, proceed to Phase 1.2!
