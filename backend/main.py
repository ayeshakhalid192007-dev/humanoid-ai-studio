"""
FastAPI backend for Physical AI RAG Chatbot

Production-ready RAG pipeline with:
- ChatKit-based conversational orchestration
- Tool-based retrieval (full-book / selected-text modes)
- SSE streaming responses
- Better Auth session integration
- Neon Postgres + Qdrant Cloud storage

Author: Physical AI Platform Team
Date: 2026-02-12
"""
from pathlib import Path
from dotenv import load_dotenv

# Load .env file before any other imports that might use env vars
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import chat, health, sessions, personalize, translate
from src.api import ai  # NEW: AI Orchestrator endpoints
from src.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Initialize database connections (if not mock mode)
    - Verify external service connectivity

    Shutdown:
    - Close database pools
    - Cleanup resources
    """
    logger.info(f"Starting Physical AI RAG Chatbot API (mode: {'mock' if settings.MOCK_MODE else 'production'})")

    # Startup
    if not settings.MOCK_MODE:
        try:
            # Verify Qdrant connectivity
            from src.db.qdrant_client import QdrantClient
            qdrant = QdrantClient()
            logger.info("Qdrant connection verified")

            # Ensure payload indexes exist for chapter filtering
            try:
                from qdrant_client.models import PayloadSchemaType
                for field in ("module", "lesson"):
                    qdrant.client.create_payload_index(
                        collection_name="curriculum",
                        field_name=field,
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                logger.info("Qdrant payload indexes verified/created (module, lesson)")
            except Exception as idx_err:
                logger.warning(f"Qdrant payload index setup: {idx_err}")
        except Exception as e:
            logger.warning(f"Qdrant connection check failed: {e}")

        try:
            # Initialize Neon pool
            from src.db.neon_client import NeonClient
            neon = NeonClient()
            await neon.connect()
            app.state.neon_pool = neon
            logger.info("Neon connection pool initialized")

            # Auto-create personalization tables if missing
            try:
                async with neon.pool.acquire() as conn:
                    # Add prompt_version column to existing tables if not exists
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS personalized_content (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            chapter_slug TEXT NOT NULL,
                            personalized_markdown TEXT NOT NULL,
                            user_profile_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
                            content_version TEXT NOT NULL,
                            prompt_version TEXT NOT NULL DEFAULT '',
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            UNIQUE (user_id, chapter_slug)
                        );
                        CREATE TABLE IF NOT EXISTS urdu_translations (
                            id SERIAL PRIMARY KEY,
                            chapter_slug TEXT NOT NULL UNIQUE,
                            urdu_markdown TEXT NOT NULL,
                            content_version TEXT NOT NULL,
                            prompt_version TEXT NOT NULL DEFAULT '',
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );
                        CREATE TABLE IF NOT EXISTS ai_generation_rate_limits (
                            id SERIAL PRIMARY KEY,
                            identifier TEXT NOT NULL,
                            request_type TEXT NOT NULL,
                            request_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );
                        CREATE TABLE IF NOT EXISTS agent_execution_logs (
                            id SERIAL PRIMARY KEY,
                            agent_type TEXT NOT NULL,
                            grounding_policy TEXT NOT NULL,
                            skills_used TEXT[] NOT NULL,
                            skills_detail JSONB NOT NULL DEFAULT '[]'::jsonb,
                            token_count INTEGER,
                            model TEXT NOT NULL,
                            latency_ms INTEGER NOT NULL,
                            cached BOOLEAN NOT NULL DEFAULT FALSE,
                            request_metadata JSONB DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );

                        CREATE INDEX IF NOT EXISTS idx_agent_logs_created
                            ON agent_execution_logs (created_at);
                        CREATE INDEX IF NOT EXISTS idx_agent_logs_type
                            ON agent_execution_logs (agent_type);
                    """)
                    logger.info("Personalization and agent execution log tables verified/created")
            except Exception as e:
                logger.warning(f"Personalization table setup: {e}")

            # Initialize AI Orchestrator with all required registries
            try:
                from src.ai.orchestrator import AIOrchestrator
                from src.ai.registry import AgentRegistry, SkillRegistry
                from src.ai.prompts.registry import PromptRegistry
                from src.ai.agents.personalization import PersonalizationAgent
                from src.ai.agents.translation import TranslationAgent
                from src.ai.agents.rag import RAGReasoningAgent

                # Initialize registries
                agent_registry = AgentRegistry()
                skill_registry = SkillRegistry()
                prompt_registry = PromptRegistry()  # Will load templates from the default templates directory

                # Register all agents (with proper dependencies)
                personalization_agent = PersonalizationAgent(
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )
                translation_agent = TranslationAgent(
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )
                rag_agent = RAGReasoningAgent(
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )

                agent_registry.register_agent(personalization_agent.get_agent_type(), personalization_agent)
                agent_registry.register_agent(translation_agent.get_agent_type(), translation_agent)
                agent_registry.register_agent(rag_agent.get_agent_type(), rag_agent)

                # Register all skills
                from src.ai.skills.markdown_preservation import MarkdownPreservationSkill
                from src.ai.skills.context_boundary import ContextBoundarySkill
                from src.ai.skills.hallucination_prevention import HallucinationPreventionSkill
                from src.ai.skills.educational_tone import EducationalToneSkill
                from src.ai.skills.knowledge_level import KnowledgeLevelSkill
                from src.ai.skills.code_block_detection import CodeBlockDetectionSkill

                skill_registry.register_skill(MarkdownPreservationSkill().get_name(), MarkdownPreservationSkill())
                skill_registry.register_skill(ContextBoundarySkill().get_name(), ContextBoundarySkill())
                skill_registry.register_skill(HallucinationPreventionSkill().get_name(), HallucinationPreventionSkill())
                skill_registry.register_skill(EducationalToneSkill().get_name(), EducationalToneSkill())
                skill_registry.register_skill(KnowledgeLevelSkill().get_name(), KnowledgeLevelSkill())
                skill_registry.register_skill(CodeBlockDetectionSkill().get_name(), CodeBlockDetectionSkill())

                # Create orchestrator instance
                orchestrator = AIOrchestrator(
                    agent_registry=agent_registry,
                    skill_registry=skill_registry,
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )

                app.state.orchestrator = orchestrator
                logger.info("AI Orchestrator initialized with agents and skills")
            except Exception as e:
                logger.warning(f"AI Orchestrator initialization failed: {e}")

        except Exception as e:
            logger.warning(f"Neon connection failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Physical AI RAG Chatbot API")
    if hasattr(app.state, 'neon_pool'):
        await app.state.neon_pool.close()
        logger.info("Neon connection pool closed")


# Create FastAPI app
app = FastAPI(
    title="Physical AI RAG Chatbot API",
    description="""
Production-ready RAG chatbot for the Physical AI & Humanoid Robotics curriculum.

## Features
- **Full-Book Search**: Semantic search across the entire curriculum
- **Selected-Text Mode**: Answer using only highlighted text
- **Streaming Responses**: Real-time SSE streaming
- **Session Management**: Conversation history and user attribution

## Endpoints
- `POST /chat` - Legacy RAG endpoint (backward compatible)
- `POST /chat/v2` - Enhanced ChatKit endpoint with tool-based retrieval
- `POST /chat/stream` - SSE streaming endpoint
- `GET /chat/modes` - Available answering modes
- `POST /chat/sessions` - Create new session
- `GET /chat/sessions/{id}` - Get session history
- `DELETE /chat/sessions/{id}` - End session
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
cors_origins = settings.BACKEND_CORS_ORIGINS.split(",") if settings.BACKEND_CORS_ORIGINS else []
cors_origins.extend([
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:3001", "http://127.0.0.1:3001",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Rate-Limit-Remaining", "X-Session-ID"]
)


import asyncio
import traceback

# Include routers
app.include_router(chat.router, tags=["Chat"])
app.include_router(sessions.router, tags=["Sessions"])
app.include_router(health.router, tags=["Health"])

# Personalization & Translation routers
app.include_router(personalize.router, tags=["Personalization"])
app.include_router(translate.router, tags=["Translation"])

# AI Agent routers (new architecture)
app.include_router(ai.router, tags=["AI Agent"])


# Background task for cleanup jobs
async def run_cleanup_jobs():
    """
    Run scheduled cleanup jobs in the background.
    """
    while True:
        try:
            # Wait before the first run to allow app to fully start
            await asyncio.sleep(60)  # Wait 1 minute before first run

            # Run cleanup every 24 hours (86400 seconds)
            while True:
                if hasattr(app.state, 'neon_pool'):
                    try:
                        # Clean up agent execution logs older than 90 days
                        neon = app.state.neon_pool
                        deleted_count = await neon.cleanup_agent_execution_logs(retention_days=90)
                        logger.info(f"Cleanup job: Deleted {deleted_count} agent execution logs")

                        # Clean up old rate limit records (older than 24 hours)
                        deleted_rate_limit = await neon.cleanup_old_rate_limit_records(hours=24)
                        logger.info(f"Cleanup job: Deleted {deleted_rate_limit} old rate limit records")

                    except Exception as e:
                        logger.error(f"Cleanup job failed: {e}")
                        logger.error(traceback.format_exc())

                # Wait 24 hours before next run
                await asyncio.sleep(86400)  # 24 hours
        except Exception as e:
            logger.error(f"Background cleanup task failed: {e}")
            logger.error(traceback.format_exc())
            # Wait before retrying
            await asyncio.sleep(300)  # 5 minutes


# Add cleanup task to the original lifespan function
original_lifespan = lifespan  # Save original function

async def lifespan(app: FastAPI):
    """
    Application lifespan handler with background cleanup tasks.
    """
    logger.info(f"Starting Physical AI RAG Chatbot API (mode: {'mock' if settings.MOCK_MODE else 'production'})")

    cleanup_task = None

    # Startup - run original startup logic
    if not settings.MOCK_MODE:
        try:
            # Verify Qdrant connectivity
            from src.db.qdrant_client import QdrantClient
            qdrant = QdrantClient()
            logger.info("Qdrant connection verified")

            # Ensure payload indexes exist for chapter filtering
            try:
                from qdrant_client.models import PayloadSchemaType
                for field in ("module", "lesson"):
                    qdrant.client.create_payload_index(
                        collection_name="curriculum",
                        field_name=field,
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                logger.info("Qdrant payload indexes verified/created (module, lesson)")
            except Exception as idx_err:
                logger.warning(f"Qdrant payload index setup: {idx_err}")
        except Exception as e:
            logger.warning(f"Qdrant connection check failed: {e}")

        try:
            # Initialize Neon pool
            from src.db.neon_client import NeonClient
            neon = NeonClient()
            await neon.connect()
            app.state.neon_pool = neon
            logger.info("Neon connection pool initialized")

            # Auto-create personalization tables if missing
            try:
                async with neon.pool.acquire() as conn:
                    # Add prompt_version column to existing tables if not exists
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS personalized_content (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            chapter_slug TEXT NOT NULL,
                            personalized_markdown TEXT NOT NULL,
                            user_profile_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
                            content_version TEXT NOT NULL,
                            prompt_version TEXT NOT NULL DEFAULT '',
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            UNIQUE (user_id, chapter_slug)
                        );
                        CREATE TABLE IF NOT EXISTS urdu_translations (
                            id SERIAL PRIMARY KEY,
                            chapter_slug TEXT NOT NULL UNIQUE,
                            urdu_markdown TEXT NOT NULL,
                            content_version TEXT NOT NULL,
                            prompt_version TEXT NOT NULL DEFAULT '',
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );
                        CREATE TABLE IF NOT EXISTS ai_generation_rate_limits (
                            id SERIAL PRIMARY KEY,
                            identifier TEXT NOT NULL,
                            request_type TEXT NOT NULL,
                            request_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );
                        CREATE TABLE IF NOT EXISTS agent_execution_logs (
                            id SERIAL PRIMARY KEY,
                            agent_type TEXT NOT NULL,
                            grounding_policy TEXT NOT NULL,
                            skills_used TEXT[] NOT NULL,
                            skills_detail JSONB NOT NULL DEFAULT '[]'::jsonb,
                            token_count INTEGER,
                            model TEXT NOT NULL,
                            latency_ms INTEGER NOT NULL,
                            cached BOOLEAN NOT NULL DEFAULT FALSE,
                            request_metadata JSONB DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );

                        CREATE INDEX IF NOT EXISTS idx_agent_logs_created
                            ON agent_execution_logs (created_at);
                        CREATE INDEX IF NOT EXISTS idx_agent_logs_type
                            ON agent_execution_logs (agent_type);
                    """)
                    logger.info("Personalization and agent execution log tables verified/created")

            except Exception as e:
                logger.warning(f"Personalization table setup: {e}")

            # Initialize AI Orchestrator with all required registries
            try:
                from src.ai.orchestrator import AIOrchestrator
                from src.ai.registry import AgentRegistry, SkillRegistry
                from src.ai.prompts.registry import PromptRegistry
                from src.ai.agents.personalization import PersonalizationAgent
                from src.ai.agents.translation import TranslationAgent
                from src.ai.agents.rag import RAGReasoningAgent

                # Initialize registries
                agent_registry = AgentRegistry()
                skill_registry = SkillRegistry()
                prompt_registry = PromptRegistry()  # Will load templates from the default templates directory

                # Register all agents (with proper dependencies)
                personalization_agent = PersonalizationAgent(
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )
                translation_agent = TranslationAgent(
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )
                rag_agent = RAGReasoningAgent(
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )

                agent_registry.register_agent(personalization_agent.get_agent_type(), personalization_agent)
                agent_registry.register_agent(translation_agent.get_agent_type(), translation_agent)
                agent_registry.register_agent(rag_agent.get_agent_type(), rag_agent)

                # Register all skills
                from src.ai.skills.markdown_preservation import MarkdownPreservationSkill
                from src.ai.skills.context_boundary import ContextBoundarySkill
                from src.ai.skills.hallucination_prevention import HallucinationPreventionSkill
                from src.ai.skills.educational_tone import EducationalToneSkill
                from src.ai.skills.knowledge_level import KnowledgeLevelSkill
                from src.ai.skills.code_block_detection import CodeBlockDetectionSkill

                skill_registry.register_skill(MarkdownPreservationSkill().get_name(), MarkdownPreservationSkill())
                skill_registry.register_skill(ContextBoundarySkill().get_name(), ContextBoundarySkill())
                skill_registry.register_skill(HallucinationPreventionSkill().get_name(), HallucinationPreventionSkill())
                skill_registry.register_skill(EducationalToneSkill().get_name(), EducationalToneSkill())
                skill_registry.register_skill(KnowledgeLevelSkill().get_name(), KnowledgeLevelSkill())
                skill_registry.register_skill(CodeBlockDetectionSkill().get_name(), CodeBlockDetectionSkill())

                # Create orchestrator instance
                orchestrator = AIOrchestrator(
                    agent_registry=agent_registry,
                    skill_registry=skill_registry,
                    prompt_registry=prompt_registry,
                    neon_client=neon
                )

                app.state.orchestrator = orchestrator
                logger.info("AI Orchestrator initialized with agents and skills")
            except Exception as e:
                logger.warning(f"AI Orchestrator initialization failed: {e}")

    # Start background cleanup task
    try:
        cleanup_task = asyncio.create_task(run_cleanup_jobs())
        logger.info("Started background cleanup task")
    except Exception as e:
        logger.error(f"Failed to start background cleanup task: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Physical AI RAG Chatbot API")

    # Cancel background task
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

    if hasattr(app.state, 'neon_pool'):
        await app.state.neon_pool.close()
        logger.info("Neon connection pool closed")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Physical AI RAG Chatbot API",
        "version": "2.0.0",
        "status": "running",
        "mode": "mock" if settings.MOCK_MODE else "production",
        "endpoints": {
            "chat": {
                "legacy": "POST /chat",
                "v2": "POST /chat/v2",
                "stream": "POST /chat/stream",
                "modes": "GET /chat/modes"
            },
            "sessions": {
                "create": "POST /chat/sessions",
                "get": "GET /chat/sessions/{id}",
                "list": "GET /chat/sessions",
                "delete": "DELETE /chat/sessions/{id}"
            },
            "health": "GET /health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development"
    )
