"""AI Client factories and centralized client management."""
import asyncio
import time
from typing import Any, Dict, Optional, Callable
from openai import AsyncOpenAI
from ..utils.circuit_breaker import CircuitBreaker
from ..utils.logger import get_logger
from ..config import get_settings


class BaseAIClient:
    """Base class for AI clients with common functionality."""

    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o-mini", logger = None):
        self.client = client
        self.model = model
        self.logger = logger or get_logger(__name__)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

    async def _execute_with_circuit_breaker(self, func: Callable, *args, **kwargs):
        """Execute an operation with circuit breaker protection."""
        async def operation():
            return await func(*args, **kwargs)

        return await self.circuit_breaker.execute(operation)


class OpenAIClient(BaseAIClient):
    """OpenAI client with enhanced functionality."""

    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o-mini", logger = None):
        super().__init__(client, model, logger)
        self._cache = {}  # Simple in-memory cache

    async def chat_completion(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000, **kwargs):
        """Execute chat completion with caching and circuit breaker."""
        # Create cache key from messages and parameters (simplified)
        cache_key = f"{self.model}:{hash(str(messages))}:{temperature}:{max_tokens}"

        if cache_key in self._cache:
            self.logger.info(f"Cache hit for: {cache_key[:20]}...")
            return self._cache[cache_key]

        async def _chat_completion():
            start_time = time.time()
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                latency = (time.time() - start_time) * 1000
                self.logger.info(f"Chat completion succeeded for model {self.model} in {latency:.2f}ms")

                # Cache the successful response (with some metadata for cache control)
                result = {
                    'choices': [choice.model_dump() for choice in response.choices],
                    'usage': response.usage.model_dump() if response.usage else None,
                    'model': response.model,
                    'timestamp': time.time()
                }

                # Simple cache limit
                if len(self._cache) > 100:
                    # Remove oldest entry
                    oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].get('timestamp', 0))
                    del self._cache[oldest_key]

                self._cache[cache_key] = result
                return result
            except Exception as e:
                self.logger.error(f"Chat completion failed: {str(e)}", exc_info=True)
                raise

        return await self._execute_with_circuit_breaker(_chat_completion)

    async def embed(self, texts: list, model: str = "text-embedding-3-small", **kwargs):
        """Create embeddings with circuit breaker."""
        async def _embed():
            start_time = time.time()
            try:
                response = await self.client.embeddings.create(
                    input=texts,
                    model=model,
                    **kwargs
                )
                latency = (time.time() - start_time) * 1000
                self.logger.info(f"Embedding creation succeeded for model {model} in {latency:.2f}ms")

                return {
                    'embeddings': [item.embedding for item in response.data],
                    'usage': response.usage.model_dump() if response.usage else None,
                    'model': response.model
                }
            except Exception as e:
                self.logger.error(f"Embedding creation failed: {str(e)}", exc_info=True)
                raise

        return await self._execute_with_circuit_breaker(_embed)


class AIClientFactory:
    """Factory and centralized registry for AI model clients."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self._clients = {}
        self.api_key = api_key
        self.base_url = base_url
        self.logger = get_logger(__name__)

    def create_openai_client(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None) -> OpenAIClient:
        """Create an OpenAI client instance."""
        api_key = api_key or self.api_key or self._get_api_key_from_env()
        if not api_key:
            raise ValueError("OpenAI API key not provided and not found in environment")

        client = AsyncOpenAI(api_key=api_key, base_url=self.base_url)
        return OpenAIClient(client, model, self.logger)

    def get_or_create_client(self, client_type: str, model: str = "gpt-4o-mini", **kwargs) -> BaseAIClient:
        """Get existing client or create new one with caching."""
        client_key = f"{client_type}:{model}"

        if client_key not in self._clients:
            if client_type == "openai":
                api_key = kwargs.get("api_key") or self.api_key or self._get_api_key_from_env()
                self._clients[client_key] = self.create_openai_client(model, api_key)
            else:
                raise ValueError(f"Unsupported client type: {client_type}")

        return self._clients[client_key]

    def register_client(self, name: str, client: BaseAIClient):
        """Manually register a client instance."""
        self._clients[name] = client

    def get_client(self, name: str) -> Optional[BaseAIClient]:
        """Get a registered client by name."""
        return self._clients.get(name)

    async def close_all_clients(self):
        """Close all client connections."""
        # For OpenAI clients, there's no explicit close method, but we could add that if needed
        self._clients.clear()

    def _get_api_key_from_env(self) -> Optional[str]:
        """Get Gemini API key from environment variables."""
        import os
        return os.getenv("GEMINI_API_KEY")


# Global factory instance for singleton access
_factory_instance: Optional[AIClientFactory] = None


async def get_ai_client_factory() -> AIClientFactory:
    """Get the global AI client factory instance (Gemini-backed)."""
    global _factory_instance
    if _factory_instance is None:
        settings = get_settings()
        _factory_instance = AIClientFactory(
            api_key=settings.GEMINI_API_KEY,
        )
    return _factory_instance


async def get_openai_client(model: str = "gemini-2.0-flash") -> OpenAIClient:
    """Get a Gemini-backed client instance (OpenAI-compatible interface)."""
    factory = await get_ai_client_factory()
    return factory.get_or_create_client("openai", model)
