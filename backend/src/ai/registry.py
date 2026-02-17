"""Agent and skill registries module."""
from typing import Dict, Type, Any, Optional
from .base import BaseAgent, BaseSkill


class AgentRegistry:
    """Registry for AI agents."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}

    def register_agent(self, agent_type: str, agent: BaseAgent) -> None:
        """Register an agent instance."""
        self._agents[agent_type] = agent

    def register_agent_class(self, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class for factory creation."""
        self._agent_classes[agent_type] = agent_class

    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get an agent by type."""
        return self._agents.get(agent_type)

    def list_agents(self) -> list[str]:
        """List all registered agent types."""
        return list(self._agents.keys())


class SkillRegistry:
    """Registry for AI skills."""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._skill_classes: Dict[str, Type[BaseSkill]] = {}

    def register_skill(self, skill_name: str, skill: BaseSkill) -> None:
        """Register a skill instance."""
        self._skills[skill_name] = skill

    def register_skill_class(self, skill_name: str, skill_class: Type[BaseSkill]) -> None:
        """Register a skill class for factory creation."""
        self._skill_classes[skill_name] = skill_class

    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """Get a skill by name."""
        return self._skills.get(skill_name)

    def list_skills(self) -> list[str]:
        """List all registered skill names."""
        return list(self._skills.keys())