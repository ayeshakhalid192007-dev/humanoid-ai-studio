"""
Chat Session Management API

Provides endpoints for:
- Creating chat sessions
- Retrieving conversation history
- Managing session lifecycle

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from .auth import get_optional_user, get_user_id_from_session, AuthenticatedUser
from ..db.neon_client import NeonClient, get_neon_client
from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(prefix="/chat/sessions", tags=["Sessions"])


# ===========================================================================
# Request/Response Models
# ===========================================================================

class CreateSessionRequest(BaseModel):
    """Request to create a new chat session."""
    metadata: Optional[dict] = Field(
        default=None,
        description="Optional metadata (user-agent, browser info, etc.)"
    )


class CreateSessionResponse(BaseModel):
    """Response after creating a session."""
    session_id: str = Field(..., description="UUID of the created session")
    created_at: datetime = Field(..., description="Session creation timestamp")
    user_id: Optional[str] = Field(None, description="Associated user ID if authenticated")


class ConversationTurn(BaseModel):
    """A single conversation turn."""
    turn_id: int = Field(..., description="Sequential turn number")
    query: str = Field(..., description="User's question")
    response: str = Field(..., description="Assistant's response")
    created_at: datetime = Field(..., description="Turn timestamp")
    citations: Optional[List[dict]] = Field(None, description="Citations used")


class SessionHistoryResponse(BaseModel):
    """Response containing session history."""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_active_at: datetime
    turn_count: int
    turns: List[ConversationTurn]


class SessionSummary(BaseModel):
    """Summary of a chat session."""
    session_id: str
    created_at: datetime
    last_active_at: datetime
    turn_count: int
    preview: Optional[str] = Field(None, description="Preview of last message")


class ListSessionsResponse(BaseModel):
    """Response listing user's sessions."""
    sessions: List[SessionSummary]
    total: int
    page: int
    page_size: int


# ===========================================================================
# Session Storage (In-Memory for Demo, Neon for Production)
# ===========================================================================

# In-memory session store for demo mode
_demo_sessions: dict = {}


async def _get_neon() -> Optional[NeonClient]:
    """Get Neon client singleton if not in mock mode."""
    if settings.MOCK_MODE:
        return None
    return await get_neon_client()


# ===========================================================================
# Endpoints
# ===========================================================================

@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    user_id: Optional[str] = Depends(get_user_id_from_session)
):
    """
    Create a new chat session.

    If authenticated, associates session with user.
    If anonymous, creates standalone session.
    """
    session_id = str(uuid4())
    now = datetime.utcnow()

    if settings.MOCK_MODE:
        # Demo mode - store in memory
        _demo_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": now,
            "last_active_at": now,
            "metadata": request.metadata or {},
            "turns": []
        }
        logger.info(f"Created demo session: {session_id}")
    else:
        # Production mode - store in Neon
        client = await _get_neon()
        await client.create_or_update_session(
            session_id=UUID(session_id),
            metadata={
                "user_id": user_id,
                **(request.metadata or {})
            }
        )

    return CreateSessionResponse(
        session_id=session_id,
        created_at=now,
        user_id=user_id
    )


@router.get("/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: str,
    user_id: Optional[str] = Depends(get_user_id_from_session),
    limit: int = Query(default=50, ge=1, le=100, description="Max turns to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination")
):
    """
    Get conversation history for a session.

    Returns turns in chronological order with pagination.
    """
    if settings.MOCK_MODE:
        # Demo mode
        session = _demo_sessions.get(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Verify ownership if user_id provided
        if user_id and session.get("user_id") and session["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )

        turns = session.get("turns", [])[offset:offset + limit]

        return SessionHistoryResponse(
            session_id=session_id,
            user_id=session.get("user_id"),
            created_at=session["created_at"],
            last_active_at=session["last_active_at"],
            turn_count=len(session.get("turns", [])),
            turns=[
                ConversationTurn(
                    turn_id=i + offset + 1,
                    query=t["query"],
                    response=t["response"],
                    created_at=t["created_at"],
                    citations=t.get("citations")
                )
                for i, t in enumerate(turns)
            ]
        )
    else:
        # Production mode
        client = await _get_neon()
        session = await client.get_session(UUID(session_id))
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Get conversation turns
        turns = await client.get_conversation_turns(
            session_id=UUID(session_id),
            limit=limit,
            offset=offset
        )

        return SessionHistoryResponse(
            session_id=session_id,
            user_id=session.get("metadata", {}).get("user_id"),
            created_at=session["created_at"],
            last_active_at=session["last_active_at"],
            turn_count=len(turns),
            turns=[
                ConversationTurn(
                    turn_id=t["turn_id"],
                    query=t["query"],
                    response=t["response"],
                    created_at=t["created_at"],
                    citations=t.get("citations")
                )
                for t in turns
            ]
        )


@router.get("", response_model=ListSessionsResponse)
async def list_user_sessions(
    user: AuthenticatedUser = Depends(get_optional_user),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page")
):
    """
    List sessions for the authenticated user.

    Returns sessions sorted by last activity (most recent first).
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to list sessions"
        )

    offset = (page - 1) * page_size

    if settings.MOCK_MODE:
        # Filter demo sessions by user
        user_sessions = [
            s for s in _demo_sessions.values()
            if s.get("user_id") == user.user_id
        ]
        user_sessions.sort(key=lambda x: x["last_active_at"], reverse=True)

        paginated = user_sessions[offset:offset + page_size]

        return ListSessionsResponse(
            sessions=[
                SessionSummary(
                    session_id=s["session_id"],
                    created_at=s["created_at"],
                    last_active_at=s["last_active_at"],
                    turn_count=len(s.get("turns", [])),
                    preview=s["turns"][-1]["query"][:50] if s.get("turns") else None
                )
                for s in paginated
            ],
            total=len(user_sessions),
            page=page,
            page_size=page_size
        )
    else:
        # Production mode
        client = await _get_neon()
        # Query sessions for user
        async with client.pool.acquire() as conn:
            total = await conn.fetchval(
                """
                SELECT COUNT(*) FROM chat_sessions
                WHERE metadata->>'user_id' = $1
                """,
                user.user_id
            )

            rows = await conn.fetch(
                """
                SELECT session_id, created_at, last_active_at, metadata
                FROM chat_sessions
                WHERE metadata->>'user_id' = $1
                ORDER BY last_active_at DESC
                LIMIT $2 OFFSET $3
                """,
                user.user_id,
                page_size,
                offset
            )

        return ListSessionsResponse(
            sessions=[
                SessionSummary(
                    session_id=str(r["session_id"]),
                    created_at=r["created_at"],
                    last_active_at=r["last_active_at"],
                    turn_count=0,  # Would need join for accurate count
                    preview=None
                )
                for r in rows
            ],
            total=total or 0,
            page=page,
            page_size=page_size
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    user_id: Optional[str] = Depends(get_user_id_from_session)
):
    """
    Delete/end a chat session.

    Removes session and all associated conversation turns.
    """
    if settings.MOCK_MODE:
        session = _demo_sessions.get(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Verify ownership
        if user_id and session.get("user_id") and session["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this session"
            )

        del _demo_sessions[session_id]
        logger.info(f"Deleted demo session: {session_id}")
    else:
        client = await _get_neon()
        # Delete conversation turns first (foreign key constraint)
        async with client.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM conversation_turns WHERE session_id = $1",
                UUID(session_id)
            )
            result = await conn.execute(
                "DELETE FROM chat_sessions WHERE session_id = $1",
                UUID(session_id)
            )
            if result == "DELETE 0":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session {session_id} not found"
                )

    return None


# ===========================================================================
# Helper for Chat API Integration
# ===========================================================================

async def add_turn_to_session(
    session_id: str,
    query: str,
    response: str,
    citations: Optional[List[dict]] = None
) -> None:
    """
    Add a conversation turn to a session.

    Called by the chat endpoint after generating a response.

    Args:
        session_id: Session UUID
        query: User's question
        response: Assistant's answer
        citations: Optional citation list
    """
    now = datetime.utcnow()

    if settings.MOCK_MODE:
        if session_id not in _demo_sessions:
            # Auto-create session if doesn't exist
            _demo_sessions[session_id] = {
                "session_id": session_id,
                "user_id": None,
                "created_at": now,
                "last_active_at": now,
                "metadata": {},
                "turns": []
            }

        _demo_sessions[session_id]["turns"].append({
            "query": query,
            "response": response,
            "created_at": now,
            "citations": citations
        })
        _demo_sessions[session_id]["last_active_at"] = now
    else:
        client = await _get_neon()
        await client.insert_conversation_turn(
            session_id=UUID(session_id),
            query=query,
            response=response,
            retrieved_chunks=[],
            metadata={"citations": citations}
        )
