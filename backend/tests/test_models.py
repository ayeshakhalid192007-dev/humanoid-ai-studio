"""
Unit tests for Pydantic models.

Tests:
- ChatRequest validation and sanitization
- ChatResponse structure
- Citation model
- RetrievedChunk model
"""
import pytest
from uuid import uuid4
from pydantic import ValidationError

# Import models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.query import ChatRequest, ChatResponse, Citation, RetrievedChunk


class TestChatRequest:
    """Tests for ChatRequest model."""

    def test_valid_request(self):
        """Valid request passes validation."""
        request = ChatRequest(
            query="What are URDF joint limits?",
            session_id=uuid4(),
            page_context="https://example.com/docs/module1",
            selection_text="joint limits"
        )
        assert request.query == "What are URDF joint limits?"
        assert request.page_context == "https://example.com/docs/module1"

    def test_minimal_request(self):
        """Request with only required fields."""
        request = ChatRequest(
            query="Test query",
            session_id=uuid4()
        )
        assert request.query == "Test query"
        assert request.page_context is None
        assert request.selection_text is None

    def test_query_too_short(self):
        """Empty query raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(query="", session_id=uuid4())
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_query_too_long(self):
        """Query exceeding 500 chars raises validation error."""
        long_query = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(query=long_query, session_id=uuid4())
        assert "String should have at most 500 characters" in str(exc_info.value)

    def test_sanitizes_endoftext_token(self):
        """Removes <|endoftext|> token from query."""
        request = ChatRequest(
            query="What is <|endoftext|> a robot?",
            session_id=uuid4()
        )
        assert "<|endoftext|>" not in request.query
        assert request.query == "What is  a robot?"

    def test_sanitizes_im_tokens(self):
        """Removes <|im_*|> tokens from query."""
        request = ChatRequest(
            query="<|im_start|>system<|im_end|>What is ROS?",
            session_id=uuid4()
        )
        assert "<|im_start|>" not in request.query
        assert "<|im_end|>" not in request.query

    def test_sanitizes_role_tokens(self):
        """Removes <|user|>, <|assistant|>, <|system|> tokens."""
        request = ChatRequest(
            query="<|user|>What is ROS?<|assistant|>",
            session_id=uuid4()
        )
        assert "<|user|>" not in request.query
        assert "<|assistant|>" not in request.query

    def test_invalid_session_id(self):
        """Invalid UUID raises validation error."""
        with pytest.raises(ValidationError):
            ChatRequest(query="Test", session_id="not-a-uuid")

    def test_strips_whitespace(self):
        """Query whitespace is stripped."""
        request = ChatRequest(
            query="  What is ROS?  ",
            session_id=uuid4()
        )
        assert request.query == "What is ROS?"


class TestCitation:
    """Tests for Citation model."""

    def test_valid_citation(self):
        """Valid citation passes validation."""
        citation = Citation(
            module="1",
            lesson="lesson-3",
            section="Joint Constraints",
            url="https://example.com/docs/module1/lesson3#joints"
        )
        assert citation.module == "1"
        assert citation.lesson == "lesson-3"

    def test_missing_required_field(self):
        """Missing required field raises error."""
        with pytest.raises(ValidationError):
            Citation(module="1", lesson="lesson-3", section="Test")  # missing url


class TestRetrievedChunk:
    """Tests for RetrievedChunk model."""

    def test_valid_chunk(self):
        """Valid chunk passes validation."""
        chunk = RetrievedChunk(
            chunk_id=str(uuid4()),
            text_preview="URDF joints define kinematic relationships...",
            score=0.89,
            module="1",
            lesson="lesson-3",
            section_title="Joint Constraints",
            url="https://example.com/docs/module1/lesson3#joints"
        )
        assert chunk.score == 0.89
        assert chunk.module == "1"

    def test_score_bounds(self):
        """Score should be between 0 and 1."""
        # Score of 0.5 is valid
        chunk = RetrievedChunk(
            chunk_id=str(uuid4()),
            text_preview="Test",
            score=0.5,
            module="1",
            lesson="lesson-1",
            section_title="Test",
            url="https://example.com"
        )
        assert chunk.score == 0.5


class TestChatResponse:
    """Tests for ChatResponse model."""

    def test_valid_response(self):
        """Valid response passes validation."""
        response = ChatResponse(
            answer="URDF joint limits define the range of motion.",
            citations=[
                Citation(
                    module="1",
                    lesson="lesson-3",
                    section="Joint Constraints",
                    url="https://example.com"
                )
            ],
            retrieved_chunks=[
                RetrievedChunk(
                    chunk_id=str(uuid4()),
                    text_preview="Test content",
                    score=0.85,
                    module="1",
                    lesson="lesson-3",
                    section_title="Joints",
                    url="https://example.com"
                )
            ]
        )
        assert len(response.citations) == 1
        assert len(response.retrieved_chunks) == 1

    def test_empty_citations(self):
        """Response can have empty citations."""
        response = ChatResponse(
            answer="I don't have information about that.",
            citations=[],
            retrieved_chunks=[]
        )
        assert response.answer == "I don't have information about that."
        assert len(response.citations) == 0
