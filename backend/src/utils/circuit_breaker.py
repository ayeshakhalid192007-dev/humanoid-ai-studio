"""Circuit breaker pattern implementation for external API resilience."""
import asyncio
import time
from typing import Callable, TypeVar, Awaitable, Optional

T = TypeVar('T')


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open and calls are rejected."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation with states:
    - CLOSED: Normal operation, failure counter maintained
    - OPEN: Stop accepting requests until recovery timeout
    - HALF_OPEN: Allow one request to test recovery
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        # Lock to ensure thread safety
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute a function through the circuit breaker."""
        return await self.execute(func, *args, **kwargs)

    async def execute(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute a function with circuit breaker protection."""
        async with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerError("Circuit breaker is OPEN")

        if self.state == "HALF_OPEN":
            # Try single request to see if we can close the circuit
            try:
                result = await func(*args, **kwargs)
                async with self._lock:
                    self.failure_count = 0
                    self.state = "CLOSED"
                return result
            except Exception:
                async with self._lock:
                    self.last_failure_time = time.time()
                    self.state = "OPEN"
                raise
        else:  # CLOSED state
            try:
                result = await func(*args, **kwargs)
                async with self._lock:
                    self.failure_count = 0
                return result
            except Exception:
                async with self._lock:
                    self.failure_count += 1
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                        self.last_failure_time = time.time()
                raise

    def is_open(self) -> bool:
        """Check if the circuit breaker is open."""
        current_state = self.state
        if current_state == "OPEN" and time.time() - (self.last_failure_time or 0) > self.recovery_timeout:
            async def reset_state():
                async with self._lock:
                    if self.state == "OPEN" and time.time() - (self.last_failure_time or 0) > self.recovery_timeout:
                        self.state = "HALF_OPEN"
            # We can't do async operations in a sync context, so we'll just check
            # But normally it would switch to HALF_OPEN when timeout expires
        return self.state == "OPEN"

    def reset(self):
        """Reset the circuit breaker to CLOSED state."""
        async def async_reset():
            async with self._lock:
                self.failure_count = 0
                self.last_failure_time = None
                self.state = "CLOSED"
        # For now, we just update the in-memory state
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()

        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """Attempt to acquire tokens from the bucket."""
        async with self._lock:
            now = time.time()
            # Add tokens based on time elapsed since last refill
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False


class RetryPolicy:
    """Exponential backoff retry policy."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, multiplier: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.base_delay * (self.multiplier ** min(attempt, 10))  # Cap exponent
        return min(delay, self.max_delay)