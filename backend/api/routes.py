"""NEXUS OS — Core API Routes"""

from fastapi import APIRouter

# Lazy imports to avoid circular dependencies
from api.engineering import router as engineering_router
from api.agents import router as agents_router
from api.projects import router as projects_router
from api.tasks import router as tasks_router
from api.repositories import router as repositories_router
from api.deployments import router as deployments_router
from api.monitoring import router as monitoring_router
from api.memory import router as memory_router
from api.knowledge import router as knowledge_router
from api.auth import router as auth_router
from api.websocket import router as websocket_router

__all__ = [
    "engineering_router", "agents_router", "projects_router",
    "tasks_router", "repositories_router", "deployments_router",
    "monitoring_router", "memory_router", "knowledge_router",
    "auth_router", "websocket_router",
]
