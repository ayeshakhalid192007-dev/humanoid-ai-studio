"""
Native Google GenAI async client factory.

Uses google-genai SDK directly — no OpenAI-compat shim.

Usage:
    from ..ai.gemini_client import get_gemini_client
    client = get_gemini_client()          # google.genai.Client
    # async call:
    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=[...],
        config=types.GenerateContentConfig(...)
    )
"""
from google import genai
from ..config import get_settings


def get_gemini_client() -> genai.Client:
    """
    Return a native google-genai Client.
    Use client.aio.* for async operations.
    """
    settings = get_settings()
    return genai.Client(api_key=settings.GEMINI_API_KEY)
