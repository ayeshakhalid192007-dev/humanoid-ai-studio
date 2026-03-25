"""RAG Reasoning Agent module."""
from typing import List, Dict, Any, AsyncGenerator
import time

from ..base import BaseAgent, AgentRequest, AgentResponse
from ...services.retriever import Retriever
from ...services.embedder import Embedder
from ...services.chapter_retriever import ChapterRetriever
from ..prompts.registry import PromptRegistry
from ...db.neon_client import NeonClient, get_neon_client
from ...config import get_settings
from ..gemini_client import get_gemini_client
from google.genai import types as genai_types


class RAGReasoningAgent(BaseAgent):
    """AI agent for RAG reasoning with strict grounding requirements."""

    def __init__(self, prompt_registry: PromptRegistry = None, neon_client: NeonClient = None, model: str = "gpt-4o-mini"):
        self.model = model
        self.retriever = Retriever()
        self.embedder = Embedder()
        self.chapter_retriever = ChapterRetriever()
        self.prompt_registry = prompt_registry
        self.neon_client = neon_client
        self.settings = get_settings()

    def get_agent_type(self) -> str:
        return "rag_chat"

    def get_required_skills(self) -> List[str]:
        # Required skills as defined in the plan
        return ["context_boundary", "hallucination_prevention"]

    def get_grounding_policy(self) -> str:
        return "strict_grounding"

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute RAG reasoning based on the query."""
        start_time = time.time()

        # For chat, handling both streaming and non-streaming requests
        query = request.query
        mode = request.mode or "full_book"
        selected_text = request.selected_text
        session_id = request.session_id
        user_id = request.user_id

        # Get system prompt from registry
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            system_prompt = template.content if template else "You are a helpful AI assistant."
        else:
            system_prompt = "You are a helpful AI assistant."

        # Retrieve relevant context based on mode
        retrieved_context = ""
        retrieved_chunks = []
        citations = []

        if mode == "selected_text" and selected_text:
            # Use provided selected text as context
            retrieved_context = selected_text
            retrieved_chunks = [{"content": selected_text[:500] + "..." if len(selected_text) > 500 else selected_text}]
            citations = ["Selected text provided by user"]
        else:
            # Use full book mode - retrieve from vector store
            query_embedding = await self.embedder.embed_text(query)
            retrieved_chunks = await self.retriever.search(query_embedding, limit=5)
            retrieved_context = "\n\n".join([chunk.get("text", chunk.get("content", "")) for chunk in retrieved_chunks])
            citations = [f"Module {chunk.get('module', 'Unknown')}, Lesson {chunk.get('lesson', 'Unknown')}"
                        for chunk in retrieved_chunks]

        # Build the complete prompt
        context_prompt = f"RETRIEVED CONTEXT:\n{retrieved_context}\n\nUSER QUERY: {query}"

        # Create the messages for the AI call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_prompt}
        ]

        # Prepare generation parameters
        temperature = 0.7
        max_tokens = 1000
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            if template:
                temperature = template.temperature
                max_tokens = template.max_tokens

        # Get AI client and make the API call using native Gemini SDK
        try:
            client = get_gemini_client()
            # Build google-genai contents from messages list
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
                elif msg["role"] == "assistant":
                    contents.append(genai_types.Content(
                        role="model",
                        parts=[genai_types.Part(text=msg["content"])]
                    ))

            model_name = self.settings.OPENAI_CHAT_MODEL if self.settings.OPENAI_CHAT_MODEL else self.model
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

            answer = response.text or ""
            token_count = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_count = getattr(response.usage_metadata, 'total_token_count', 0) or 0
            model = model_name
        except Exception as e:
            # Handle API errors gracefully
            answer = f"I encountered an issue processing your request: {str(e)}"
            token_count = 0
            model = self.settings.OPENAI_CHAT_MODEL or self.model

        # Calculate token usage (rough estimation if not provided by API)
        if token_count == 0:
            token_count = len(answer.split()) * 1.5  # Approximate conversion

        latency = int((time.time() - start_time) * 1000)

        return AgentResponse(
            agent_type=self.get_agent_type(),
            content=answer,
            cached=False,  # Currently not implementing caching for chat (it has context)
            model=model,
            token_count=token_count,
            latency_ms=latency,
            skills_used=[],
            skills_detail=[],
            grounding_policy=self.get_grounding_policy(),
            agent_data={
                "query": query,
                "citations": citations,
                "retrieved_chunks": retrieved_chunks,
                "session_id": session_id,
                "user_id": user_id,
                "prompt_version": self.prompt_registry.get_version(self.get_agent_type()) if self.prompt_registry else ""
            }
        )

    async def execute_stream(self, request: AgentRequest) -> AsyncGenerator[str, None]:
        """
        Execute streaming RAG reasoning based on the query.
        This method should yield tokens as they are generated.
        """
        query = request.query
        mode = request.mode or "full_book"
        selected_text = request.selected_text
        session_id = request.session_id
        user_id = request.user_id

        # Get system prompt from registry
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            system_prompt = template.content if template else "You are a helpful AI assistant."
        else:
            system_prompt = "You are a helpful AI assistant."

        # Retrieve relevant context based on mode
        retrieved_context = ""
        retrieved_chunks = []
        citations = []

        if mode == "selected_text" and selected_text:
            # Use provided selected text as context
            retrieved_context = selected_text
            retrieved_chunks = [{"content": selected_text[:500] + "..." if len(selected_text) > 500 else selected_text}]
            citations = ["Selected text provided by user"]
        else:
            # Use full book mode - retrieve from vector store
            query_embedding = await self.embedder.embed_text(query)
            retrieved_chunks = await self.retriever.search(query_embedding, limit=5)
            retrieved_context = "\n\n".join([chunk.get("text", chunk.get("content", "")) for chunk in retrieved_chunks])
            citations = [f"Module {chunk.get('module', 'Unknown')}, Lesson {chunk.get('lesson', 'Unknown')}"
                        for chunk in retrieved_chunks]

        # Build the complete prompt
        context_prompt = f"RETRIEVED CONTEXT:\n{retrieved_context}\n\nUSER QUERY: {query}"

        # Create the messages for the AI call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_prompt}
        ]

        # Prepare generation parameters
        temperature = 0.7
        max_tokens = 1000
        if self.prompt_registry:
            template = self.prompt_registry.get_template(self.get_agent_type())
            if template:
                temperature = template.temperature
                max_tokens = template.max_tokens

        client = get_gemini_client()
        try:
            # Build google-genai contents from messages list
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
                elif msg["role"] == "assistant":
                    contents.append(genai_types.Content(
                        role="model",
                        parts=[genai_types.Part(text=msg["content"])]
                    ))

            stream_config = genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction or None,
            )

            model_name = self.settings.OPENAI_CHAT_MODEL if self.settings.OPENAI_CHAT_MODEL else self.model
            async for chunk in await client.aio.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=stream_config,
            ):
                text = chunk.text or ""
                if text:
                    yield text
        except Exception as e:
            # Handle API errors gracefully
            yield f"Error: {str(e)}"

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that the RAG response is properly grounded."""
        # For strict grounding, we should check if citations are present in the agent data
        citations = response.agent_data.get('citations', [])
        retrieved_chunks = response.agent_data.get('retrieved_chunks', [])

        # At minimum, both citations and retrieved chunks should be non-empty for proper grounding
        # Though this is a soft validation, as actual citation checking is more complex
        if not citations and not retrieved_chunks and "not available" not in (response.content or "").lower():
            return False

        return bool(response.content)