"""
Gemini-compatible AsyncOpenAI client factory.

Gemini exposes an OpenAI-compatible REST API, so we reuse the openai
Python library — just swap the base_url and api_key.

Usage:
    from ..ai.gemini_client import get_gemini_client
    client = get_gemini_client()
    response = await client.chat.completions.create(...)
"""
from openai import AsyncOpenAI
from ..config import get_settings


def get_gemini_client() -> AsyncOpenAI:
    """
    Return an AsyncOpenAI client pointed at Gemini's OpenAI-compatible endpoint.
    The same openai SDK methods (chat.completions.create, stream=True, etc.) work unchanged.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url=settings.GEMINI_BASE_URL,
    )
