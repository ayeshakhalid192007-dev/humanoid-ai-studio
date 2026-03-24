"""
Content Personalizer Service

Generates personalized chapter content using OpenAI based on user profile.
Adapts explanations and examples while preserving chapter structure.

Author: Physical AI Platform Team
Date: 2026-02-16
"""
from typing import Dict, Any

from ..config import get_settings
from ..ai.gemini_client import get_gemini_client
from google.genai import types as genai_types


class ContentPersonalizer:
    """
    Personalizes chapter content based on user profile data.

    Uses Gemini to adapt explanations and examples while
    preserving headings, sections, and ordering.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = get_gemini_client()
        self.model = self.settings.OPENAI_CHAT_MODEL

        self.system_prompt = """You are an expert educational content personalizer for a Physical AI & Humanoid Robotics curriculum.

Your task is to adapt chapter content based on the student's background profile. Follow these rules STRICTLY:

1. PRESERVE the exact chapter structure: all headings, sections, and their ordering must remain unchanged.
2. ADAPT explanations based on the student's knowledge level:
   - For beginners: use simpler language, more analogies, step-by-step breakdowns
   - For intermediate: use standard technical language with brief context
   - For advanced: use concise, technical explanations, skip basics
3. ADAPT examples based on the student's background:
   - Software background: reference their known languages/frameworks in examples
   - Hardware background: relate to their hardware experience level
4. DO NOT add new sections, headings, or concepts not in the original chapter.
5. DO NOT remove any sections or headings from the original.
6. DO NOT change code blocks - keep them exactly as they are.
7. DO NOT add introductory or concluding remarks about personalization.
8. Output ONLY the personalized chapter content in Markdown format.
9. PRESERVE all Markdown formatting: lists, tables, code blocks, bold, italic, links.

CRITICAL: Your output must be ONLY the adapted chapter content. No meta-commentary."""

    async def personalize(
        self,
        chapter_content: str,
        user_profile: Dict[str, str],
    ) -> str:
        """
        Generate personalized version of chapter content.

        Args:
            chapter_content: Original chapter Markdown
            user_profile: Dict with software_background, hardware_background, robotics_knowledge

        Returns:
            Personalized Markdown content
        """
        user_context = (
            f"Student Profile:\n"
            f"- Software Background: {user_profile.get('software_background', 'Not specified')}\n"
            f"- Hardware Background: {user_profile.get('hardware_background', 'Not specified')}\n"
            f"- Robotics Knowledge Level: {user_profile.get('robotics_knowledge', 'beginner')}\n"
        )

        user_message = (
            f"{user_context}\n"
            f"---\n\n"
            f"Personalize the following chapter content for this student:\n\n"
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
            raise RuntimeError("Empty AI response from personalization")
        return content
