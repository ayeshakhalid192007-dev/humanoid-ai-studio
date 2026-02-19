# Quickstart: Dynamic Personalized Chapters + Urdu Translation

**Feature Branch**: `002-personalized-chapters-urdu`

## Prerequisites

- Python 3.11+ with `backend/venv` activated
- Node.js 18+ for book (Docusaurus) and auth-server
- Running services: auth-server (port 3002), backend (port 8000), book (port 3000)
- Environment variables in `backend/.env` and `auth-server/.env`
- Qdrant Cloud collection `curriculum` populated via `embed_curriculum.py`
- Neon Postgres accessible with existing tables

## Setup Steps

### 1. Database Migration

Run the schema migration to create new tables:

```bash
cd backend
python scripts/setup_db_personalization.py
```

This creates:
- `personalized_content` table (user-specific cached content)
- `urdu_translations` table (chapter-level cached translations)
- `ai_generation_rate_limits` table (rate limiting for AI endpoints)

### 2. Backend: New API Endpoints

New files to create:
- `backend/src/api/personalize.py` — POST /api/personalize, GET /api/personalize/status/{slug}
- `backend/src/api/translate.py` — POST /api/translate, GET /api/translate/status/{slug}
- `backend/src/services/content_personalizer.py` — Personalization service with prompt template
- `backend/src/services/content_translator.py` — Translation service with prompt template
- `backend/src/services/chapter_retriever.py` — Chapter content retrieval from Qdrant

Register new routers in `backend/main.py`:
```python
from src.api import personalize, translate
app.include_router(personalize.router, tags=["personalization"])
app.include_router(translate.router, tags=["translation"])
```

### 3. Frontend: Chapter Toolbar Component

New files to create:
- `book/src/components/ChapterToolbar/index.tsx` — Buttons + state management
- `book/src/components/ChapterToolbar/styles.module.css` — Styling including RTL
- `book/src/theme/DocItem/Content/index.tsx` — Swizzled wrapper injecting toolbar

### 4. Run & Test

```bash
# Terminal 1: Auth server
cd auth-server && npm start

# Terminal 2: Backend
cd backend && python main.py

# Terminal 3: Book (Docusaurus)
cd book && npm start
```

### 5. Manual Test Checklist

1. Visit any chapter (e.g., http://localhost:3000/docs/module1/lesson1-ros2-basics)
2. Verify "Personalized Version" and "Translate to Urdu" buttons appear
3. Click "Translate to Urdu" — should work without auth
4. Click "Personalized Version" without login — should show AuthModal
5. Login, click "Personalized Version" — should generate personalized content
6. Revisit same chapter — cached version loads instantly
7. Toggle back to original — in-place content switch

## Key Architecture Decisions

- **RAG pipeline reuse**: Extends existing Qdrant + OpenAI pipeline
- **No ORM**: Raw SQL via asyncpg (matches existing pattern)
- **Docusaurus swizzle**: Wraps DocItem/Content for button injection
- **Existing AuthModal**: Reused for login gate on personalization
