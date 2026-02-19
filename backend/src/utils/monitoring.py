"""Monitoring and observability utilities for Physical AI Platform.

Implements:
- OpenTelemetry instrumentation
- Prometheus metrics collection
- Structured logging with correlation IDs
- Request tracing across services
"""

import asyncio
import time
import uuid
from contextvars import ContextVar
from typing import Optional, Dict, Any, Callable
from functools import wraps

from opentelemetry import trace, metrics
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.textmap import CarrierT, Getter, Setter, TextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.util.types import AttributeValue

from .logger import get_logger

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default=None)

# Global tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create metrics
request_counter = meter.create_counter(
    "http_requests_total",
    description="Total number of HTTP requests",
)

request_duration_histogram = meter.create_histogram(
    "http_request_duration_seconds",
    description="Duration of HTTP requests in seconds",
)

active_requests_gauge = meter.create_up_down_counter(
    "http_active_requests",
    description="Number of active HTTP requests",
)

# Custom logger for monitoring
logger = get_logger(__name__)


class CorrelationIdPropagator(TextMapPropagator):
    """Propagator for correlation ID in HTTP headers."""

    def extract(self, carrier: CarrierT, context: Context, getter: Getter) -> Context:
        # Extract correlation ID from carrier
        correlation_ids = getter.get(carrier, 'x-correlation-id')
        if correlation_ids:
            correlation_id = correlation_ids[0] if isinstance(correlation_ids, list) else correlation_ids
            correlation_id_var.set(correlation_id)
        # Return the incoming context
        return context

    def inject(self, carrier: CarrierT, context: Context, setter: Setter):
        correlation_id = correlation_id_var.get()
        if correlation_id:
            setter.set(carrier, 'x-correlation-id', correlation_id)

    @property
    def fields(self):
        return {'x-correlation-id'}


def setup_monitoring(service_name: str = "physical-ai-platform",
                    otlp_endpoint: Optional[str] = None,
                    enable_metrics: bool = True,
                    enable_tracing: bool = True):
    """Initialize monitoring with OpenTelemetry and Prometheus."""

    # Set up global propagator to include correlation ID
    set_global_textmap(CorrelationIdPropagator())

    if enable_tracing:
        # Configure tracer provider
        trace_provider = TracerProvider(
            resource=Resource.create({"service.name": service_name})
        )

        if otlp_endpoint:
            # Export traces to OTLP endpoint
            trace_provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
            )

        trace.set_tracer_provider(trace_provider)

    if enable_metrics:
        # Configure meter provider
        metric_provider = MeterProvider(
            resource=Resource.create({"service.name": service_name})
        )

        if otlp_endpoint:
            # Export metrics to OTLP endpoint
            metric_provider = MeterProvider(
                resource=Resource.create({"service.name": service_name})
            )
            # In a real setup, you'd export metrics similarly
            # For now, we'll keep it in memory

        metrics.set_meter_provider(metric_provider)


def get_correlation_id() -> str:
    """Get the current correlation ID or create a new one."""
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str):
    """Set the correlation ID in the current context."""
    correlation_id_var.set(correlation_id)


def trace_function(operation_name: str = None):
    """Decorator to trace function execution with OpenTelemetry."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            correlation_id = get_correlation_id()
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(operation) as span:
                span.set_attribute("correlation_id", correlation_id)
                span.set_attribute("function", func.__name__)

                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_seconds", duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            correlation_id = get_correlation_id()
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(operation) as span:
                span.set_attribute("correlation_id", correlation_id)
                span.set_attribute("function", func.__name__)

                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_seconds", duration)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def monitor_request_duration(func: Callable) -> Callable:
    """Decorator to measure and record request duration."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        correlation_id = get_correlation_id()

        try:
            result = await func(*args, **kwargs)
            status = "success"
            return result
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            attributes = {
                "method": getattr(func, '__name__', 'unknown'),
                "correlation_id": correlation_id,
                "status": status
            }

            request_duration_histogram.record(duration, attributes=attributes)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        correlation_id = get_correlation_id()

        try:
            result = func(*args, **kwargs)
            status = "success"
            return result
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            attributes = {
                "method": getattr(func, '__name__', 'unknown'),
                "correlation_id": correlation_id,
                "status": status
            }

            request_duration_histogram.record(duration, attributes=attributes)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def add_request_instrumentation(app, service_name: str = "physical-ai-platform"):
    """Add request instrumentation to FastAPI app."""

    # Use OpenTelemetry FastAPI instrumentation
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace.get_tracer_provider(),
        excluded_urls="/health,/metrics"
    )

    # Add custom middleware for correlation ID and more detailed metrics
    @app.middleware("http")
    async def correlation_id_middleware(request, call_next):
        # Extract or create correlation ID
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        correlation_id_var.set(correlation_id)

        # Add to logger context
        request.state.correlation_id = correlation_id

        # Record request start
        attributes = {
            "http.method": request.method,
            "http.url": str(request.url),
            "correlation_id": correlation_id
        }
        active_requests_gauge.add(1, attributes=attributes)

        start_time = time.time()

        try:
            response = await call_next(request)
        finally:
            # Record request end
            duration = time.time() - start_time

            response_attributes = {
                "http.method": request.method,
                "http.url": str(request.url),
                "http.status_code": response.status_code,
                "correlation_id": correlation_id
            }

            request_counter.add(1, attributes=response_attributes)
            request_duration_histogram.record(duration, attributes=response_attributes)
            active_requests_gauge.add(-1, attributes=attributes)

            # Add correlation ID to response headers
            response.headers["x-correlation-id"] = correlation_id

        return response


class MetricsCollector:
    """Utility class for collecting and exposing custom metrics."""

    def __init__(self):
        self.custom_metrics = {}

    def register_counter(self, name: str, description: str = ""):
        """Register a custom counter metric."""
        counter = meter.create_counter(name, description=description)
        self.custom_metrics[name] = counter
        return counter

    def register_histogram(self, name: str, description: str = ""):
        """Register a custom histogram metric."""
        histogram = meter.create_histogram(name, description=description)
        self.custom_metrics[name] = histogram
        return histogram

    def register_gauge(self, name: str, description: str = ""):
        """Register a custom gauge metric."""
        gauge = meter.create_up_down_counter(name, description=description)
        self.custom_metrics[name] = gauge
        return gauge


# Global metrics collector instance
metrics_collector = MetricsCollector()


def record_agent_execution(agent_type: str, latency_ms: float, cached: bool,
                          token_count: Optional[int] = None, model: Optional[str] = None):
    """Record agent execution metrics."""
    attributes = {
        "agent_type": agent_type,
        "cached": cached,
        "correlation_id": get_correlation_id()
    }

    if model:
        attributes["model"] = model

    # Record execution count
    execution_counter = metrics_collector.register_counter(
        "agent_executions_total",
        "Total number of agent executions"
    )
    execution_counter.add(1, attributes=attributes)

    # Record latency
    execution_duration = metrics_collector.register_histogram(
        "agent_execution_duration_ms",
        "Duration of agent executions in milliseconds"
    )
    execution_duration.record(latency_ms, attributes=attributes)

    # Record token count if available
    if token_count:
        token_counter = metrics_collector.register_counter(
            "agent_tokens_total",
            "Total number of tokens processed by agents"
        )
        token_counter.add(token_count, attributes=attributes)


def record_cache_hit(cache_type: str, namespace: str):
    """Record cache hit metrics."""
    attributes = {
        "cache_type": cache_type,
        "namespace": namespace,
        "correlation_id": get_correlation_id()
    }

    cache_hit_counter = metrics_collector.register_counter(
        "cache_hits_total",
        "Total number of cache hits"
    )
    cache_hit_counter.add(1, attributes=attributes)


def record_cache_miss(cache_type: str, namespace: str):
    """Record cache miss metrics."""
    attributes = {
        "cache_type": cache_type,
        "namespace": namespace,
        "correlation_id": get_correlation_id()
    }

    cache_miss_counter = metrics_collector.register_counter(
        "cache_misses_total",
        "Total number of cache misses"
    )
    cache_miss_counter.add(1, attributes=attributes)


def record_db_query(duration_ms: float, query_type: str, table_name: str, success: bool = True):
    """Record database query metrics."""
    attributes = {
        "query_type": query_type,
        "table": table_name,
        "success": success,
        "correlation_id": get_correlation_id()
    }

    db_query_counter = metrics_collector.register_counter(
        "db_queries_total",
        "Total number of database queries"
    )
    db_query_counter.add(1, attributes=attributes)

    db_query_duration = metrics_collector.register_histogram(
        "db_query_duration_ms",
        "Duration of database queries in milliseconds"
    )
    db_query_duration.record(duration_ms, attributes=attributes)


# Initialize default metrics
def init_default_metrics():
    """Initialize default metrics for the platform."""
    # These are already created at module level, but we can extend here
    pass


__all__ = [
    'setup_monitoring',
    'get_correlation_id',
    'set_correlation_id',
    'trace_function',
    'monitor_request_duration',
    'add_request_instrumentation',
    'MetricsCollector',
    'metrics_collector',
    'record_agent_execution',
    'record_cache_hit',
    'record_cache_miss',
    'record_db_query'
]