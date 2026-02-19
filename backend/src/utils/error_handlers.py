"""Comprehensive error handling utilities with circuit breaker integration."""

from typing import Optional, Dict, Any, Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from enum import Enum
import logging
from ..utils.logger import get_logger
from ..utils.circuit_breaker import CircuitBreaker


logger = get_logger(__name__)


class ErrorCode(str, Enum):
    """Standard error codes for the application."""

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # AI-specific errors
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    AI_RATE_LIMIT_ERROR = "AI_RATE_LIMIT_ERROR"
    AI_CONTENT_FILTERED = "AI_CONTENT_FILTERED"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"

    # Authentication errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"


class APIError(Exception):
    """Base API exception with standard error code."""

    def __init__(self, error_code: ErrorCode, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_json_response(self) -> JSONResponse:
        """Convert this error to FastAPI JSONResponse."""
        error_response = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details
            }
        }
        return JSONResponse(
            status_code=self.status_code,
            content=error_response
        )


class ValidationError(APIError):
    """Validation error with field-specific details."""

    def __init__(self, message: str, field_errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=422,
            details={"field_errors": field_errors or {}}
        )


class ServiceError(APIError):
    """Service-level error with context."""

    def __init__(self, error_code: ErrorCode, message: str, service_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=error_code,
            message=message,
            details={
                **(details or {}),
                "service": service_name
            }
        )


class CircuitBreakerManager:
    """Global circuit breaker manager for services."""

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def get_or_create_circuit_breaker(self, name: str, **settings) -> CircuitBreaker:
        """Get or create a circuit breaker instance."""
        if name not in self.circuit_breakers:
            failure_threshold = settings.get('failure_threshold', 5)
            recovery_timeout = settings.get('recovery_timeout', 60)
            self.circuit_breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout
            )
        return self.circuit_breakers[name]

    def reset_circuit_breaker(self, name: str):
        """Reset a specific circuit breaker."""
        if name in self.circuit_breakers:
            self.circuit_breakers[name].reset()

    def get_status(self, name: str) -> Dict[str, Any]:
        """Get the status of a circuit breaker."""
        if name in self.circuit_breakers:
            cb = self.circuit_breakers[name]
            return {
                "name": name,
                "state": cb.state,
                "failure_count": cb.failure_count,
                "is_open": cb.is_open()
            }
        return {"name": name, "state": "UNKNOWN", "is_open": False}


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


def handle_api_exception(exc: Exception) -> APIError:
    """Convert various exceptions to standard APIError."""
    if isinstance(exc, APIError):
        return exc

    if isinstance(exc, HTTPException):
        # Convert HTTPException to APIError
        if exc.status_code == 422:
            return ValidationError("Validation error occurred", field_errors={"detail": str(exc.detail)})
        elif exc.status_code == 401:
            return APIError(ErrorCode.UNAUTHORIZED, "Authentication required", 401)
        elif exc.status_code == 403:
            return APIError(ErrorCode.FORBIDDEN, "Access denied", 403)
        elif exc.status_code == 404:
            return APIError(ErrorCode.NOT_FOUND, "Resource not found", 404)
        elif exc.status_code == 429:
            return APIError(ErrorCode.RATE_LIMIT_EXCEEDED, "Rate limit exceeded", 429)
        else:
            return APIError(ErrorCode.INTERNAL_ERROR, f"Request failed: {str(exc)}", exc.status_code)

    # Handle specific exception types
    if "circuit" in str(exc).lower() or "open" in str(exc).lower():
        return APIError(ErrorCode.SERVICE_UNAVAILABLE, "Service temporarily unavailable due to high load", 503)

    # Default to internal error
    logger.error(f"Unhandled API exception: {exc}", exc_info=True)
    return APIError(ErrorCode.INTERNAL_ERROR, f"An internal error occurred: {str(exc)}", 500)


async def safe_service_call(service_callable, service_name: str, circuit_breaker_name: Optional[str] = None):
    """
    Safely call a service method with circuit breaker protection.

    Args:
        service_callable: The service method to call (can be sync or async)
        service_name: Name of the service for logging
        circuit_breaker_name: Name of circuit breaker to use (auto-generated if not provided)
    """
    if circuit_breaker_name is None:
        circuit_breaker_name = f"service_{service_name}"

    circuit_breaker = circuit_breaker_manager.get_or_create_circuit_breaker(circuit_breaker_name)

    try:
        # Execute with circuit breaker protection
        result = await circuit_breaker.execute(service_callable)
        return result
    except Exception as e:
        # Log the error before raising
        logger.error(f"Service call failed for {service_name}: {str(e)}", exc_info=True)

        # Convert the error to an APIError
        if "rate limit" in str(e).lower():
            raise ServiceError(
                ErrorCode.AI_RATE_LIMIT_ERROR,
                f"Rate limit exceeded for {service_name}",
                service_name
            )

        raise ServiceError(
            ErrorCode.SERVICE_UNAVAILABLE,
            f"Service {service_name} is currently unavailable: {str(e)}",
            service_name,
            {"original_error": str(e)}
        )


def standardize_error_response(error: Union[APIError, Exception]) -> Dict[str, Any]:
    """
    Create a standardized error response body from any error type.

    Args:
        error: Either APIError or any exception

    Returns:
        Dictionary with standardized error structure
    """
    if isinstance(error, APIError):
        return {
            "error": {
                "code": error.error_code.value,
                "message": error.message,
                "status_code": error.status_code,
                "details": error.details
            },
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    else:
        # For raw exceptions, create a standard error response
        return {
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": f"An unexpected error occurred: {str(error)}",
                "status_code": 500,
                "details": {"error_type": type(error).__name__}
            },
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }


# Decorator for automatic error handling
def with_api_error_handling(async_func):
    """
    Decorator to wrap API endpoints with standard error handling.
    """
    import functools

    @functools.wraps(async_func)
    async def wrapper(*args, **kwargs):
        try:
            result = await async_func(*args, **kwargs)
            return result
        except APIError as api_err:
            logger.error(f"APIError in {async_func.__name__}: {api_err.message}")
            return api_err.to_json_response()
        except HTTPException as http_err:
            # Convert HTTP exception to API error for consistency
            error = handle_api_exception(http_err)
            logger.error(f"HTTPError in {async_func.__name__}: {error.message}")
            return error.to_json_response()
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in {async_func.__name__}: {str(e)}", exc_info=True)
            error = handle_api_exception(e)
            return error.to_json_response()

    return wrapper