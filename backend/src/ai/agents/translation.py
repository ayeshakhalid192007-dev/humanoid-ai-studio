"""Translation Agent module."""
from typing import List
import time

from ..base import BaseAgent, AgentRequest, AgentResponse
from ...services.chapter_retriever import ChapterRetriever
from ..prompts.registry import PromptRegistry
from ...db.neon_client import NeonClient, get_neon_client
from ...config import get_settings
from ..gemini_client import get_gemini_client
from google.genai import types as genai_types


class TranslationAgent(BaseAgent):
    """AI agent for translating chapter content."""

    def __init__(self, prompt_registry: PromptRegistry = None, neon_client: NeonClient = None, model: str = "gpt-4o-mini"):
        self.model = model
        self.chapter_retriever = ChapterRetriever()
        self.prompt_registry = prompt_registry
        self.neon_client = neon_client
        self.settings = get_settings()

    def get_agent_type(self) -> str:
        return "translation"

    def get_required_skills(self) -> List[str]:
        # Required skills as defined in the plan
        return ["context_boundary", "hallucination_prevention",
                "code_block_detection", "markdown_preservation"]

    def get_grounding_policy(self) -> str:
        return "semantic_fidelity"

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute translation on the chapter or custom content."""
        start_time = time.time()

        # Check for cache first if we're translating a chapter (no custom content)
        if (not request.content and request.chapter_slug and self.neon_client and self.prompt_registry):
            prompt_version = self.prompt_registry.get_version(self.get_agent_type())
            if prompt_version:
                cached_result = await self.neon_client.get_urdu_translation(
                    request.chapter_slug,
                    request.content_version or "",  # Using content_version now instead of content
                    prompt_version
                )
                if cached_result:
                    return AgentResponse(
                        agent_type=self.get_agent_type(),
                        content=cached_result["urdu_markdown"],
                        cached=True,
                        model=cached_result.get('model', 'gpt-4o-mini'),
                        token_count=0,  # Not tracked for cached responses
                        latency_ms=0,  # Not applicable for cached responses
                        skills_used=[],
                        skills_detail=[],  # Could track which skills were used previously, but not implemented yet
                        grounding_policy=self.get_grounding_policy(),
                        agent_data={
                            "target_language": request.target_language or "urdu",
                            "source_language": "english",
                            "content_version": cached_result.get("content_version", ""),
                            "prompt_version": cached_result.get("prompt_version", "")
                        }
                    )

        # Get system prompt from registry
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            system_prompt = template.content if template else "You are an expert translator."
        else:
            system_prompt = "You are an expert translator."

        # If content isn't provided, fetch from chapter
        content_to_process = request.content
        content_version = request.content_version or ""

        if not content_to_process and request.chapter_slug:
            chapter_data = await self.chapter_retriever.get_chapter_content(request.chapter_slug)
            if not chapter_data:
                raise ValueError(f"Chapter not found: {request.chapter_slug}")
            content_to_process = chapter_data.get("content", chapter_data.get("markdown", ""))
            content_version = chapter_data.get("content_version", chapter_data.get("version", ""))

        target_language = request.target_language or "urdu"

        # Build the complete prompt with target language
        context_prompt = f"Translate the following content to {target_language}:\n\n{content_to_process}"

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

        # Get AI client and make the API call using native Gemini SDK
        try:
            client = get_gemini_client()
            model_name = self.settings.OPENAI_CHAT_MODEL if self.settings.OPENAI_CHAT_MODEL else "gemini-2.5-flash"
            system_instruction = ""
            contents = []
            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                elif msg["role"] == "user":
                    contents.append(genai_types.Content(
                        role="user",
                        parts=[genai_types.Part(text=msg["content"])]
                    ))
            gen_config = genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction or None,
            )
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=gen_config,
            )
            translated_content = response.text or ""
            token_count = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_count = getattr(response.usage_metadata, 'total_token_count', 0) or 0
            model = model_name
        except Exception as e:
            # Handle API errors gracefully
            translated_content = f"I encountered an issue processing your request: {str(e)}"
            token_count = 0
            model = self.settings.OPENAI_CHAT_MODEL or "gemini-2.5-flash"

        # Cache the result if translating a chapter and we have necessary components
        if (request.chapter_slug and self.neon_client and
            translated_content and translated_content != (content_to_process or "")
            and self.prompt_registry):

            # Use content_version from chapter data or from request
            content_version = request.content_version or ""
            if not request.content and request.chapter_slug and not content_version:
                chapter_data = await self.chapter_retriever.get_chapter_content(request.chapter_slug)
                if chapter_data:
                    content_version = chapter_data.get("version", "")

            prompt_version = self.prompt_registry.get_version(self.get_agent_type()) or ""

            await self.neon_client.upsert_urdu_translation(
                request.chapter_slug,
                translated_content,
                content_version,
                prompt_version
            )

        # Calculate token usage (rough estimation if not provided by API)
        if token_count == 0:
            token_count = len(translated_content.split()) * 1.5  # Approximate conversion

        latency = int((time.time() - start_time) * 1000)

        return AgentResponse(
            agent_type=self.get_agent_type(),
            content=translated_content,
            cached=False,
            model=model,
            token_count=int(token_count),
            latency_ms=latency,
            skills_used=[],
            skills_detail=[],
            grounding_policy=self.get_grounding_policy(),
            agent_data={
                "target_language": target_language,
                "source_language": "english",  # Default, could be detected later
                "content_version": content_version,
                "prompt_version": self.prompt_registry.get_version(self.get_agent_type()) if self.prompt_registry else ""
            }
        )

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that translation preserved semantics and code blocks."""
        # This will be implemented to check for semantic fidelity
        return bool(response.content)  # Basic validation