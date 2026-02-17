"""Prompt registry module for centralized prompt management."""
import hashlib
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import yaml


@dataclass
class PromptTemplate:
    """Data class for a prompt template."""
    agent_type: str
    content: str
    version: str
    model: str
    temperature: float
    max_tokens: int


class PromptRegistry:
    """Loads prompt templates from disk. Computes version hash for cache invalidation."""

    def __init__(self, templates_dir: Path = None):
        self._templates: Dict[str, PromptTemplate] = {}
        if templates_dir is None:
            # Default to the templates directory in the same package
            templates_dir = Path(__file__).parent / "templates"
        self._load_templates(templates_dir)

    def _load_templates(self, templates_dir: Path):
        """Load all prompt templates from the specified directory."""
        for template_file in templates_dir.glob("*.md"):
            template = self._load_template(template_file)
            self._templates[template.agent_type] = template

    def _load_template(self, file_path: Path) -> PromptTemplate:
        """Load a single prompt template from file."""
        content = file_path.read_text(encoding="utf-8")

        # Extract YAML frontmatter if present
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                body_content = parts[2]
                try:
                    metadata = yaml.safe_load(yaml_content) or {}
                except yaml.YAMLError:
                    metadata = {
                        "agent_type": file_path.stem,
                        "model": "gpt-4o-mini",
                        "temperature": 0.3,
                        "max_tokens": 16000
                    }
            else:
                # Invalid frontmatter format, treat as content
                metadata = {"agent_type": file_path.stem}
                body_content = content
        else:
            # No frontmatter, default values
            metadata = {"agent_type": file_path.stem}
            body_content = content

        # Calculate content version (SHA-256 hash of content, first 16 hex chars)
        content_hash = hashlib.sha256(body_content.encode("utf-8")).hexdigest()
        version = content_hash[:16]

        agent_type = metadata.get("agent_type", file_path.stem)
        model = metadata.get("model", "gpt-4o-mini")
        temperature = metadata.get("temperature", 0.3)
        max_tokens = metadata.get("max_tokens", 16000)

        return PromptTemplate(
            agent_type=agent_type,
            content=body_content,
            version=version,  # Use calculated version
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def get_template(self, agent_type: str) -> Optional[PromptTemplate]:
        """Returns template with content and version hash."""
        return self._templates.get(agent_type)

    def get_version(self, agent_type: str) -> Optional[str]:
        """SHA-256 hash of template content (first 16 hex chars)."""
        template = self.get_template(agent_type)
        return template.version if template else None

    def list_templates(self) -> list[str]:
        """List all registered template agent types."""
        return list(self._templates.keys())