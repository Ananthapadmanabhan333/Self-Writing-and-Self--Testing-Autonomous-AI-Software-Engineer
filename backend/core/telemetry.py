"""
NEXUS OS — Telemetry & Observability
OpenTelemetry setup for distributed tracing and performance monitoring.
"""

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from core.config import settings

logger = structlog.get_logger()

def setup_telemetry():
    """Configure OpenTelemetry tracing."""
    if not settings.JAEGER_ENDPOINT:
        logger.warning("⚠️ Jaeger endpoint not configured, tracing disabled")
        return

    resource = Resource.create({
        "service.name": settings.APP_NAME,
        "service.version": settings.APP_VERSION,
        "deployment.environment": settings.APP_ENV
    })

    tracer_provider = TracerProvider(resource=resource)
    
    try:
        otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        trace.set_tracer_provider(tracer_provider)
        logger.info("🔭 Telemetry initialized", endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    except Exception as e:
        logger.error("❌ Telemetry setup failed", error=str(e))

def get_tracer():
    return trace.get_tracer(__name__)
