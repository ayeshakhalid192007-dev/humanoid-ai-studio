"""Code Block Detection skill module."""
import re
from typing import List

from ..base import BaseSkill, SkillContext


class CodeBlockDetectionSkill(BaseSkill):
    """Skill to detect and preserve code blocks during transformations."""

    def get_name(self) -> str:
        return "code_block_detection"

    def get_phase(self) -> "SkillPhase":
        return "both"  # This skill operates in pre-processing (to identify blocks) and post-processing (to verify preservation)

    async def pre_process(self, context: SkillContext) -> SkillContext:
        """
        Extract code blocks from the original content to preserve during transformation.
        """
        original_code_blocks = self._extract_code_blocks(context.original_content)
        context.original_code_blocks = original_code_blocks

        # Add the count to the system prompt so agent knows what to preserve
        context.skill_results.append({
            "skill": self.get_name(),
            "phase": "pre",
            "status": "success",
            "duration_ms": 0,  # Will be updated by orchestrator
            "details": f"Detected {len(original_code_blocks)} code blocks to preserve"
        })

        return context

    async def post_process(self, context: SkillContext) -> SkillContext:
        """
        Validate that code blocks from original content are preserved in final response.
        """
        if not context.ai_response:
            return context

        final_code_blocks = self._extract_code_blocks(context.ai_response)

        # Check if all original code blocks are preserved
        missing_blocks = []
        for orig_block in context.original_code_blocks:
            found = False
            for final_block in final_code_blocks:
                if self._code_blocks_match(orig_block, final_block):
                    found = True
                    break
            if not found:
                missing_blocks.append(orig_block)

        if missing_blocks:
            context.skill_results.append({
                "skill": self.get_name(),
                "phase": "post",
                "status": "warning",  # Not critical failure, but a warning
                "duration_ms": 0,  # Will be updated by orchestrator
                "details": f"Missing {len(missing_blocks)} code blocks in final output"
            })
        else:
            context.skill_results.append({
                "skill": self.get_name(),
                "phase": "post",
                "status": "success",
                "duration_ms": 0,  # Will be updated by orchestrator
                "details": f"All {len(context.original_code_blocks)} code blocks preserved"
            })

        return context

    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from markdown content."""
        if not content:
            return []

        code_blocks = []
        lines = content.split('\n')
        in_code_block = False
        current_block = []

        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    # End of code block
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    current_block.append(line)
            elif in_code_block:
                current_block.append(line)

        # Handle case where content ends while still in a code block
        if in_code_block and current_block:
            code_blocks.append('\n'.join(current_block))

        return code_blocks

    def _code_blocks_match(self, block1: str, block2: str) -> bool:
        """Check if two code blocks match (ignoring leading/trailing whitespace)."""
        # This is a basic check - in a more advanced implementation, we might need
        # to be more stringent or consider formatting differences
        return block1.strip() == block2.strip()