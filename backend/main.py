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
from src.api import ai, chatkit  # NEW: AI Orchestrator and ChatKit endpoints
from src.config import get_settings
from src.utils.logger import get_logger
from src.utils.monitoring import setup_monitoring, add_request_instrumentation

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Initialize monitoring and observability
    - Initialize database connections (if not mock mode)
    - Verify external service connectivity

    Shutdown:
    - Close database pools
    - Cleanup resources
    """
    logger.info(f"Starting Physical AI RAG Chatbot API (mode: {'mock' if settings.MOCK_MODE else 'production'})")

    # Initialize monitoring
    try:
        setup_monitoring(
            service_name="physical-ai-backend",
            otlp_endpoint=getattr(settings, 'OTLP_ENDPOINT', None),
            enable_metrics=True,
            enable_tracing=True
        )
        logger.info("Monitoring initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize monitoring: {e}")

    # Startup - only initialize if not in mock mode
    if not settings.MOCK_MODE:
        # Initialize Qdrant client
        try:
            from src.db.qdrant_client import QdrantClient
            qdrant = QdrantClient()
            app.state.qdrant = qdrant
            logger.info("Qdrant client initialized")
        except Exception as e:
            logger.warning(f"Qdrant client initialization failed: {e}")
            # Import and use mock only if the real client fails
            from src.db.qdrant_mock import MockQdrantClient
            app.state.qdrant = MockQdrantClient(url="mock", api_key="mock")

        # Initialize Neon client
        try:
            from src.db.neon_client import NeonClient
            from migrations.migration_manager import MigrationManager

            neon = NeonClient()
            app.state.neon_pool = neon
            app.state.migration_manager = MigrationManager(settings.NEON_DATABASE_URL)

            # Try to connect in the background to prevent blocking startup
            async def connect_to_neon():
                try:
                    await neon.connect()
                    logger.info("Neon connection pool initialized")

                    # Auto-create personalization tables if missing
                    try:
                        async with neon.pool.acquire() as conn:
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
                            logger.info("Database tables verified/created")
                    except Exception as table_err:
                        logger.warning(f"Table creation failed: {table_err}")

                except Exception as conn_err:
                    logger.warning(f"Neon connection failed: {conn_err}")

            # Start connection in background to not block startup
            asyncio.create_task(connect_to_neon())

        except Exception as e:
            logger.warning(f"Neon initialization failed: {e}")
            from src.db.neon_client import NeonClient
            # Create a disconnected client instance for minimal functionality
            app.state.neon_pool = NeonClient()

        # Initialize AI Orchestrator (only if Neon is available)
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
            prompt_registry = PromptRegistry()

            # Register all agents (with proper dependencies)
            personalization_agent = PersonalizationAgent(
                prompt_registry=prompt_registry,
                neon_client=app.state.neon_pool
            )
            translation_agent = TranslationAgent(
                prompt_registry=prompt_registry,
                neon_client=app.state.neon_pool
            )
            rag_agent = RAGReasoningAgent(
                prompt_registry=prompt_registry,
                neon_client=app.state.neon_pool
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
                neon_client=app.state.neon_pool
            )

            app.state.orchestrator = orchestrator
            logger.info("AI Orchestrator initialized with agents and skills")
        except Exception as e:
            logger.warning(f"AI Orchestrator initialization failed: {e}")
            logger.warning("Continuing with limited AI functionality")
    else:
        # For mock mode, initialize minimal services
        from src.db.qdrant_mock import MockQdrantClient
        from src.db.neon_client import NeonClient
        app.state.qdrant = MockQdrantClient(url="mock", api_key="mock")
        app.state.neon_pool = NeonClient()

    # Background cleanup task (only if Neon is connected)
    cleanup_task = None
    try:
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
                                neon = app.state.neon_pool
                                # Only run cleanup if neon is connected (has a pool)
                                if hasattr(neon, 'pool') and neon.pool:
                                    # Clean up agent execution logs older than 90 days
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

    # Close Neon connection pool if it exists and is connected
    if hasattr(app.state, 'neon_pool') and hasattr(app.state.neon_pool, 'pool') and app.state.neon_pool.pool:
        await app.state.neon_pool.close()
        logger.info("Neon connection pool closed")

    # Close any migration manager connections
    if hasattr(app.state, 'migration_manager'):
        try:
            await app.state.migration_manager.close_pool()
            logger.info("Migration manager connection closed")
        except Exception as e:
            logger.warning(f"Error closing migration manager: {e}")




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

# Add request instrumentation
add_request_instrumentation(app, service_name="physical-ai-backend")

# Include routers
app.include_router(chat.router, tags=["Chat"])
app.include_router(sessions.router, tags=["Sessions"])
app.include_router(health.router, tags=["Health"])

# Personalization & Translation routers
app.include_router(personalize.router, tags=["Personalization"])
app.include_router(translate.router, tags=["Translation"])

# AI Agent and ChatKit routers (new architecture)
app.include_router(ai.router, tags=["AI Agent"])
app.include_router(chatkit.router, tags=["ChatKit"])






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
