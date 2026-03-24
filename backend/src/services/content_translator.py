"""
Content Translator Service

Generates Urdu translations of chapter content using OpenAI.
Preserves Markdown formatting, leaves code blocks untouched,
and keeps technical terms in English.

Author: Physical AI Platform Team
Date: 2026-02-16
"""
from ..config import get_settings
from ..ai.gemini_client import get_gemini_client
from google.genai import types as genai_types


class ContentTranslator:
    """
    Translates chapter content to Urdu using Gemini.

    Preserves all Markdown formatting, code blocks, and technical terms.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = get_gemini_client()
        self.model = self.settings.OPENAI_CHAT_MODEL

        self.system_prompt = """You are an expert translator specializing in translating technical educational content from English to Urdu.

Your task is to translate robotics and AI curriculum content. Follow these rules STRICTLY:

1. Translate ALL prose text (paragraphs, headings, list items, table cells) to Urdu.
2. DO NOT translate code blocks (``` fenced blocks) — leave them COMPLETELY unchanged, including comments inside code.
3. DO NOT translate command-line examples, file paths, or variable names.
4. KEEP technical English terms as-is with Urdu transliteration in parentheses where helpful. Examples:
   - "ROS 2" stays as "ROS 2"
   - "node" stays as "node (نوڈ)"
   - "topic" stays as "topic (ٹاپک)"
   - "publisher" stays as "publisher (پبلشر)"
5. PRESERVE all Markdown formatting exactly:
   - Headings (#, ##, ###, etc.)
   - Lists (-, *, numbered)
   - Tables (| pipes and alignment)
   - Bold (**text**), italic (*text*)
   - Links [text](url)
   - Images ![alt](url)
6. PRESERVE all Markdown structure: heading hierarchy, section ordering, list nesting.
7. Output ONLY the translated content in Markdown format.
8. DO NOT add any introductory or concluding notes about the translation.
9. Write natural, fluent Urdu — not word-by-word translation.

CRITICAL: Your output must be ONLY the translated chapter content. No meta-commentary."""

    async def translate(self, chapter_content: str) -> str:
        """
        Translate chapter content to Urdu.

        Args:
            chapter_content: Original chapter Markdown (English)

        Returns:
            Urdu translated Markdown content
        """
        user_message = (
            f"Translate the following chapter content to Urdu:\n\n"
            f"{chapter_content}"
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=[genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=user_message)]
            )],
            config=genai_types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=16000,
                system_instruction=self.system_prompt,
            ),
        )

        content = response.text
        if not content:
            raise RuntimeError("Empty AI response from translation")
        return content
