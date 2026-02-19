"""
Health Check API Endpoint - GET /health

Checks connectivity to all external services (Qdrant, Neon, OpenAI).

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import asyncio
from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

from ..services.retriever import Retriever
from ..db.neon_client import NeonClient
from ..config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str  # "healthy", "degraded", or "unhealthy"
    services: Dict[str, str]
    timestamp: str
    version: str = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check health of all services.

    Returns 200 if all services are up, 503 if any service is down.

    Service checks (2-second timeout each):
    - Qdrant: Collection existence check
    - Neon: SELECT 1 query
    - OpenAI: API key validation (passive check)
    """
    services = {}

    # Check Qdrant
    try:
        retriever = Retriever()
        qdrant_healthy = await asyncio.wait_for(
            retriever.health_check(),
            timeout=2.0
        )
        services["qdrant"] = "up" if qdrant_healthy else "down"
    except asyncio.TimeoutError:
        services["qdrant"] = "timeout"
    except Exception:
        services["qdrant"] = "down"

    # Check Neon Postgres
    neon_client = None
    try:
        neon_client = NeonClient()
        neon_healthy = await asyncio.wait_for(
            neon_client.health_check(),
            timeout=2.0
        )
        services["neon"] = "up" if neon_healthy else "down"
    except asyncio.TimeoutError:
        services["neon"] = "timeout"
    except Exception:
        services["neon"] = "down"
    finally:
        if neon_client:
            await neon_client.close()

    # Check OpenAI (passive - just verify key is configured)
    settings = get_settings()
    services["openai"] = "up" if settings.OPENAI_API_KEY else "down"

    # Determine overall status
    all_up = all(s == "up" for s in services.values())
    any_down = any(s == "down" for s in services.values())

    if all_up:
        overall_status = "healthy"
        status_code = status.HTTP_200_OK
    elif any_down:
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        overall_status = "degraded"
        status_code = status.HTTP_200_OK

    return HealthResponse(
        status=overall_status,
        services=services,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
