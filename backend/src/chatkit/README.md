# ChatKit Integration for Physical AI Platform

## Overview

This package implements ChatKit-style conversational capabilities for the Physical AI platform, integrating with the existing AI Orchestrator and RAG system. The implementation provides educational conversational experiences with:

- Context-aware responses based on page content
- Text selection functionality for focused questions
- Seamless integration with user authentication
- Streaming responses via Server-Sent Events (SSE)

## Architecture

The ChatKit implementation follows these layers:

1. **Frontend Component** (`book/src/components/ChatKitWidget/`) - React UI component with text selection hooks
2. **API Layer** (`backend/src/api/chatkit.py`) - ChatKit protocol endpoints
3. **Context Injection** (`backend/src/chatkit/context_injector.py`) - Page and user context integration
4. **Agent Implementation** (`backend/src/chatkit/agent.py`) - Core conversational agent
5. **Tool Integration** (`backend/src/chatkit/tools.py`) - RAG and retrieval tools
6. **Server Interface** (`backend/src/chatkit/server.py`) - ChatKit protocol compatibility

## API Endpoints

- `POST /api/chatkit/threads` - Create new conversation thread
- `GET /api/chatkit/threads/{thread_id}` - Get thread information
- `DELETE /api/chatkit/threads/{thread_id}` - Delete conversation thread
- `POST /api/chatkit/threads/{thread_id}/messages` - Send message and receive response
- `GET /api/chatkit/threads/{thread_id}/messages` - List messages (placeholder)

Also available through the AI Orchestrator:

- `POST /api/ai/chatkit` - Main ChatKit endpoint through orchestrator
- `POST /api/ai/chatkit/stream` - Streaming ChatKit endpoint through orchestrator

## Usage Examples

### Frontend Integration

```tsx
<ChatKitWidget
  pageContext={{
    title: "Module 1: ROS2 Foundations",
    url: "/docs/module-1/ros2-foundations",
    moduleId: "module-1",
    sectionTitle: "Nodes and Topics"
  }}
/>
```

### Context Injection

The system automatically injects:
- Current page title and URL
- Selected text from user interactions
- User profile information (if authenticated)
- Page module and section context
- Learning history (if available)

## Authentication

The ChatKit implementation uses Better Auth for authentication, with session tokens automatically passed via cookies. Unauthenticated users receive appropriately contextualized responses without user-specific personalization.

## Thread Management

- Thread persistence via session IDs
- Automatic context injection per thread
- Integration with existing conversation logging
- Support for long-running conversations with context continuity

## Performance and Caching

- RAG caching via Neon DB
- Conversation history optimization
- Streaming performance for real-time responses
- Rate limiting per user/session

## Error Handling

The system provides:
- Graceful fallbacks for service outages
- Error messages in ChatKit-compatible format
- Client-side retry mechanisms
- Detailed server logging for debugging

## Migration

The implementation maintains backward compatibility with existing chat endpoints while providing enhanced ChatKit functionality alongside the AI Orchestrator. The `/chat/v2` endpoint supports both legacy behavior and new ChatKit features via feature flags.