"""
Custom exception hierarchy for the RAG Chatbot backend.

Provides:
- Base exception classes with structured error responses
- Domain-specific exceptions for different error scenarios
- HTTP status code mapping
- Error serialization for API responses

Usage:
    from src.utils.exceptions import ValidationError, DatabaseError

    raise ValidationError("Invalid query length", field="query", value=query)

    # In FastAPI exception handlers:
    @app.exception_handler(RAGException)
    async def handle_rag_exception(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
"""
from typing import Any, Dict, Optional


# ============================================================================
# Base Exception Classes
# ============================================================================


class RAGException(Exception):
    """
    Base exception for all RAG Chatbot errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code
        error_code: Machine-readable error code
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize exception to dictionary for API responses.

        Returns:
            Dictionary with error details
        """
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }

    def __str__(self) -> str:
        """String representation of exception."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ============================================================================
# Validation Exceptions (4xx)
# ============================================================================


class ValidationError(RAGException):
    """
    Input validation error (400 Bad Request).

    Raised when user input fails validation (e.g., query too long, invalid format).
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if field and details is None:
            details = {"field": field}
            if value is not None:
                details["value"] = str(value)

        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(RAGException):
    """
    Authentication error (401 Unauthorized).

    Raised when authentication fails (e.g., invalid API key).
    """

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class RateLimitError(RAGException):
    """
    Rate limit exceeded error (429 Too Many Requests).

    Raised when user exceeds rate limit (FR-048: 20 queries/hour).
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        window: Optional[str] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window

        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class NotFoundError(RAGException):
    """
    Resource not found error (404 Not Found).

    Raised when requested resource doesn't exist.
    """

    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details
        )


# ============================================================================
# Database Exceptions (5xx)
# ============================================================================


class DatabaseError(RAGException):
    """
    Database operation error (500 Internal Server Error).

    Raised when database operations fail (Neon, Qdrant).
    """

    def __init__(
        self,
        message: str,
        database: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {}
        if database:
            details["database"] = database
        if operation:
            details["operation"] = operation
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )


class ConnectionError(RAGException):
    """
    Connection error (503 Service Unavailable).

    Raised when unable to connect to external services (Neon, Qdrant, OpenAI).
    """

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        details = {}
        if service:
            details["service"] = service
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            status_code=503,
            error_code="CONNECTION_ERROR",
            details=details
        )


# ============================================================================
# External API Exceptions (5xx)
# ============================================================================


class OpenAIError(RAGException):
    """
    OpenAI API error (500 Internal Server Error).

    Raised when OpenAI API calls fail (embeddings, chat completion).
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        model: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if model:
            details["model"] = model
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message,
            status_code=500,
            error_code="OPENAI_ERROR",
            details=details
        )


class QdrantError(RAGException):
    """
    Qdrant vector database error (500 Internal Server Error).

    Raised when Qdrant operations fail (search, collection info).
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        collection: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if collection:
            details["collection"] = collection
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message,
            status_code=500,
            error_code="QDRANT_ERROR",
            details=details
        )


# ============================================================================
# RAG Pipeline Exceptions (5xx)
# ============================================================================


class EmbeddingError(RAGException):
    """
    Embedding generation error (500 Internal Server Error).

    Raised when text embedding generation fails.
    """

    def __init__(self, message: str, text: Optional[str] = None):
        details = {}
        if text:
            # Truncate text for security
            details["text_preview"] = text[:100] + "..." if len(text) > 100 else text

        super().__init__(
            message=message,
            status_code=500,
            error_code="EMBEDDING_ERROR",
            details=details
        )


class ChatCompletionError(RAGException):
    """
    Chat completion error (500 Internal Server Error).

    Raised when OpenAI chat completion fails.
    """

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {}
        if model:
            details["model"] = model
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message,
            status_code=500,
            error_code="CHAT_COMPLETION_ERROR",
            details=details
        )


class ContextWindowExceededError(RAGException):
    """
    Context window exceeded error (400 Bad Request).

    Raised when combined query + context exceeds model's context window (FR-040).
    """

    def __init__(
        self,
        message: str = "Context window exceeded",
        max_tokens: Optional[int] = None,
        actual_tokens: Optional[int] = None
    ):
        details = {}
        if max_tokens:
            details["max_tokens"] = max_tokens
        if actual_tokens:
            details["actual_tokens"] = actual_tokens

        super().__init__(
            message=message,
            status_code=400,
            error_code="CONTEXT_WINDOW_EXCEEDED",
            details=details
        )


# ============================================================================
# Configuration Exceptions
# ============================================================================


class ConfigurationError(RAGException):
    """
    Configuration error (500 Internal Server Error).

    Raised when application configuration is invalid or missing.
    """

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details
        )


# ============================================================================
# Circuit Breaker Exception
# ============================================================================


class CircuitBreakerOpenError(RAGException):
    """
    Circuit breaker open error (503 Service Unavailable).

    Raised when circuit breaker is open and blocking requests to a failing service.
    """

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        details = {}
        if service:
            details["service"] = service
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            status_code=503,
            error_code="CIRCUIT_BREAKER_OPEN",
            details=details
        )
