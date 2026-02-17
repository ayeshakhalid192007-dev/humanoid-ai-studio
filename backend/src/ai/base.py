"""Base abstract interfaces for agents and skills."""
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel


class SkillPhase(str, Enum):
    """Enumeration for skill execution phases."""
    PRE = "pre"
    POST = "post"
    BOTH = "both"


@dataclass
class SkillContext:
    """Mutable context passed through the skill chain."""
    agent_type: str
    grounding_policy: str
    system_prompt: str
    user_message: str
    original_content: str  # Immutable reference for validation
    original_headings: List[str]  # Extracted heading hierarchy (for structure validation)
    original_code_blocks: List[str]  # Extracted code blocks (for preservation validation)
    ai_response: Optional[str] = None  # Set after AI call
    metadata: Dict[str, Any] = None
    skill_results: List[Dict[str, Any]] = None  # Each: {"skill": str, "phase": str, "status": str, "duration_ms": int, "details": str}

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.skill_results is None:
            self.skill_results = []


class BaseSkill(ABC):
    """Abstract base for composable skills. Declares execution phase."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name of the skill."""
        pass

    @abstractmethod
    def get_phase(self) -> SkillPhase:
        """Return the execution phase of the skill."""
        pass

    async def pre_process(self, context: SkillContext) -> SkillContext:
        """Override for pre-processing. Default: passthrough."""
        return context

    async def post_process(self, context: SkillContext) -> SkillContext:
        """Override for post-processing. Default: passthrough."""
        return context


@dataclass
class AgentRequest:
    """Immutable request passed to agent.execute()."""
    request_type: str  # "personalization" | "translation" | "rag_chat"
    chapter_slug: Optional[str]  # For personalization/translation
    content: Optional[str]  # Pre-fetched chapter content or custom content
    query: Optional[str]  # For RAG chat
    user_id: Optional[str]  # Authenticated user (personalization)
    user_profile: Optional[Dict[str, Any]]  # Profile data (personalization)
    target_language: Optional[str]  # For translation (default: "urdu")
    conversation_history: Optional[List[Dict[str, Any]]]  # For RAG chat
    session_id: Optional[str]  # For RAG chat session tracking
    mode: Optional[str]  # "full_book" | "selected_text" (RAG chat)
    selected_text: Optional[str]  # For selected-text mode (RAG chat)
    stream: bool = False  # Whether to stream response


@dataclass
class AgentResponse:
    """Response from agent.execute()."""
    agent_type: str
    content: str  # The AI-generated content (markdown, answer, etc.)
    cached: bool = False
    model: str = ""
    token_count: int = 0
    latency_ms: int = 0
    skills_used: List[str] = None
    skills_detail: List[Dict[str, Any]] = None
    grounding_policy: str = ""
    agent_data: Dict[str, Any] = None  # Agent-specific data

    def __post_init__(self):
        if self.skills_used is None:
            self.skills_used = []
        if self.skills_detail is None:
            self.skills_detail = []
        if self.agent_data is None:
            self.agent_data = {}


class BaseAgent(ABC):
    """Abstract base for all AI agents. Singleton, stateless per-request."""

    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the agent type identifier."""
        pass

    @abstractmethod
    def get_required_skills(self) -> List[str]:
        """Return the list of skill names that the agent requires."""
        pass

    @abstractmethod
    def get_grounding_policy(self) -> str:
        """Return the grounding policy for this agent."""
        pass

    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent with the given request."""
        pass

    @abstractmethod
    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that the agent's output meets requirements."""
        pass

    async def execute_stream(self, request: AgentRequest):
        """Execute the agent with streaming capability (optional, default raises NotImplementedError)."""
        raise NotImplementedError("Streaming is not implemented for this agent")