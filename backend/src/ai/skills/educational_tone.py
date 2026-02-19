"""Educational Tone Control skill module."""
from typing import Dict, Any

from ..base import BaseSkill, SkillContext


class EducationalToneSkill(BaseSkill):
    """Skill to control educational tone appropriate for target audience."""

    def get_name(self) -> str:
        return "educational_tone"

    def get_phase(self) -> "SkillPhase":
        return "pre"  # This is a pre-processing skill

    async def pre_process(self, context: SkillContext) -> SkillContext:
        """
        Adjust the system prompt to include educational tone instructions.
        """
        # Add educational tone instructions to system prompt based on agent type
        tone_instructions = self._get_tone_instructions(context.agent_type)

        if tone_instructions:
            context.system_prompt += f"\n\n{tone_instructions}"

        context.skill_results.append({
            "skill": self.get_name(),
            "phase": "pre",
            "status": "success",
            "duration_ms": 0,  # Will be updated by orchestrator
        })

        return context

    def _get_tone_instructions(self, agent_type: str) -> str:
        """
        Return tone control instructions based on the agent type.
        """
        if agent_type == "personalization":
            return """
EDUCATIONAL TONE GUIDELINES:
- Adapt explanations to match student's background and proficiency level
- For beginners: Use simpler analogies, more verbose explanations, avoid advanced terms without definition
- For intermediate: Use standard educational language with brief context
- For advanced: Use concise technical explanations, fewer basic explanations
- Maintain supportive, encouraging tone throughout
- Use clear transitions between concepts
- Connect new concepts to student's known background when possible
"""
        elif agent_type == "translation":
            # For translation, we'll focus on preserving educational quality in the target language
            return """
EDUCATIONAL TONE GUIDELINES:
- Maintain the pedagogical quality in the target language
- Preserve the instructor's supportive and educational tone
- Ensure technical concepts remain clearly explained
- Keep the language appropriate for educational content
"""
        elif agent_type == "rag_chat":
            # For chat, ensure educational responses
            return """
EDUCATIONAL TONE GUIDELINES:
- Provide educational, not just informational responses
- Explain concepts thoroughly, not just facts
- Use pedagogically sound language
- Offer clarifications when appropriate
- Maintain supportive, encouraging tone
- Acknowledge limitations when needed
"""
        else:  # Default or undefined agent types
            return """
EDUCATIONAL TONE GUIDELINES:
- Maintain a supportive, educational tone appropriate for curriculum content
- Explain concepts clearly with appropriate depth
- Use pedagogically sound language
"""