"""Markdown Preservation skill module."""
import re
from typing import List

from ..base import BaseSkill, SkillContext


class MarkdownPreservationSkill(BaseSkill):
    """Skill to preserve markdown structure and formatting."""

    def get_name(self) -> str:
        return "markdown_preservation"

    def get_phase(self) -> "SkillPhase":
        return "post"  # This is a post-processing skill

    async def post_process(self, context: SkillContext) -> SkillContext:
        """
        Validate and preserve markdown structure after AI processing.
        """
        if not context.ai_response:
            return context

        # Extract headings from original content
        original_headings = self._extract_headings(context.original_content)
        new_headings = self._extract_headings(context.ai_response)

        # Check if structure is preserved
        # If not, try to fix structural issues
        if self._headings_different(original_headings, new_headings):
            context.skill_results.append({
                "skill": self.get_name(),
                "phase": "post",
                "status": "warning",  # Not an error, but structure differs
                "duration_ms": 0,  # Will be updated by orchestrator
                "details": f"Headings differ: {len(original_headings)} original vs {len(new_headings)} new",
            })
        else:
            context.skill_results.append({
                "skill": self.get_name(),
                "phase": "post",
                "status": "success",
                "duration_ms": 0,
            })

        # Return unchanged context - we're checking, not modifying in this basic implementation
        return context

    def _extract_headings(self, content: str) -> List[str]:
        """Extract heading hierarchy from markdown content."""
        if not content:
            return []

        headings = []
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#'):
                # Count the number of # symbols to get heading level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                # Extract the heading text (remove # and leading/trailing spaces)
                heading_text = stripped[level:].strip()
                if heading_text:
                    headings.append(f"{'#' * level} {heading_text}")
        return headings

    def _headings_different(self, original: List[str], new: List[str]) -> bool:
        """Check if heading structure differs between original and new content."""
        if len(original) != len(new):
            return True

        # Compare the heading structure more carefully
        for orig, new_heading in zip(original, new):
            # Extract only the heading level (number of #)
            orig_level = orig.count('#') if orig.startswith('#') else 0
            new_level = new_heading.count('#') if new_heading.startswith('#') else 0
            if orig_level != new_level:
                return True

        return False