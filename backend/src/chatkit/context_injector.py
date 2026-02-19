"""
Context Injection System for ChatKit

This module provides mechanisms to inject page context, user information,
and other relevant data into ChatKit conversations for enhanced responses.

Author: Physical AI Platform Team
Date: 2026-02-18
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

from ..utils.logger import get_logger
from ..services.content_personalizer import ContentPersonalizer


@dataclass
class PageContext:
    """Represents context from a page that a user is viewing."""
    page_title: str
    page_url: str
    page_module: str  # e.g., "Module 1", "Lesson 2.1"
    page_section: str  # e.g., "URDF Introduction", "Launch Files"
    page_content_preview: str  # First few hundred characters of content
    timestamp: datetime


@dataclass
class UserContext:
    """Represents user-specific information."""
    user_id: str
    user_profile: Dict[str, Any]
    learning_history: Dict[str, Any]
    preferred_language: str = "en"
    expertise_level: str = "beginner"


@dataclass
class ConversationContext:
    """Combined context for a conversation."""
    page_context: Optional[PageContext] = None
    user_context: Optional[UserContext] = None
    selected_text: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None


class ContextInjector:
    """
    System for injecting contextual information into ChatKit conversations.

    This class:
    - Captures page context from frontend requests
    - Retrieves user profile information
    - Combines contexts appropriately
    - Formats contexts for injection into system prompts
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.personalizer = ContentPersonalizer()

    def extract_page_context(self, page_data: Dict[str, Any]) -> Optional[PageContext]:
        """
        Extract page context from frontend-provided page data.

        Args:
            page_data: Dictionary containing page information from frontend
                      Expected keys: title, url, module, section, contentPreview

        Returns:
            PageContext object or None if insufficient data
        """
        if not page_data:
            return None

        # Validate required fields
        required_fields = ['title', 'url', 'module', 'section']
        for field in required_fields:
            if field not in page_data or not page_data[field]:
                self.logger.warning(f"Missing required page context field: {field}")
                return None

        return PageContext(
            page_title=page_data.get('title', ''),
            page_url=page_data.get('url', ''),
            page_module=page_data.get('module', ''),
            page_section=page_data.get('section', ''),
            page_content_preview=page_data.get('contentPreview', '')[:500],  # Limit length
            timestamp=datetime.utcnow()
        )

    def extract_user_context(self, user_profile: Dict[str, Any]) -> Optional[UserContext]:
        """
        Extract user context from profile data.

        Args:
            user_profile: User profile information from authentication system

        Returns:
            UserContext object or None if insufficient data
        """
        if not user_profile:
            return None

        return UserContext(
            user_id=user_profile.get('id', ''),
            user_profile=user_profile,
            learning_history=user_profile.get('learning_history', {}),
            preferred_language=user_profile.get('preferred_language', 'en'),
            expertise_level=user_profile.get('expertise_level', 'beginner')
        )

    def create_conversation_context(
        self,
        page_data: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        selected_text: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """
        Create a comprehensive conversation context.

        Args:
            page_data: Page information from frontend
            user_profile: User profile information
            selected_text: Text selected/highlighted by user
            additional_metadata: Additional context metadata

        Returns:
            ConversationContext object with all available contexts
        """
        page_context = self.extract_page_context(page_data) if page_data else None
        user_context = self.extract_user_context(user_profile) if user_profile else None

        return ConversationContext(
            page_context=page_context,
            user_context=user_context,
            selected_text=selected_text,
            additional_metadata=additional_metadata or {}
        )

    def format_system_prompt(self, context: ConversationContext) -> str:
        """
        Format context information into a system prompt for the ChatKit agent.

        Args:
            context: ConversationContext containing all relevant context

        Returns:
            Formatted system prompt string
        """
        prompt_parts = []

        # Add user-specific context
        if context.user_context:
            expertise_level = context.user_context.expertise_level
            preferred_language = context.user_context.preferred_language

            expert_prompts = {
                'beginner': (
                    "Explain concepts with simple analogies and step-by-step breakdowns. "
                    "Provide clear examples and avoid jargon."
                ),
                'intermediate': (
                    "Provide explanations with appropriate technical depth. "
                    "Include relevant examples but assume some baseline knowledge."
                ),
                'advanced': (
                    "Deliver technical explanations with industry-standard terminology. "
                    "Focus on nuances and deeper implications without extensive explanation of basics."
                )
            }

            prompt_parts.append(f"USER CONTEXT:")
            prompt_parts.append(f"- User expertise level: {expertise_level}")
            prompt_parts.append(f"- Preferred language: {preferred_language}")
            prompt_parts.append(f"- Guidelines: {expert_prompts.get(expertise_level, expert_prompts['beginner'])}")

        # Add page context
        if context.page_context:
            prompt_parts.append(f"\nCURRENT PAGE CONTEXT:")
            prompt_parts.append(f"- Title: {context.page_context.page_title}")
            prompt_parts.append(f"- Module: {context.page_context.page_module}")
            prompt_parts.append(f"- Section: {context.page_context.page_section}")
            prompt_parts.append(f"- URL: {context.page_context.page_url}")

            if context.page_context.page_content_preview:
                prompt_parts.append(f"- Content preview: {context.page_context.page_content_preview[:200]}...")

        # Add selection context
        if context.selected_text:
            prompt_parts.append(f"\nUSER SELECTION CONTEXT:")
            prompt_parts.append(f"- Selected text: {context.selected_text[:500]}...")
            prompt_parts.append(f"- Task: Answer questions specifically about the selected text")

        # Add additional context from metadata
        if context.additional_metadata:
            prompt_parts.append(f"\nADDITIONAL CONTEXT:")
            for key, value in context.additional_metadata.items():
                prompt_parts.append(f"- {key}: {value}")

        # Add standard instructions
        prompt_parts.append(f"\nCONVERSATION INSTRUCTIONS:")
        prompt_parts.append(f"- Base responses ONLY on provided context and curriculum knowledge")
        prompt_parts.append(f"- Cite relevant sections from the curriculum when providing information")
        prompt_parts.append(f"- If user has selected text, prioritize answering about that specific text")
        prompt_parts.append(f"- If information is insufficient from context, acknowledge and suggest related topics")

        return "\n".join(prompt_parts)

    def get_context_hash(self, context: ConversationContext) -> str:
        """
        Generate a hash for the context to identify unique context combinations.

        Args:
            context: ConversationContext to hash

        Returns:
            Hash string for context identification/lookup
        """
        context_data = {
            'page_title': context.page_context.page_title if context.page_context else '',
            'user_id': context.user_context.user_id if context.user_context else '',
            'selected_text_hash': hashlib.md5(context.selected_text.encode()).hexdigest() if context.selected_text else '',
            'metadata_keys': list(context.additional_metadata.keys()) if context.additional_metadata else []
        }

        context_json = json.dumps(context_data, sort_keys=True)
        return hashlib.md5(context_json.encode()).hexdigest()

    async def inject_context_to_agent(self, agent, context: ConversationContext):
        """
        Inject the conversation context into a ChatKit agent.

        Args:
            agent: ChatKitAgent instance to inject context into
            context: ConversationContext to inject
        """
        # Format and inject system context
        system_prompt = self.format_system_prompt(context)

        # Remove any existing context messages from the agent's message history
        original_messages = agent.state.messages
        filtered_messages = [
            msg for msg in original_messages
            if not (msg.role == "system" and "CONTEXT" in msg.content.upper())
        ]

        # Reset the agent's messages to just the original system prompt and user messages
        agent.state.messages = []

        # Rebuild messages keeping the original system prompt (first message)
        if original_messages:
            agent._init_system_prompt()  # Reinitialize with basic system prompt
            # Add back the user messages and assistant responses, but inject context
            for msg in filtered_messages[1:]:  # Skip the original system prompt we'll replace
                agent.state.messages.append(msg)

        # Add the new context as a system message
        from .agent import ConversationMessage
        context_message = ConversationMessage(
            role="system",
            content=system_prompt if system_prompt.strip() else "No context provided."
        )

        # Insert context message after the initial system message
        if len(agent.state.messages) >= 1:
            agent.state.messages.insert(1, context_message)
        else:
            agent.state.messages.append(context_message)

    async def personalize_context_response(self, context: ConversationContext, response: str) -> str:
        """
        Apply personalization to a response based on user context.

        Args:
            context: ConversationContext with user information
            response: Original response text

        Returns:
            Personalized response based on user context
        """
        if not context.user_context:
            return response

        # Use content personalizer for expertise-level adaptation
        expertise_level = context.user_context.expertise_level
        if expertise_level in ['beginner', 'intermediate', 'advanced']:
            # This would typically call the personalization service
            # For now, we'll just return the response as is
            # In a real implementation, we'd adjust complexity based on user_level
            pass

        # Apply language translation if needed
        if context.user_context.preferred_language != 'en':
            # This would call the translation service
            # For now, just return the response
            pass

        return response