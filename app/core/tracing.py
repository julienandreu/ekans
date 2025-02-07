"""Tracing configuration and setup."""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(
    service_name: str = "ekans",
    endpoint: str | None = None,
) -> None:
    """Configure OpenTelemetry tracing.

    Args:
        service_name: Name of the service for tracing
        endpoint: Optional OTLP endpoint (e.g., http://localhost:4317 for local collector)
    """
    resource = Resource.create({"service.name": service_name})

    # Create and set tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure exporter
    if endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
