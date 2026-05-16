"""
NEXUS OS — Database Models & SQLAlchemy Setup
Production-grade async PostgreSQL with pgvector support.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

from core.config import settings


# ---- Engine & Session ----
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database schema."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    """Base model with common fields."""

    id: Any
    __abstract__ = True

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# ==============================================================
# CORE DOMAIN MODELS
# ==============================================================

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    settings = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    repositories = relationship("Repository", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="engineer")  # admin, manager, engineer, viewer
    hashed_password = Column(String(255), nullable=False)
    github_token = Column(String(255))
    preferences = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    organization = relationship("Organization", back_populates="users")
    projects = relationship("Project", back_populates="owner")
    tasks = relationship("EngineeringTask", back_populates="assigned_to")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        String(50), default="active"
    )  # active, paused, completed, archived
    tech_stack = Column(JSONB, default=[])
    architecture_type = Column(String(100))
    requirements_raw = Column(Text)
    requirements_parsed = Column(JSONB, default={})
    feature_graph = Column(JSONB, default={})
    sprint_config = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="projects")
    owner = relationship("User", back_populates="projects")
    tasks = relationship("EngineeringTask", back_populates="project")
    deployments = relationship("Deployment", back_populates="project")
    repositories = relationship("Repository", back_populates="project")


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500))  # owner/repo
    url = Column(String(1000))
    clone_url = Column(String(1000))
    default_branch = Column(String(100), default="main")
    language = Column(String(50))
    tech_stack = Column(JSONB, default=[])
    index_status = Column(
        String(50), default="pending"
    )  # pending, indexing, indexed, failed
    last_indexed_at = Column(DateTime(timezone=True))
    file_count = Column(Integer, default=0)
    line_count = Column(Integer, default=0)
    complexity_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="repositories")
    project = relationship("Project", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository")


class EngineeringTask(Base):
    __tablename__ = "engineering_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    type = Column(
        String(50)
    )  # feature, bug, refactor, test, deploy, debug, security, docs
    status = Column(
        String(50), default="pending"
    )  # pending, planning, in_progress, review, completed, failed
    priority = Column(String(20), default="medium")  # critical, high, medium, low
    complexity_estimate = Column(Float)
    story_points = Column(Integer)
    acceptance_criteria = Column(JSONB, default=[])
    implementation_plan = Column(JSONB, default={})
    agent_assignments = Column(JSONB, default=[])
    generated_code = Column(JSONB, default={})
    test_results = Column(JSONB, default={})
    debug_history = Column(JSONB, default=[])
    sprint_id = Column(String(100))
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("engineering_tasks.id"), nullable=True)
    dependencies = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tasks")
    assigned_to = relationship("User", back_populates="tasks")
    subtasks = relationship("EngineeringTask", backref="parent_task", remote_side=[id])
    agent_executions = relationship("AgentExecution", back_populates="task")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("engineering_tasks.id"))
    agent_type = Column(
        String(50)
    )  # architect, backend, frontend, devops, qa, security, debug, refactor, sre, release
    status = Column(
        String(50), default="running"
    )  # running, completed, failed, cancelled
    input_context = Column(JSONB, default={})
    output = Column(JSONB, default={})
    reasoning_trace = Column(JSONB, default=[])  # Chain-of-thought steps
    tools_used = Column(JSONB, default=[])
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    duration_ms = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    task = relationship("EngineeringTask", back_populates="agent_executions")


class GeneratedCode(Base):
    __tablename__ = "generated_code"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("engineering_tasks.id"))
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=True)
    file_path = Column(String(1000), nullable=False)
    language = Column(String(50))
    content = Column(Text, nullable=False)
    content_hash = Column(String(64))
    version = Column(Integer, default=1)
    is_applied = Column(Boolean, default=False)
    test_coverage = Column(Float)
    quality_score = Column(Float)
    generated_by = Column(String(50))  # agent type
    review_status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    environment = Column(String(50))  # development, staging, production
    strategy = Column(String(50), default="rolling")  # rolling, canary, blue_green
    status = Column(
        String(50), default="pending"
    )  # pending, deploying, success, failed, rolled_back
    provider = Column(String(50))  # vercel, railway, aws, gcp, azure, kubernetes
    target_url = Column(String(1000))
    commit_sha = Column(String(40))
    branch = Column(String(255))
    config = Column(JSONB, default={})
    metrics = Column(JSONB, default={})
    error_log = Column(Text)
    rollback_deployment_id = Column(UUID(as_uuid=True), nullable=True)
    canary_percentage = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    project = relationship("Project", back_populates="deployments")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(20))  # critical, high, medium, low
    status = Column(
        String(50), default="open"
    )  # open, investigating, mitigating, resolved
    root_cause = Column(Text)
    resolution = Column(Text)
    remediation_steps = Column(JSONB, default=[])
    affected_services = Column(JSONB, default=[])
    timeline = Column(JSONB, default=[])
    auto_resolved = Column(Boolean, default=False)
    mean_time_to_detect_seconds = Column(Integer)
    mean_time_to_resolve_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))


class EngineeringMemory(Base):
    __tablename__ = "engineering_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    memory_type = Column(
        String(50)
    )  # architecture_decision, debugging_pattern, deployment_outcome, coding_preference
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(255))  # ID in Qdrant
    tags = Column(JSONB, default=[])
    relevance_score = Column(Float, default=1.0)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))
    source = Column(String(100))  # agent, human, system
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    node_type = Column(
        String(50)
    )  # service, api, repository, developer, incident, feature, infrastructure
    name = Column(String(255), nullable=False)
    properties = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"))
    target_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"))
    edge_type = Column(
        String(50)
    )  # depends_on, owned_by, deployed_to, caused_by, affects
    properties = Column(JSONB, default={})
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Commit(Base):
    __tablename__ = "commits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"))
    sha = Column(String(40), nullable=False)
    message = Column(Text)
    author = Column(String(255))
    files_changed = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    ai_generated = Column(Boolean, default=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("engineering_tasks.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repository = relationship("Repository", back_populates="commits")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("engineering_tasks.id"), nullable=True)
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=True)
    test_type = Column(String(50))  # unit, integration, e2e, load, security
    status = Column(String(50))  # running, passed, failed, error
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    coverage_percentage = Column(Float)
    duration_seconds = Column(Float)
    test_results = Column(JSONB, default=[])
    error_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
