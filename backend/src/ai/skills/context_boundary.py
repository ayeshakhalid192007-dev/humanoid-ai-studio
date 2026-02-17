"""Context Boundary skill module."""
import re
from typing import List

from ..base import BaseSkill, SkillContext


class ContextBoundarySkill(BaseSkill):
    """Skill to enforce strict context boundaries and prevent prompt injection."""

    def get_name(self) -> str:
        return "context_boundary"

    def get_phase(self) -> "SkillPhase":
        return "pre"  # This is a pre-processing skill

    async def pre_process(self, context: SkillContext) -> SkillContext:
        """
        Sanitize inputs to prevent prompt injection and enforce context boundaries.
        """
        # Sanitize user message against injection patterns
        sanitized_message = self._sanitize_user_message(context.user_message)

        # Update context with sanitized content
        context.user_message = sanitized_message

        # Verify agent type is valid for current context
        context.skill_results.append({
            "skill": self.get_name(),
            "phase": "pre",
            "status": "success",
            "duration_ms": 0,  # Will be updated by orchestrator
        })

        return context

    def _sanitize_user_message(self, message: str) -> str:
        """
        Clean the user message to prevent prompt injection.
        """
        if not message:
            return message

        # Remove common prompt injection sequences
        sanitized = re.sub(r'(?i)system:', '[REDACTED]', message)
        sanitized = re.sub(r'(?i)user:', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)assistant:', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)ignore.*previous.*instructions', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)you.*are.*now.*', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)forget.*previous', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)disregard.*prior', '[REDACTED]', sanitized)

        # Look for and redact attempts to change the system instructions
        sanitized = re.sub(r'(?i)never.*say.*that.*', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)don\'t.*inform.*about', '[REDACTED]', sanitized)

        # Prevent attempts to view the full prompt
        sanitized = re.sub(r'(?i)show.*full.*prompt', '[REDACTED]', sanitized)
        sanitized = re.sub(r'(?i)view.*entire.*instructions', '[REDACTED]', sanitized)

        return sanitized

    def _validate_content_boundary(self, content: str, agent_type: str) -> bool:
        """
        Validate that content is appropriate for the agent type.
        """
        # In a more sophisticated implementation, this would check if content
        # is relevant to the agent's purpose
        return True