"""Common response envelope for AI agents."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class GenerationMetadata(BaseModel):
    """Metadata about the AI generation process."""
    model: str
    token_count: int
    latency_ms: int
    prompt_version: str


class AIEnvelope(BaseModel):
    """Common response wrapper for all AI agent responses."""
    agent_type: str
    skills_used: List[str]
    cached: bool
    grounding_policy: str
    generation_metadata: GenerationMetadata
    data: Dict[str, Any]  # Agent-specific payload (from AgentResponse.agent_data + content)


class ErrorResponse(BaseModel):
    """Error response structure."""
    error: str
    detail: str
    skill_failed: Optional[str] = None