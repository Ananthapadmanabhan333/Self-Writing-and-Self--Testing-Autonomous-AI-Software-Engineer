"""
NEXUS OS — Autonomous Software Engineering Operating System
Main FastAPI Application Entry Point
"""

import asyncio
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from api.routes import (
    agents_router,
    auth_router,
    deployments_router,
    engineering_router,
    knowledge_router,
    memory_router,
    monitoring_router,
    projects_router,
    repositories_router,
    tasks_router,
    websocket_router,
)
from core.config import settings
from core.database import engine, init_db
from core.events import kafka_producer
from core.redis_client import redis_client
from core.telemetry import setup_telemetry

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("🚀 NEXUS OS initializing...", version=settings.APP_VERSION)

    # Initialize observability
    setup_telemetry()

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Connect Redis
    await redis_client.connect()
    logger.info("✅ Redis connected")

    # Start Kafka producer
    await kafka_producer.start()
    logger.info("✅ Kafka producer started")

    logger.info(
        "⚡ NEXUS OS fully operational",
        agents_count=10,
        engines_count=15,
        mode=settings.APP_ENV,
    )

    yield

    # Graceful shutdown
    logger.info("🔄 NEXUS OS shutting down...")
    await kafka_producer.stop()
    await redis_client.disconnect()
    await engine.dispose()
    logger.info("✅ NEXUS OS shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="NEXUS OS — Autonomous Software Engineering OS",
        description=(
            "Enterprise-grade autonomous software engineering platform that functions as "
            "an AI-native engineering workforce. Combines autonomous planning, multi-agent "
            "orchestration, code generation, sandboxed execution, self-debugging, deployment "
            "automation, and runtime monitoring into a single unified platform."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- Middleware ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ---- Prometheus Instrumentation ----
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_group_untemplated=True,
        should_round_latency_decimals=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app)

    # ---- Route Registration ----
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(projects_router, prefix="/api/v1/projects", tags=["Projects"])
    app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])
    app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])
    app.include_router(engineering_router, prefix="/api/v1/engineering", tags=["Engineering"])
    app.include_router(repositories_router, prefix="/api/v1/repositories", tags=["Repositories"])
    app.include_router(deployments_router, prefix="/api/v1/deployments", tags=["Deployments"])
    app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["Monitoring"])
    app.include_router(memory_router, prefix="/api/v1/memory", tags=["Memory"])
    app.include_router(knowledge_router, prefix="/api/v1/knowledge", tags=["Knowledge Graph"])
    app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

    return app


app = create_application()
FastAPIInstrumentor.instrument_app(app)


@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "operational",
        "service": "nexus-os",
        "version": settings.APP_VERSION,
        "agents": 10,
        "engines": 15,
    }


@app.get("/api/v1/status", tags=["System"])
async def system_status():
    """Detailed system status for all NEXUS OS components."""
    from core.redis_client import redis_client
    redis_ok = await redis_client.ping()

    return {
        "platform": "NEXUS OS",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "components": {
            "api": "operational",
            "database": "operational",
            "redis": "operational" if redis_ok else "degraded",
            "vector_store": "operational",
            "message_queue": "operational",
            "agents": {
                "architect": "standby",
                "backend": "standby",
                "frontend": "standby",
                "devops": "standby",
                "qa": "standby",
                "security": "standby",
                "debug": "standby",
                "refactor": "standby",
                "sre": "standby",
                "release": "standby",
            },
            "engines": {
                "requirements_understanding": "operational",
                "planning_reasoning": "operational",
                "code_generation": "operational",
                "sandboxed_execution": "operational",
                "self_debugging": "operational",
                "autonomous_testing": "operational",
                "deployment_orchestration": "operational",
                "runtime_monitoring": "operational",
                "engineering_memory": "operational",
                "autonomous_refactoring": "operational",
                "knowledge_graph": "operational",
                "project_management": "operational",
                "observability": "operational",
                "security_governance": "operational",
            },
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )
