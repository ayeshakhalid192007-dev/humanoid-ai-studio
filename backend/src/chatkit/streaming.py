"""
Streaming Response Handler

Provides SSE (Server-Sent Events) streaming support for
real-time response delivery to clients.

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from typing import AsyncIterator, Dict, Any
import json
import asyncio

from starlette.responses import StreamingResponse


class StreamingHandler:
    """
    Handles conversion of async generators to SSE streams.

    SSE Format:
        data: {"type": "chunk", "content": "...", "metadata": {...}}

        data: {"type": "done", "content": "", "metadata": {...}}

    """

    @staticmethod
    def format_sse_event(data: Dict[str, Any], event_type: str = "message") -> str:
        """
        Format data as an SSE event.

        Args:
            data: Event data to send
            event_type: SSE event type

        Returns:
            Formatted SSE string
        """
        json_data = json.dumps(data, ensure_ascii=False)
        return f"event: {event_type}\ndata: {json_data}\n\n"

    @staticmethod
    async def create_sse_stream(
        generator: AsyncIterator[Dict[str, Any]],
        heartbeat_interval: float = 15.0
    ) -> AsyncIterator[str]:
        """
        Convert an async generator to an SSE stream with heartbeat.

        Args:
            generator: Async generator yielding response chunks
            heartbeat_interval: Seconds between heartbeat pings

        Yields:
            Formatted SSE strings
        """
        async def heartbeat():
            """Send periodic heartbeats to keep connection alive."""
            while True:
                await asyncio.sleep(heartbeat_interval)
                yield StreamingHandler.format_sse_event(
                    {"type": "heartbeat", "content": "", "metadata": {}},
                    "ping"
                )

        try:
            async for chunk in generator:
                yield StreamingHandler.format_sse_event(chunk, "message")

                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            # Client disconnected
            yield StreamingHandler.format_sse_event(
                {"type": "cancelled", "content": "", "metadata": {}},
                "close"
            )
        except Exception as e:
            # Send error event
            yield StreamingHandler.format_sse_event(
                {"type": "error", "content": str(e), "metadata": {}},
                "error"
            )

    @staticmethod
    def create_streaming_response(
        generator: AsyncIterator[Dict[str, Any]],
        headers: Dict[str, str] = None
    ) -> StreamingResponse:
        """
        Create a FastAPI StreamingResponse for SSE.

        Args:
            generator: Async generator yielding response chunks
            headers: Additional headers to include

        Returns:
            StreamingResponse configured for SSE
        """
        default_headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }

        if headers:
            default_headers.update(headers)

        return StreamingResponse(
            StreamingHandler.create_sse_stream(generator),
            media_type="text/event-stream",
            headers=default_headers
        )


class StreamBuffer:
    """
    Buffer for accumulating streamed content with metadata tracking.

    Useful for:
    - Aggregating full response for logging
    - Tracking token counts
    - Building complete response after streaming
    """

    def __init__(self):
        self.content_buffer: str = ""
        self.tool_calls: list = []
        self.citations: list = []
        self.metadata: Dict[str, Any] = {}
        self.chunk_count: int = 0
        self.is_complete: bool = False

    def add_chunk(self, chunk: Dict[str, Any]) -> None:
        """
        Add a chunk to the buffer.

        Args:
            chunk: Chunk dict with type, content, metadata
        """
        chunk_type = chunk.get("type", "")
        content = chunk.get("content", "")
        metadata = chunk.get("metadata", {})

        if chunk_type == "chunk":
            self.content_buffer += content
            self.chunk_count += 1

        elif chunk_type == "tool_call":
            self.tool_calls.append({
                "name": content,
                "arguments": metadata.get("arguments", {})
            })

        elif chunk_type == "citation":
            self.citations.append({
                "section": content,
                **metadata
            })

        elif chunk_type == "done":
            self.is_complete = True
            self.metadata.update(metadata)

    def get_complete_response(self) -> Dict[str, Any]:
        """
        Get the complete buffered response.

        Returns:
            Dict with full response data
        """
        return {
            "answer": self.content_buffer,
            "citations": self.citations,
            "tool_calls": self.tool_calls,
            "chunk_count": self.chunk_count,
            "is_complete": self.is_complete,
            "metadata": self.metadata
        }
