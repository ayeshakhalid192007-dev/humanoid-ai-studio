"""
Structured logging configuration for the RAG Chatbot backend.

Provides:
- JSON-formatted logs for production
- Console-friendly logs for development
- Request ID tracking for distributed tracing
- Performance timing decorators
- Log level configuration per environment

Usage:
    from src.utils.logger import get_logger, log_timing

    logger = get_logger(__name__)
    logger.info("Processing request", extra={"user_id": 123})

    @log_timing(logger)
    async def slow_function():
        ...
"""
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable, Dict, Optional

from pythonjsonlogger import jsonlogger

# Context variable for request ID tracking
request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Add request ID to log records for distributed tracing."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject request_id from context into log record."""
        record.request_id = request_id_ctx_var.get() or "no-request-id"
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to JSON log output."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["request_id"] = getattr(record, "request_id", "no-request-id")

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def configure_logging(
    level: str = "INFO",
    format: str = "json",
    show_sql: bool = False
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log format ("json" for production, "console" for development)
        show_sql: Whether to show SQL queries (for debugging)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Configure formatter
    if format == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Console-friendly format for development
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    # Configure root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # SQL query logging (optional)
    if show_sql:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set request ID in context for current request.

    Args:
        request_id: Optional request ID (generates UUID if not provided)

    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_ctx_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """
    Get current request ID from context.

    Returns:
        Current request ID or None
    """
    return request_id_ctx_var.get()


def log_timing(logger: logging.Logger, log_level: int = logging.INFO):
    """
    Decorator to log function execution time.

    Args:
        logger: Logger instance to use
        log_level: Log level for timing messages

    Usage:
        @log_timing(logger)
        async def slow_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            func_name = func.__name__

            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time
                logger.log(
                    log_level,
                    f"Function {func_name} completed",
                    extra={"duration_ms": round(elapsed * 1000, 2)}
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logger.error(
                    f"Function {func_name} failed",
                    extra={"duration_ms": round(elapsed * 1000, 2), "error": str(e)}
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            func_name = func.__name__

            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time
                logger.log(
                    log_level,
                    f"Function {func_name} completed",
                    extra={"duration_ms": round(elapsed * 1000, 2)}
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logger.error(
                    f"Function {func_name} failed",
                    extra={"duration_ms": round(elapsed * 1000, 2), "error": str(e)}
                )
                raise

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Example usage logger
_example_logger = get_logger(__name__)
_example_logger.info("Logger module initialized")
