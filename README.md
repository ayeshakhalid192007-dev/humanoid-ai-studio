# Humanoid AI Studio

> An interactive, full-stack educational platform for Physical AI and Humanoid Robotics — powered by a RAG chatbot, OAuth2 authentication, and a live curriculum book.

[![Deploy Book](https://img.shields.io/badge/Book-Netlify-00C7B7?logo=netlify)](https://netlify.com)
[![Backend](https://img.shields.io/badge/Backend-Railway-0B0D0E?logo=railway)](https://railway.app)
[![Auth Server](https://img.shields.io/badge/Auth-Railway-0B0D0E?logo=railway)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

---

## What Is This?

**Humanoid AI Studio** is a production-grade learning platform that teaches Physical AI and Humanoid Robotics through:

- A **Docusaurus curriculum book** with 4 progressive modules
- An **embedded RAG chatbot** (Retrieval-Augmented Generation) that answers questions from the curriculum
- **OAuth2 social login** (Google, GitHub) via Better Auth
- **AI-powered personalization** — generate custom chapters in Urdu or other languages
- Full **observability**, **rate limiting**, and **cloud deployment** on Railway + Netlify

The platform follows **Spec-Driven Development with Reusable Intelligence (SDD-RI)** methodology — every feature is specified, planned, tested, and documented before it is built.

---

## Tech Stack

<div align="center">

**Frontend**

![Docusaurus](https://img.shields.io/badge/Docusaurus_3.6-3ECC5F?style=for-the-badge&logo=docusaurus&logoColor=white)
![React](https://img.shields.io/badge/React_18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-EF4686?style=for-the-badge&logo=framer&logoColor=white)

**Backend**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_V2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

**Auth Server**

![Express](https://img.shields.io/badge/Express.js_4-000000?style=for-the-badge&logo=express&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js_20-339933?style=for-the-badge&logo=node.js&logoColor=white)
![Better Auth](https://img.shields.io/badge/Better_Auth-6D28D9?style=for-the-badge&logo=auth0&logoColor=white)

**AI & LLM**

![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white)

**Databases**

![Qdrant](https://img.shields.io/badge/Qdrant-DC143C?style=for-the-badge&logo=databricks&logoColor=white)
![Neon](https://img.shields.io/badge/Neon_Postgres-00E699?style=for-the-badge&logo=postgresql&logoColor=black)
![Redis](https://img.shields.io/badge/Redis-FF4438?style=for-the-badge&logo=redis&logoColor=white)

**Deployment & Infra**

![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![Netlify](https://img.shields.io/badge/Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**Observability**

![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)

</div>

---

## Curriculum — 4 Modules

### Module 1: The Robotic Nervous System (ROS 2)
**Focus**: Middleware for robot control

- ROS 2 Nodes, Topics, and Services
- Bridging Python Agents to ROS controllers via `rclpy`
- URDF (Unified Robot Description Format) for humanoids

**Learning Outcomes**:
- LO-001: Predict message flow through ROS 2 graphs
- LO-002: Write Python nodes controlling URDF-defined joints
- LO-003: Debug node communication using CLI tools
- LO-004: Reason about URDF joint limits and workspace constraints
- LO-005: Explain when to use topics vs services vs action servers

---

### Module 2: The Digital Twin (Gazebo & Unity)
**Focus**: Physics simulation and environment building

- Simulating physics, gravity, and collisions in Gazebo
- High-fidelity rendering and human-robot interaction in Unity
- Simulating sensors: LiDAR, Depth Cameras, IMUs

**Learning Outcomes**:
- LO-101: Configure sensor plugins and predict sensor output formats
- LO-102: Debug physics simulation failures (collision, gravity, friction)
- LO-103: Transfer Module 1 ROS 2 nodes to simulated environments

---

### Module 3: The AI-Robot Brain (NVIDIA Isaac)
**Focus**: Advanced perception and training

- NVIDIA Isaac Sim — photorealistic simulation and synthetic data generation
- Isaac ROS — hardware-accelerated VSLAM and navigation
- Nav2 — path planning for bipedal humanoid movement

**Learning Outcomes**:
- LO-201: Generate synthetic training data and validate against real-world distributions
- LO-202: Configure and debug VSLAM pipeline failures
- LO-203: Implement Nav2 path planning for bipedal constraints

---

### Module 4: Vision-Language-Action (VLA)
**Focus**: Convergence of LLMs and Robotics

- Voice-to-Action using OpenAI Whisper
- Cognitive planning — translating natural language into ROS 2 action sequences
- **Capstone**: Autonomous Humanoid that executes voice commands, plans paths, navigates obstacles, and manipulates objects

**Learning Outcomes**:
- LO-301: Decompose natural language commands into ROS 2 action sequences
- LO-302: Integrate voice → perception → planning → manipulation pipeline
- LO-303: Evaluate end-to-end system performance against voice command accuracy

---

## Architecture

```
humanoid-ai-studio/
├── book/                    # Docusaurus 3 frontend (React, TypeScript, Tailwind)
│   ├── docs/                # Curriculum markdown (modules 1–4, capstone)
│   └── src/                 # React components, pages, context, plugins
│
├── backend/                 # FastAPI RAG backend (Python 3.11)
│   ├── src/
│   │   ├── api/             # Endpoints: chat, personalize, translate, sessions, auth
│   │   ├── ai/              # Gemini client, orchestrator, RAG/personalization/translation agents
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
├── specs/                   # SDD-RI feature specs (spec.md, plan.md, tasks.md)
├── history/                 # Prompt History Records + Architecture Decision Records
└── .specify/                # SDD templates, scripts, project constitution
```

---

## Key Features

### RAG Chatbot
- Embedded chat widget in the book UI (bottom-right)
- Retrieves curriculum chunks from Qdrant using cosine similarity
- Answers questions contextually using Google Gemini
- Supports **text selection → "Ask about this"** workflow
- SSE (Server-Sent Events) for streaming responses
- Rate limiting: 20 queries/hour per user (configurable)

### OAuth2 Authentication
- Social login (Google, GitHub) via Better Auth
- JWT access token validation
- Secure cross-domain session management with credential relay
- User profiles stored in Neon Postgres

### AI Personalization
- Generate custom chapters in Urdu or other languages on demand
- Translation endpoint for curriculum content
- Multi-agent orchestration via skill pipeline

### Observability
- Structured JSON logging (Python JSON Logger)
- OpenTelemetry distributed tracing
- Prometheus metrics export
- Health check endpoints on all services

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Node.js | 18+ |
| Python | 3.11+ |
| Docker | Latest |
| Ubuntu | 22.04 LTS (recommended) |
| GPU (Module 3+) | NVIDIA GPU with 6GB+ VRAM |

For detailed environment setup, see **[quickstart.md](specs/001-book-publication-rag-chatbot/quickstart.md)**.

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
# LLM
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key_fallback

# Databases
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
DATABASE_URL=postgresql://user:pass@host/db

# Auth
BETTER_AUTH_SECRET=your_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# App
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_QUERIES_PER_HOUR=20
```

### Run Locally

```bash
# 1. Start the RAG backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. Start the auth server
cd auth-server
npm install
npm start

# 3. Start the book
cd book
npm install
npm start
```

---

## Deployment

| Service | Platform | Notes |
|---|---|---|
| Book (frontend) | Netlify | Auto-deploys from `book/` changes |
| RAG Backend | Railway | Docker-based, health check on `/health` |
| Auth Server | Railway | Docker-based, health check on `/health` |

### Railway Deployment

Both `backend/` and `auth-server/` include `railway.toml` and `Dockerfile`. Push to your Railway project and set environment variables in the Railway dashboard.

### Netlify Deployment

The `book/` directory is configured for Netlify. Set build command to `npm run build` and publish directory to `build/`.

---

## Pedagogical Approach

### Reasoning-First Learning (NON-NEGOTIABLE)

Every lesson follows the **Prediction → Execution → Reflection** cycle:

1. **Prediction Phase** — "Before running, what will this node publish?"
2. **Execution Phase** — Run code, capture output
3. **Reflection Phase** — "Did output match prediction? Why/why not?"
4. **Extension Challenge** — Modify code to achieve new behavior

Active prediction improves retention by 30–50% and engages higher-order thinking (Bloom's Taxonomy: Analysis and Evaluation levels).

### Observable Outcome Standards

Predictions must be verifiable and measurable:

| Type | Example |
|---|---|
| Quantitative | Joint position ±2°, execution time ±0.5s, message rate ±10% |
| Visual | RViz shows expected robot state |
| Logs | Terminal output matches predicted message structure |

**Rejected** (too vague):
- "The robot moves"
- "Output appears in terminal"

**Accepted**:
- "Right arm joint 3 rotates to 45° ±2° in 2.0s ±0.5s"
- "Terminal prints: `[INFO] [joint_controller]: Target reached` within 3 seconds"

---

## Testing Environment

All code is validated against:

- **OS**: Ubuntu 22.04 LTS
- **ROS 2**: Humble Hawksbill (LTS, supported until 2027)
- **Gazebo**: Gazebo 11 (Module 2)
- **Isaac Sim**: NVIDIA Isaac Sim 2023.1.1 (Module 3)
- **Python**: 3.10+

**Protocol**:
1. Fresh Docker container: `osrf/ros:humble-desktop-full`
2. Install only documented dependencies
3. Execute all code snippets in lesson order
4. Verify predictions match outcomes (screenshot/log comparison)

---

## Development Methodology (SDD-RI)

This project follows **Spec-Driven Development with Reusable Intelligence**:

```
Specify → Plan → Tasks → Implement → Validate → Record
```

Every feature has:
- `spec.md` — requirements and acceptance criteria
- `plan.md` — architecture decisions and rationale
- `tasks.md` — testable implementation tasks
- PHR (Prompt History Record) — AI exchange logs for traceability
- ADR (Architecture Decision Record) — significant decisions with rationale

### For Students
1. Prerequisites: Ubuntu 22.04, ROS 2 Humble installed
2. Start with Module 1: `specs/module-1-ros2/`
3. Follow the prediction-execution-reflection cycle for every lesson

### For Instructors
1. Review constitution: `.specify/memory/constitution.md`
2. Use templates: `/sp.specify` (specs), `/sp.plan` (architecture), `/sp.tasks` (tasks)
3. Report issues via GitHub issue tracker with `pedagogy` label

### For Contributors
1. Read governance: Constitution → Enforcement and Accountability section
2. Follow SDD-RI: Specify → Plan → Implement → Validate
3. Validate in Standard Testing Environment before submitting

---

## Project Governance

**Review Authority**: Designated curriculum maintainers (minimum 2) with veto power

**Violation Response**:
- **Minor** (formatting, unclear wording): 7-day fix window
- **Major** (missing prediction checkpoints, untested code): Blocked from release
- **Repeat**: Escalation to project governance

**Principle Hierarchy** (conflict resolution):
1. Reasoning-First Learning — NON-NEGOTIABLE
2. Interactive Verification — Core pedagogy
3. System-Oriented Architecture — Conceptual foundation
4. Modularity and Scalability — Structural requirement
5. Python-ROS 2 Bridge Patterns — Implementation detail
6. SDD-RI — Documentation standard

---

## Version History

| Version | Date | Changes |
|---|---|---|
| v1.2.0 | 2026-02-07 | Added comprehensive governance framework |
| v1.1.0 | 2026-02-07 | Added 4-module curriculum overview |
| v1.0.0 | 2026-02-07 | Initial constitution with 6 core principles |

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Humanoid AI Studio Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Contact

Maintainer contact information and community links to be added.

**Constitution Version**: 1.2.0 | **Last Updated**: 2026-03-27

---

<div align="center">

![DEVELOP](https://img.shields.io/badge/DEVELOP-FF0000?style=for-the-badge)
![AND](https://img.shields.io/badge/AND-FF6600?style=for-the-badge)
![DEPLOY](https://img.shields.io/badge/DEPLOY-FFD700?style=for-the-badge)
![THIS](https://img.shields.io/badge/THIS-00CC00?style=for-the-badge)
![SO](https://img.shields.io/badge/SO-00CCCC?style=for-the-badge)
![IT](https://img.shields.io/badge/IT-0099FF?style=for-the-badge)
![WILL](https://img.shields.io/badge/WILL-6600FF?style=for-the-badge)
![BE](https://img.shields.io/badge/BE-CC00CC?style=for-the-badge)
![BENEFICIAL](https://img.shields.io/badge/BENEFICIAL-FF3399?style=for-the-badge)
![FOR](https://img.shields.io/badge/FOR-FF6600?style=for-the-badge)
![EVERYONE](https://img.shields.io/badge/EVERYONE-FF0000?style=for-the-badge)

</div>
