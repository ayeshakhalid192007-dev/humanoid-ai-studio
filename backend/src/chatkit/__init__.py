"""
ChatKit Integration Module

Provides OpenAI ChatKit-based conversational orchestration with:
- Tool-based RAG retrieval
- Streaming response support
- Dual answering modes (full-book / selected-text)

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from .agent import ChatKitAgent
from .tools import RAGTools
from .streaming import StreamingHandler
from .server import PhysicalAIChatKitServer, RequestContext
from .context_injector import ContextInjector, ConversationContext

__all__ = ["ChatKitAgent", "RAGTools", "StreamingHandler", "PhysicalAIChatKitServer", "RequestContext", "ContextInjector", "ConversationContext"]
