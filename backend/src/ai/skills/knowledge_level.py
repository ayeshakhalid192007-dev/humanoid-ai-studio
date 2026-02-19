"""Knowledge Level Adjustment skill module."""
from typing import Dict, Any

from ..base import BaseSkill, SkillContext


class KnowledgeLevelSkill(BaseSkill):
    """Skill to adapt content complexity based on user's declared proficiency level."""

    def get_name(self) -> str:
        return "knowledge_level"

    def get_phase(self) -> "SkillPhase":
        return "pre"  # This is a pre-processing skill

    async def pre_process(self, context: SkillContext) -> SkillContext:
        """
        Adjust the system prompt to account for user's knowledge level.
        """
        # The user profile information should contain knowledge level information
        if context.metadata and "user_profile" in context.metadata:
            user_profile = context.metadata["user_profile"]
        else:
            # If the profile isn't already in metadata, we may need to get it from the request context
            # In the orchestrator, this should be passed in properly
            user_profile = context.metadata.get("user_profile", {}) if context.metadata else {}

        # Modify the system prompt to add knowledge level instructions
        knowledge_level_instructions = self._get_knowledge_level_instructions(user_profile)

        if knowledge_level_instructions:
            context.system_prompt += f"\n\n{knowledge_level_instructions}"

        context.skill_results.append({
            "skill": self.get_name(),
            "phase": "pre",
            "status": "success",
            "duration_ms": 0,  # Will be updated by orchestrator
        })

        return context

    def _get_knowledge_level_instructions(self, user_profile: Dict[str, Any]) -> str:
        """
        Return knowledge-level adjustment instructions based on user profile.
        """
        software_background = user_profile.get("software_background", "Not specified")
        hardware_background = user_profile.get("hardware_background", "Not specified")
        robotics_knowledge = user_profile.get("robotics_knowledge", "beginner")  # beginner, intermediate, advanced

        # Based on the knowledge level, create appropriate instructions
        if robotics_knowledge == "beginner":
            level_instructions = """
USER KNOWLEDGE PROFILE:
- Software Background: {software_back}
- Hardware Background: {hardware_back}
- Robotics Knowledge Level: Beginner
ADAPTATION INSTRUCTIONS:
- Provide detailed explanations with step-by-step breakdowns
- Use analogies related to user's background when possible (e.g., if user has Python background, reference Python concepts in robotics analogies)
- Explain technical terms before using them
- Include more examples and visual references
- Slow down explanations, add context
""".format(software_back=software_background, hardware_back=hardware_background)

        elif robotics_knowledge == "intermediate":
            level_instructions = """
USER KNOWLEDGE PROFILE:
- Software Background: {software_back}
- Hardware Background: {hardware_back}
- Robotics Knowledge Level: Intermediate
ADAPTATION INSTRUCTIONS:
- Provide standard technical explanations with brief context
- Use appropriate technical terminology
- Reference user's background when relevant
- Assume foundational knowledge but explain complex topics
""".format(software_back=software_background, hardware_back=hardware_background)

        elif robotics_knowledge == "advanced":
            level_instructions = """
USER KNOWLEDGE PROFILE:
- Software Background: {software_back}
- Hardware Background: {hardware_back}
- Robotics Knowledge Level: Advanced
ADAPTATION INSTRUCTIONS:
- Provide concise technical explanations, skip basics
- Use advanced technical terminology without extensive explanation
- Focus on complex applications and concepts
- Reference user's background directly without basic analogies
""".format(software_back=software_background, hardware_back=hardware_background)

        else:  # Default to beginner if level is not specified
            level_instructions = """
USER KNOWLEDGE PROFILE:
- Software Background: {software_back}
- Hardware Background: {hardware_back}
- Robotics Knowledge Level: Beginner (default)
ADAPTATION INSTRUCTIONS:
- Provide detailed explanations with step-by-step breakdowns
- Use analogies related to user's background when possible
- Explain technical terms before using them
- Include more examples and visual references
""".format(software_back=software_background, hardware_back=hardware_background)

        return level_instructions