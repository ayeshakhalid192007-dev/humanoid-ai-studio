"""Personalization Agent module."""
from typing import List
import time
import openai
from openai import AsyncOpenAI

from ..base import BaseAgent, AgentRequest, AgentResponse
from ...services.chapter_retriever import ChapterRetriever
from ..prompts.registry import PromptRegistry
from ...db.neon_client import NeonClient, get_neon_client
from ...config import get_settings


class PersonalizationAgent(BaseAgent):
    """AI agent for content personalization based on user profile."""

    def __init__(self, prompt_registry: PromptRegistry = None, neon_client: NeonClient = None):
        self.client = AsyncOpenAI()
        self.chapter_retriever = ChapterRetriever()
        self.prompt_registry = prompt_registry
        self.neon_client = neon_client
        self.settings = get_settings()

    def get_agent_type(self) -> str:
        return "personalization"

    def get_required_skills(self) -> List[str]:
        # Required skills as defined in the plan
        return ["context_boundary", "hallucination_prevention",
                "knowledge_level", "educational_tone", "markdown_preservation"]

    def get_grounding_policy(self) -> str:
        return "structural_fidelity"

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute personalization on the chapter content."""
        start_time = time.time()

        # Check for cache first (with both content and prompt version)
        if request.user_id and request.chapter_slug and self.neon_client and self.prompt_registry:
            prompt_version = self.prompt_registry.get_version(self.get_agent_type())
            if prompt_version:
                cached_result = await self.neon_client.get_personalized_content(
                    request.user_id,
                    request.chapter_slug,
                    request.content_version or "",  # Using content_version now instead of content
                    prompt_version
                )
                if cached_result:
                    return AgentResponse(
                        agent_type=self.get_agent_type(),
                        content=cached_result["personalized_markdown"],
                        cached=True,
                        model=cached_result.get('model', 'gpt-4o-mini'),
                        token_count=0,  # Not tracked for cached responses
                        latency_ms=0,  # Not applicable for cached responses
                        skills_used=[],
                        skills_detail=[],  # Could track which skills were used previously, but not implemented yet
                        grounding_policy=self.get_grounding_policy(),
                        agent_data={
                            "user_profile_snapshot": cached_result.get("user_profile_snapshot", {}),
                            "content_version": cached_result.get("content_version", ""),
                            "prompt_version": cached_result.get("prompt_version", "")
                        }
                    )

        # Get system prompt from registry
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            system_prompt = template.content if template else "You are an expert educational content personalizer."
        else:
            system_prompt = "You are an expert educational content personalizer."

        # If content isn't provided, fetch from chapter
        content_to_process = request.content
        content_version = ""

        if not content_to_process and request.chapter_slug:
            chapter_data = await self.chapter_retriever.get_chapter_content(request.chapter_slug)
            if not chapter_data:
                raise ValueError(f"Chapter not found: {request.chapter_slug}")
            content_to_process = chapter_data["markdown"]
            content_version = chapter_data.get("version", "")
        elif hasattr(request, 'content_version'):
            content_version = request.content_version

        # Get user profile for personalization
        user_profile = request.user_profile or {}

        # Build the complete prompt with user profile
        profile_info = f"Student Profile: {user_profile}"
        context_prompt = f"{profile_info}\n\nORIGINAL CHAPTER CONTENT:\n{content_to_process}"

        # Create the messages for the AI call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_prompt}
        ]

        # Prepare generation parameters
        temperature = 0.3
        max_tokens = 16000
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            if template:
                temperature = template.temperature
                max_tokens = template.max_tokens

        # Make the API call
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_CHAT_MODEL if self.settings.OPENAI_CHAT_MODEL else "gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            personalized_content = response.choices[0].message.content or ""
            token_count = response.usage.total_tokens if response.usage else 0
            model = response.model if response.model else "gpt-4o-mini"
        except Exception as e:
            # Handle API errors gracefully
            personalized_content = f"I encountered an issue processing your request: {str(e)}"
            token_count = 0
            model = "gpt-4o-mini"

        # Cache the result if we have the necessary components
        if (request.user_id and request.chapter_slug and self.neon_client and
            personalized_content and personalized_content != (content_to_process or "")):

            user_profile_snapshot = request.user_profile or {}
            prompt_version = self.prompt_registry.get_version(self.get_agent_type()) if self.prompt_registry else ""

            await self.neon_client.upsert_personalized_content(
                request.user_id,
                request.chapter_slug,
                personalized_content,
                user_profile_snapshot,
                content_version,
                prompt_version
            )

        # Calculate token usage (rough estimation if not provided by API)
        if token_count == 0:
            token_count = len(personalized_content.split()) * 1.5  # Approximate conversion

        latency = int((time.time() - start_time) * 1000)

        return AgentResponse(
            agent_type=self.get_agent_type(),
            content=personalized_content,
            cached=False,
            model=model,
            token_count=int(token_count),
            latency_ms=latency,
            skills_used=[],
            skills_detail=[],
            grounding_policy=self.get_grounding_policy(),
            agent_data={
                "user_profile_snapshot": user_profile,
                "content_version": content_version,
                "prompt_version": self.prompt_registry.get_version(self.get_agent_type()) if self.prompt_registry else ""
            }
        )

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that personalization preserved structure."""
        # This will be implemented to check for structural fidelity
        # In a real implementation, this would check that headings/code blocks were preserved
        return bool(response.content)  # Basic validation