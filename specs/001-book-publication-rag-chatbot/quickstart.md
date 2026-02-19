# Developer Quickstart Guide: Book Publication & RAG Chatbot

**Feature**: Book Publication & RAG Chatbot
**Branch**: `001-book-publication-rag-chatbot`
**Date**: 2026-02-09
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide walks you through setting up the book publication and RAG chatbot development environment. By the end, you'll have:

- ✅ Docusaurus curriculum book running locally at http://localhost:3000
- ✅ FastAPI chatbot backend running at http://localhost:8000
- ✅ Qdrant vector database with embedded curriculum content
- ✅ Neon Postgres database with conversation history schema
- ✅ OpenAI API integration for embeddings and chat completion

**Estimated Setup Time**: 30-45 minutes

---

## 1. Prerequisites

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.10+ | Backend (FastAPI, OpenAI SDK) | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | Frontend (Docusaurus build) | [nodejs.org](https://nodejs.org/) |
| **Git** | 2.30+ | Version control | [git-scm.com](https://git-scm.com/) |
| **Code Editor** | Any | VSCode recommended | [code.visualstudio.com](https://code.visualstudio.com/) |

**Verify installations**:
```bash
python --version  # Should show 3.10 or higher
node --version    # Should show v18 or higher
npm --version     # Should show 9.0 or higher
git --version     # Should show 2.30 or higher
```

### Required Accounts (Free Tiers)

Create accounts for the following services:

1. **Qdrant Cloud** (Vector database)
   - Sign up: https://cloud.qdrant.io/
   - Create free tier cluster (1GB storage)
   - Save cluster URL and API key

2. **Neon Serverless Postgres** (Relational database)
   - Sign up: https://neon.tech/
   - Create free tier database (500MB storage, 1 compute hour)
   - Save connection string (format: `postgresql://user:password@host/dbname`)

3. **OpenAI** (LLM and embeddings)
   - Sign up: https://platform.openai.com/
   - Generate API key: https://platform.openai.com/api-keys
   - Add $10 credit for testing (embeddings + chat: ~$0.02/query)

4. **Railway** (Backend deployment, optional for local dev)
   - Sign up: https://railway.app/
   - Free tier: 500 hours/month + $5 credit
   - Only needed for production deployment

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended (for local Docusaurus + FastAPI + database connections)
- **Disk**: 2GB free space (Node modules + Python packages)
- **OS**: Windows 10+, macOS 11+, or Linux (Ubuntu 20.04+)
- **Internet**: Required for API calls (OpenAI, Qdrant Cloud, Neon)

---

## 2. Environment Setup

### 2.1 Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/physical-ai-platform.git
cd physical-ai-platform

# Switch to feature branch
git checkout 001-book-publication-rag-chatbot
```

### 2.2 Create Environment Variables File

Create a `.env` file in the project root with your API credentials:

```bash
# Copy template to .env
cp .env.example .env

# Edit .env with your credentials
```

**`.env` Template**:
```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION=curriculum

# Neon Postgres Configuration
NEON_DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# FastAPI Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_CORS_ORIGINS=http://localhost:3000,https://yourdomain.github.io

# Rate Limiting
RATE_LIMIT_QUERIES_PER_HOUR=20
RATE_LIMIT_WINDOW_SECONDS=3600

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=90

# Frontend Configuration (for Docusaurus)
DOCUSAURUS_BASE_URL=/
DOCUSAURUS_URL=https://yourdomain.github.io
```

**Security Note**: Never commit `.env` to Git. The `.gitignore` file excludes it by default.

### 2.3 Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi  # Should show fastapi 0.100+
pip list | grep openai   # Should show openai 1.x
pip list | grep qdrant   # Should show qdrant-client
```

**Expected `requirements.txt`** (example):
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
openai==1.10.0
qdrant-client==1.7.3
asyncpg==0.29.0
python-dotenv==1.0.0
httpx==0.26.0
pytest==7.4.4
pytest-asyncio==0.23.3
```

### 2.4 Install Frontend Dependencies

```bash
# Navigate to book directory
cd ../book

# Install Node.js dependencies
npm install

# Verify installation
npm list docusaurus --depth=0  # Should show @docusaurus/core 3.x
```

**Expected `package.json` dependencies** (example):
```json
{
  "dependencies": {
    "@docusaurus/core": "^3.1.0",
    "@docusaurus/preset-classic": "^3.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "clsx": "^2.1.0",
    "prism-react-renderer": "^2.3.1"
  },
  "devDependencies": {
    "@docusaurus/module-type-aliases": "^3.1.0",
    "@docusaurus/types": "^3.1.0",
    "typescript": "^5.3.3"
  }
}
```

---

## 3. Database Initialization

### 3.1 Initialize Neon Postgres Schema

Run the database setup script to create tables and indexes:

```bash
# From project root, navigate to backend
cd backend

# Ensure virtual environment is active
# Run setup script
python scripts/setup_db.py
```

**Expected Output**:
```
Connecting to Neon Postgres...
Creating chat_sessions table...
Creating conversation_turns table...
Creating rate_limit_records table...
Creating indexes...
✅ Database schema initialized successfully
```

**What This Does**:
- Creates `chat_sessions` table with session tracking
- Creates `conversation_turns` table with conversation history
- Creates `rate_limit_records` table for sliding window rate limiting
- Creates indexes on timestamp and session_id columns for fast queries

**Troubleshooting**:
- If connection fails, verify `NEON_DATABASE_URL` in `.env`
- Check that Neon project has available compute hours (free tier: 1 hour/month)
- Ensure SSL mode is enabled (`?sslmode=require` in connection string)

### 3.2 Embed Curriculum Content in Qdrant

Generate embeddings for all curriculum markdown files and store in Qdrant:

```bash
# From backend directory
python scripts/embed_curriculum.py
```

**Expected Output**:
```
Reading curriculum files from ../book/docs/...
Found 24 lessons across 4 modules
Parsing markdown and extracting chunks...
Extracted 487 chunks (avg 650 words/chunk)
Generating embeddings (batch size: 50)...
  Batch 1/10: 50 chunks embedded (1.2s)
  Batch 2/10: 50 chunks embedded (1.1s)
  ...
  Batch 10/10: 37 chunks embedded (0.9s)
Total embedding cost: $0.12 (487 chunks × 1536 dimensions)
Uploading to Qdrant collection 'curriculum'...
✅ Curriculum successfully embedded (487 chunks, 3.2 MB)
```

**What This Does**:
1. Parses all markdown files in `book/docs/` directory
2. Splits content at heading boundaries (`##` and `###`)
3. Extracts metadata: module, lesson, section_title, url
4. Generates embeddings using OpenAI `text-embedding-3-small`
5. Uploads chunks + embeddings to Qdrant collection
6. Creates HNSW index for fast vector search

**Troubleshooting**:
- If OpenAI API error, check `OPENAI_API_KEY` is valid
- If Qdrant connection fails, verify `QDRANT_URL` and `QDRANT_API_KEY`
- If out of storage, reduce chunk count (delete old curriculum versions)
- Cost alert: 500 chunks × $0.0001 per 1K tokens = ~$0.50 total

---

## 4. Local Development

### 4.1 Start Backend Server

In one terminal, start the FastAPI backend:

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Uvicorn server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
- Open http://localhost:8000/docs in browser (FastAPI auto-generated docs)
- Test health endpoint: http://localhost:8000/health
- Expected response:
  ```json
  {
    "status": "healthy",
    "services": {
      "qdrant": "up",
      "neon": "up",
      "openai": "up"
    },
    "timestamp": "2026-02-09T14:30:45Z"
  }
  ```

### 4.2 Start Book Development Server

In a second terminal, start the Docusaurus development server:

```bash
# Navigate to book directory
cd book

# Start Docusaurus dev server
npm start
```

**Expected Output**:
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at http://localhost:3000/

✔ Client
  Compiled successfully in 3.45s

webpack compiled successfully
```

**Verify Frontend**:
- Open http://localhost:3000 in browser
- Book homepage should load with navigation sidebar
- Check chatbot widget appears in bottom-right corner
- Try typing a question in chatbot (should connect to http://localhost:8000/chat)

### 4.3 Test End-to-End Flow

**Step 1**: Open book page (e.g., http://localhost:3000/docs/module1/lesson3)

**Step 2**: Click chatbot widget in bottom-right corner

**Step 3**: Type a question:
```
What are URDF joint limits?
```

**Step 4**: Verify response includes:
- Answer text referencing curriculum content
- Citations with clickable links (e.g., "Module 1, Lesson 3")
- Typing indicator during generation (animated dots)

**Step 5**: Test conversation persistence:
- Ask follow-up question: "Can you give an example?"
- Navigate to another page (e.g., Module 2, Lesson 1)
- Open chatbot again → conversation history should persist

**Step 6**: Test rate limiting:
- Submit 21 queries in rapid succession
- 21st query should return 429 error: "Rate limit: 20 queries/hour"

---

## 5. Testing

### 5.1 Backend Unit Tests

Run pytest for backend services:

```bash
# From backend directory
pytest tests/unit/ -v

# Expected output:
# tests/unit/test_embedder.py::test_embed_text PASSED
# tests/unit/test_retriever.py::test_vector_search PASSED
# tests/unit/test_rate_limiter.py::test_sliding_window PASSED
# ========================= 15 passed in 2.3s =========================
```

### 5.2 Backend Integration Tests

Test API contracts:

```bash
# From backend directory
pytest tests/integration/ -v

# Tests include:
# - POST /chat with valid query (200 response)
# - POST /chat with empty query (400 error)
# - POST /chat with rate limit exceeded (429 error)
# - GET /health with all services up (200 response)
```

### 5.3 Frontend Tests

Run Jest tests for React components:

```bash
# From book directory
npm test

# Tests include:
# - ChatbotWidget component renders correctly
# - sessionStorage persistence across navigation
# - Citation links navigate to correct book sections
```

### 5.4 End-to-End Tests

Run Playwright tests for full chatbot flow:

```bash
# From backend directory (requires both frontend and backend running)
pytest tests/e2e/ -v

# Tests include:
# - User types question, receives answer with citations
# - Conversation history persists across page navigation
# - Rate limiting triggers after 20 queries
# - Offline message shown when backend unavailable
```

---

## 6. Deployment

### 6.1 Deploy Backend to Railway

**Prerequisites**:
- Railway account created
- GitHub repository connected to Railway

**Steps**:
1. Go to https://railway.app/dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository and `001-book-publication-rag-chatbot` branch
4. Railway auto-detects Python project (uses `requirements.txt`)
5. Add environment variables:
   - Go to project settings → Variables
   - Copy all variables from `.env` file
   - Save variables
6. Deploy:
   - Railway auto-deploys on every commit to branch
   - Wait ~2 minutes for build + deployment
7. Get backend URL:
   - Click "Generate Domain" button
   - Copy URL (e.g., `https://your-backend.railway.app`)
   - Update `BACKEND_CORS_ORIGINS` to include this URL

**Verify Deployment**:
- Visit https://your-backend.railway.app/health
- Should return 200 with all services "up"

### 6.2 Deploy Book to GitHub Pages

**Prerequisites**:
- GitHub repository is public (or organization has paid plan)
- GitHub Pages enabled in repository settings

**Steps**:
1. Update `docusaurus.config.js` with production values:
   ```javascript
   const config = {
     url: 'https://yourusername.github.io',
     baseUrl: '/physical-ai-platform/',  // Repository name
     // ...
   };
   ```

2. GitHub Actions workflow already configured (`.github/workflows/deploy-book.yml`)

3. Push to main branch:
   ```bash
   git checkout main
   git merge 001-book-publication-rag-chatbot
   git push origin main
   ```

4. GitHub Actions auto-builds and deploys:
   - Go to repository → Actions tab
   - Watch "Deploy Docusaurus" workflow run (~5 minutes)
   - On success, book deployed to GitHub Pages

5. Verify deployment:
   - Visit https://yourusername.github.io/physical-ai-platform/
   - Book should load with chatbot widget
   - Chatbot queries should hit Railway backend

### 6.3 Update Chatbot Widget with Production Backend

Edit `book/src/components/ChatbotWidget/index.tsx`:

```typescript
// Change API endpoint from localhost to Railway URL
const BACKEND_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-backend.railway.app'
  : 'http://localhost:8000';
```

Commit and push to trigger redeployment.

---

## 7. Common Issues

### Issue 1: "CORS Error" when chatbot tries to connect to backend

**Symptoms**: Browser console shows: `Access-Control-Allow-Origin error`

**Cause**: Backend CORS middleware not configured for frontend domain

**Solution**:
1. Check `BACKEND_CORS_ORIGINS` in `.env` includes frontend URL
2. For local dev: `http://localhost:3000`
3. For production: `https://yourusername.github.io`
4. Restart backend server after changing `.env`

### Issue 2: "Chatbot temporarily offline" message

**Symptoms**: Chatbot shows error: "Database maintenance"

**Cause**: Neon Postgres auto-suspended (compute hours exhausted)

**Solution**:
1. Check Neon dashboard: https://console.neon.tech/
2. Verify compute hours remaining (free tier: 1 hour/month)
3. Database auto-resumes on next query (<1s delay)
4. If hours exhausted, wait until next billing cycle or upgrade to paid tier

### Issue 3: "High demand" error from chatbot

**Symptoms**: Chatbot shows: "Estimated wait: 30 seconds"

**Cause**: OpenAI API rate limit exceeded

**Solution**:
1. Wait for rate limit window to reset (~1 minute)
2. Check OpenAI usage: https://platform.openai.com/usage
3. If consistently hitting limits, upgrade OpenAI tier
4. Implement query caching (FR-049) to reduce API calls

### Issue 4: Docusaurus build fails with "Invalid frontmatter"

**Symptoms**: `npm start` or GitHub Actions build fails with frontmatter error

**Cause**: Markdown file has malformed YAML frontmatter

**Solution**:
1. Check error message for file path and line number
2. Open file, verify YAML syntax:
   ```markdown
   ---
   sidebar_position: 3
   title: "Lesson Title"
   ---
   ```
3. Use online YAML validator: https://www.yamllint.com/
4. Run pre-commit hook: `python scripts/validate_frontmatter.py <file>`

### Issue 5: "Chunk retrieval score too low" (no relevant results)

**Symptoms**: Chatbot responds: "I don't have specific curriculum content on that topic"

**Cause**: Query embedding doesn't match any curriculum chunks (cosine similarity <0.7)

**Solution**:
1. Verify curriculum content exists for the topic
2. Check Qdrant collection: http://localhost:6333/dashboard (local) or Qdrant Cloud console
3. Re-run embedding script if curriculum updated: `python scripts/embed_curriculum.py`
4. Consider lowering similarity threshold in `backend/src/services/retriever.py` (FR-039)

### Issue 6: Railway deployment runs out of hours mid-quarter

**Symptoms**: Backend stops responding, Railway dashboard shows "service paused"

**Cause**: Free tier 500 hours/month exhausted

**Solution**:
1. Monitor Railway usage dashboard weekly
2. Set up usage alerts at 400 hours (80% threshold)
3. Optimize cold start prevention (health check pings every 4 minutes)
4. If exhausted, upgrade to Railway Hobby plan ($5/month)

---

## 8. Next Steps

After completing this quickstart:

1. **Customize Curriculum Content**:
   - Add markdown files to `book/docs/` directory
   - Follow structure: `book/docs/module<N>/<lesson-name>.md`
   - Re-run embedding script: `python scripts/embed_curriculum.py`

2. **Customize Chatbot Behavior**:
   - Edit system prompt in `backend/src/services/generator.py`
   - Adjust retrieval threshold in `backend/src/services/retriever.py`
   - Add suggested questions in `book/src/components/ChatbotWidget/index.tsx`

3. **Set Up Monitoring**:
   - Add Railway usage alerts (Settings → Notifications)
   - Monitor Neon compute hours (Console → Usage)
   - Track OpenAI API costs (Platform → Usage)

4. **Review Implementation Tasks**:
   - Run `/sp.tasks` command to generate `tasks.md`
   - Follow TDD workflow: write tests first, implement features
   - Submit PRs for review before merging to main

---

## Resources

### Documentation
- **Docusaurus**: https://docusaurus.io/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **Qdrant**: https://qdrant.tech/documentation/
- **Neon Postgres**: https://neon.tech/docs/introduction

### Related Spec Files
- **Plan**: `specs/001-book-publication-rag-chatbot/plan.md`
- **Research**: `specs/001-book-publication-rag-chatbot/research.md`
- **Data Model**: `specs/001-book-publication-rag-chatbot/data-model.md`
- **API Contracts**: `specs/001-book-publication-rag-chatbot/contracts/`

### Support
- **GitHub Issues**: https://github.com/yourusername/physical-ai-platform/issues
- **Feature Spec**: `specs/001-physical-ai-robotics-platform/spec.md`
- **Constitution**: `.specify/memory/constitution.md`

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-09
**Maintained By**: Physical AI Platform Team
