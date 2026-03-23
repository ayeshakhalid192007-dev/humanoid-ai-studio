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
import hashlib
from ..clients import get_openai_client
from ..gemini_client import get_gemini_client


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
            retrieved_chunks = await self.retriever.retrieve(query, limit=5)
            retrieved_context = "\n\n".join([chunk.get("content", "") for chunk in retrieved_chunks])
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

        # Get AI client and make the API call
        try:
            client = await get_openai_client(self.settings.OPENAI_CHAT_MODEL or self.model)
            response = await client.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract response details from the cached/completed response
            answer = response['choices'][0]['message']['content'] or ""
            token_count = response['usage']['total_tokens'] if response.get('usage') else 0
            model = response['model'] if response.get('model') else "gpt-4o-mini"
        except Exception as e:
            # Handle API errors gracefully
            answer = f"I encountered an issue processing your request: {str(e)}"
            token_count = 0
            model = "gpt-4o-mini"

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
            retrieved_chunks = await self.retriever.retrieve(query, limit=5)
            retrieved_context = "\n\n".join([chunk.get("content", "") for chunk in retrieved_chunks])
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
            stream = await client.chat.completions.create(
                model=self.settings.OPENAI_CHAT_MODEL if self.settings.OPENAI_CHAT_MODEL else self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
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