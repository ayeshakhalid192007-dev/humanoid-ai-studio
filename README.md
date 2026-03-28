<div align="center">

# 🤖 Humanoid AI Studio

### AI-Native Educational Platform for Physical AI & Humanoid Robotics

[![Live Book](https://img.shields.io/badge/Live_Book-Netlify-00C7B7?style=for-the-badge&logo=netlify)](https://netlify.com)
[![Backend](https://img.shields.io/badge/Backend-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app)
[![Auth Server](https://img.shields.io/badge/Auth-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)
[![gitagent](https://img.shields.io/badge/gitagent-0.1.0-6D28D9?style=for-the-badge)](https://gitagent.sh)

<br/>

![Docusaurus](https://img.shields.io/badge/Docusaurus_3.6-3ECC5F?style=flat-square&logo=docusaurus&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)

</div>

---

## What Is Humanoid AI Studio?

**Humanoid AI Studio** is a production-grade learning platform for **Physical AI and Humanoid Robotics education**. It delivers a 4-module interactive curriculum through a Docusaurus book, guided by an embedded RAG-powered chatbot that answers questions directly from the course content, with OAuth2 social login and AI-powered personalization.

**The problem it solves:**
- Static documentation sites have no AI layer — learners get stuck with no contextual help
- Robotics education content is scattered with no unified, progressive learning path
- No personalization — every learner gets the same experience regardless of language or background

**How it works:**

```mermaid
graph LR
    A[Student Signs Up] --> B[OAuth2 Login]
    B --> C[Module 1 Unlocked]
    C --> D{Learn via Book}
    D --> E[Ask RAG Chatbot]
    D --> F[Select Text → Ask About This]
    D --> G[Request Personalized Chapter]
    G --> H[Urdu or Custom Language]
    E --> I[Gemini Streams Response]
    I --> D
    D --> J[Module 2 → 3 → 4]
    J --> K[Capstone: Autonomous Humanoid]
```

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        FE["Docusaurus Book\n(Netlify)"]
    end

    subgraph Auth["Auth Layer"]
        AUTH["Better-Auth OIDC Server\n(Railway · Node.js)"]
        JWKS["JWKS Endpoint\n/.well-known/jwks.json"]
    end

    subgraph API["API Layer"]
        BACKEND["FastAPI Backend\n(Railway · Python 3.11)"]
        MW["JWKS Middleware\nJWT Validation"]
    end

    subgraph AI["AI Layer"]
        RAG["RAG Pipeline\nQdrant + Sentence Transformers"]
        GEMINI["Google Gemini\nStreaming SSE"]
        PERSONALIZE["Personalization Agent\nUrdu / Custom Language"]
    end

    subgraph Data["Data Layer"]
        PG[("PostgreSQL\nNeon")]
        REDIS[("Redis\nCache + Rate Limit")]
        QDRANT[("Qdrant\nVector Store")]
    end

    FE -->|"OAuth / Session"| AUTH
    FE -->|"API Calls"| BACKEND
    AUTH --> JWKS
    AUTH --> PG
    BACKEND --> MW
    MW --> JWKS
    BACKEND --> RAG
    BACKEND --> PERSONALIZE
    BACKEND --> PG
    BACKEND --> REDIS
    RAG --> QDRANT
    RAG --> GEMINI
```

---

## 🔄 Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Docusaurus Book
    participant AUTH as Better-Auth OIDC
    participant API as FastAPI Backend
    participant AI as RAG / Gemini
    participant DB as Neon Postgres

    U->>FE: Visit Book
    FE->>AUTH: Sign In (Google / GitHub)
    AUTH-->>FE: JWT Access Token (RS256)
    FE->>API: Chat Request + Bearer Token
    API->>AUTH: Verify via JWKS endpoint
    AUTH-->>API: Token valid
    API->>DB: Fetch user session
    DB-->>API: Session data
    API->>AI: RAG query with curriculum context
    AI-->>API: Streamed response (SSE)
    API-->>FE: Response
    FE-->>U: Answer rendered in chat widget
```

---

## 🎓 4-Module Learning Path

```mermaid
graph LR
    S1["Module 1\nROS 2"]
    S2["Module 2\nSimulation"]
    S3["Module 3\nNVIDIA Isaac"]
    S4["Module 4\nVLA Capstone"]

    S1 --> S2
    S2 --> S3
    S3 --> S4

    style S1 fill:#3B82F6,color:#fff
    style S2 fill:#22C55E,color:#fff
    style S3 fill:#F97316,color:#fff
    style S4 fill:#EF4444,color:#fff
```

Each module builds on the previous. All lessons follow the **Prediction → Execution → Reflection** cycle and include executable code, observable outcomes, and debugging scenarios.

---

## 🛠️ Technology Stack

### Frontend
[![Docusaurus](https://img.shields.io/badge/Docusaurus-3.6-3ECC5F?style=flat&logo=docusaurus&logoColor=white)](https://docusaurus.io/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Framer Motion](https://img.shields.io/badge/Framer_Motion-EF4686?style=flat&logo=framer)](https://www.framer.com/motion/)

### Backend
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=flat&logo=gunicorn&logoColor=white)](https://www.uvicorn.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic_V2-E92063?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)

### Auth Server
[![Node.js](https://img.shields.io/badge/Node.js-20+-339933?style=flat&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Express](https://img.shields.io/badge/Express-4.x-000000?style=flat&logo=express)](https://expressjs.com/)
[![Better Auth](https://img.shields.io/badge/Better_Auth-6D28D9?style=flat&logo=auth0&logoColor=white)](https://www.better-auth.com/)

### AI & ML
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-FF6F00?style=flat&logo=huggingface&logoColor=white)](https://www.sbert.net/)

### Databases
[![Qdrant](https://img.shields.io/badge/Qdrant-DC143C?style=flat)](https://qdrant.tech/)
[![Neon Postgres](https://img.shields.io/badge/Neon_Postgres-00E699?style=flat&logo=postgresql&logoColor=black)](https://neon.tech/)
[![Redis](https://img.shields.io/badge/Redis-FF4438?style=flat&logo=redis&logoColor=white)](https://redis.io/)

### Infrastructure
[![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat&logo=railway)](https://railway.app/)
[![Netlify](https://img.shields.io/badge/Netlify-00C7B7?style=flat&logo=netlify&logoColor=white)](https://netlify.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=flat&logo=opentelemetry)](https://opentelemetry.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=prometheus&logoColor=white)](https://prometheus.io/)

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🤖 RAG Chatbot
- Google Gemini + SSE streaming responses
- Qdrant vector retrieval (cosine similarity)
- Sentence Transformers — local, free embeddings
- Text-selection triggered queries
- Full-book or selected-text search modes
- Rate limiting: 20 queries/hour per user

</td>
<td width="50%">

### 🔐 Authentication
- Better-Auth OIDC (RS256 JWT)
- Google + GitHub OAuth2 social login
- JWKS endpoint for token verification
- Secure cross-domain session management
- User profiles in Neon Postgres

</td>
</tr>
<tr>
<td width="50%">

### 🌐 AI Personalization
- Generate custom chapters on demand
- Urdu language support
- Translation endpoint for curriculum content
- Multi-agent skill pipeline orchestration

</td>
<td width="50%">

### 📡 Observability
- OpenTelemetry distributed tracing
- Prometheus metrics export
- Structured JSON logging
- Health check endpoints on all services
- Per-user rate limiting via Redis

</td>
</tr>
</table>

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| Python | 3.11+ |
| Docker | Latest |
| Ubuntu | 22.04 LTS (recommended) |
| GPU (Module 3+) | NVIDIA with 6GB+ VRAM |

### 1. Clone

```bash
git clone https://github.com/ayeshakhalid192007-dev/humanoid-ai-studio.git
cd humanoid-ai-studio
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Key values in `.env`:

```env
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key_fallback
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_QUERIES_PER_HOUR=20
```

### 3. Start Auth Server

```bash
cd auth-server && npm install && npm start
# Runs on http://localhost:3002
```

### 4. Start Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### 5. Start the Book

```bash
cd book && npm install && npm start
# Runs on http://localhost:3000
```

For detailed setup, see **[quickstart.md](specs/001-book-publication-rag-chatbot/quickstart.md)**

---

## 🤖 AI Agent Architecture (gitagent)

Humanoid AI Studio uses [**gitagent**](https://gitagent.sh) — a framework-agnostic, git-native standard for defining AI agents. The agent is version-controlled alongside the codebase, exportable to any LLM framework, and composable across skills.

```bash
# Export the agent as a system prompt (works with any LLM)
npx gitagent export --format system-prompt

# Export as Claude Code CLAUDE.md
npx gitagent export --format claude-code

# Validate agent configuration
npx gitagent validate

# View agent info
npx gitagent info
```

### Agent Structure

```mermaid
graph TB
    subgraph Agent["humanoid-ai-studio agent"]
        SOUL["SOUL.md\nAria — AI tutor identity"]
        RULES["RULES.md\nSafety & content boundaries"]
        AGENTS["AGENTS.md\nSub-agent delegation map"]
        YAML["agent.yaml\nModel, skills, runtime config"]
    end

    subgraph Skills["skills/"]
        S1["rag-tutor\nCurriculum Q&A via Qdrant"]
        S2["personalize-chapter\nAdaptive chapter generation"]
        S3["translate-urdu\nRTL Urdu translation"]
        S4["ros2-guide\nROS 2 Humble step-by-step"]
        S5["code-explainer\nRobotics code walkthrough"]
    end

    subgraph Knowledge["knowledge/"]
        K["index.yaml\nCurriculum + spec document registry"]
    end

    YAML --> Skills
    SOUL --> YAML
    RULES --> YAML
    AGENTS --> YAML
    Skills --> Knowledge
```

### Skills

| Skill | Purpose | Trigger |
|---|---|---|
| `rag-tutor` | Answers curriculum questions via Qdrant + Gemini RAG | Any factual robotics question |
| `personalize-chapter` | Rewrites chapters for learner's background + language | "Personalize this chapter" |
| `translate-urdu` | Translates prose to Urdu RTL, preserves all code | "Translate to Urdu" |
| `ros2-guide` | Step-by-step ROS 2 Humble Hawksbill guidance | ROS 2 how-to questions |
| `code-explainer` | Explains robotics Python/YAML/SDF code line by line | "Explain this code" / debug requests |

### Sub-Agents

```mermaid
graph LR
    O["Orchestrator\nhumanoid-ai-studio"]
    O -->|"curriculum question"| R["rag-tutor\nQdrant + Gemini SSE"]
    O -->|"personalize request"| P["personalization-agent\nProfile + RAG + Gemini"]
    O -->|"translate request"| T["translation-agent\nUrdu RTL output"]
    O -->|"auth / session"| A["auth-agent\nBetter-Auth OIDC"]
```

---

## 📁 Project Structure

```
humanoid-ai-studio/
├── book/                    # Docusaurus 3 frontend (React, TypeScript, Tailwind)
│   ├── docs/                # Curriculum markdown (modules 1–4, capstone)
│   └── src/                 # React components, pages, context, plugins
│
├── backend/                 # FastAPI RAG backend (Python 3.11)
│   ├── src/
│   │   ├── api/             # Endpoints: chat, personalize, translate, sessions, auth
│   │   ├── ai/              # Gemini client, orchestrator, RAG/personalization agents
│   │   ├── db/              # Qdrant (vector) + Neon Postgres clients
│   │   ├── models/          # Pydantic schemas
│   │   └── utils/           # Logging, monitoring, rate limiting
│   └── main.py              # FastAPI app entry point
│
├── auth-server/             # Better Auth server (Node.js, Express)
│   └── src/
│       ├── index.js         # Express + Better Auth setup
│       └── auth.js          # OAuth2/OIDC authentication logic
│
├── agent.yaml               # gitagent manifest — model, skills, runtime config
├── SOUL.md                  # Agent identity (Aria — the AI tutor)
├── RULES.md                 # Agent safety and content boundaries
├── AGENTS.md                # Sub-agent delegation architecture
├── skills/                  # Reusable AI skill modules (rag-tutor, ros2-guide, etc.)
├── knowledge/               # Curriculum document registry for RAG
├── specs/                   # SDD-RI feature specs (spec.md, plan.md, tasks.md)
├── history/                 # Prompt History Records + Architecture Decision Records
└── .specify/                # SDD templates, scripts, project constitution
```

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest
```

### Book (Frontend)

```bash
cd book
npm run build    # type-check + production build
```

**Standard testing environment:**
- OS: Ubuntu 22.04 LTS
- ROS 2: Humble Hawksbill
- Gazebo: Gazebo 11 (Module 2)
- Isaac Sim: NVIDIA Isaac Sim 2023.1.1 (Module 3)

---

## 🚢 Deployment

All deployments are automated via GitHub Actions on push to `main`:

| Workflow | Path Trigger | Target |
|---------|-------------|--------|
| `deploy-book.yml` | `book/**` | Netlify |
| `deploy-backend.yml` | `backend/**` | Railway |
| `deploy-auth.yml` | `auth-server/**` | Railway |

**Required GitHub Secrets:** `RAILWAY_TOKEN`, `NETLIFY_SITE_ID`, `NETLIFY_AUTH_TOKEN`

---

## 📊 Implementation Progress

```
Auth & OAuth2 Login      ████████████████████  Complete
RAG Chatbot              ████████████████████  Complete
Module 1 — ROS 2         ████████████████████  Complete
Module 2 — Simulation    ████████████████████  Complete
Module 3 — NVIDIA Isaac  ████████████████████  Complete
Module 4 — VLA Capstone  ████████████████████  Complete
AI Personalization       ████████████████████  Complete
Observability            ████████████████████  Complete
CI/CD Deployment         ████████████████████  Complete
```

---

## 🤝 Contributing

1. Fork the repository and create a branch: `git checkout -b feature/<name>`
2. Follow **SDD-RI**: Specify → Plan → Implement → Validate
3. All Python-ROS 2 bridges must be reusable and documented
4. Validate in the Standard Testing Environment before opening a PR

**Code Standards:** Python — PEP 8, type hints, async-first · TypeScript — strict mode · React — functional components only · All changes must include observable outcome verification

---

## 📄 License

MIT — see [LICENSE](./LICENSE)

---

## Contact

Maintainer contact information and community links to be added.

**Constitution Version**: 1.2.0 | **Last Updated**: 2026-03-27

---

<div align="center">

### DEVELOP AND DEPLOY THIS SO IT WILL BE BENEFICIAL FOR EVERYONE

</div>
