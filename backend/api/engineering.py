"""NEXUS OS — Engineering API Routes (core orchestration endpoint)"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db, EngineeringTask
from agents.orchestrator import run_engineering_pipeline
from engines.requirements_engine import requirements_engine
from engines.debug_engine import debug_engine
from engines.sandbox_engine import sandbox_engine
from engines.memory_engine import memory_system

router = APIRouter()


# ── Request/Response Models ──────────────────────────────────

class ParseRequirementsRequest(BaseModel):
    raw_input: str = Field(..., min_length=10)
    input_type: str = Field("text", pattern="^(text|github_issue|jira|api_spec|voice_note)$")
    organization_id: str
    project_id: Optional[str] = None


class RunEngineeringRequest(BaseModel):
    task_id: Optional[str] = None
    task_type: str = Field("feature", pattern="^(feature|bug|refactor|migration|security)$")
    requirements: str = Field(..., min_length=10)
    organization_id: str
    project_id: Optional[str] = None
    autonomous_mode: bool = True


class ExecuteCodeRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = Field(30, ge=5, le=300)
    environment: Optional[Dict[str, str]] = None
    install_packages: Optional[List[str]] = None


class DebugRequest(BaseModel):
    error_message: str
    stack_trace: Optional[str] = None
    code_context: Optional[Dict[str, str]] = None
    task_id: Optional[str] = None


class AnalyzeCIRequest(BaseModel):
    ci_logs: str
    workflow_name: str


# ── Routes ───────────────────────────────────────────────────

@router.post("/parse-requirements")
async def parse_requirements(req: ParseRequirementsRequest):
    """Parse raw requirements into structured engineering specification."""
    spec = await requirements_engine.parse(req.raw_input, req.input_type)
    tasks = await requirements_engine.decompose_to_tasks(spec)
    architecture = await requirements_engine.infer_architecture(spec)
    return {
        "specification": spec,
        "tasks": tasks,
        "architecture": architecture,
        "prd_available": True,
    }


@router.post("/generate-prd")
async def generate_prd(req: ParseRequirementsRequest):
    """Generate full Product Requirements Document."""
    spec = await requirements_engine.parse(req.raw_input, req.input_type)
    prd = await requirements_engine.generate_prd(spec)
    tech_spec = await requirements_engine.generate_technical_spec(spec)
    return {"prd": prd, "technical_spec": tech_spec, "specification": spec}


@router.post("/run-pipeline")
async def run_engineering_pipeline_endpoint(
    req: RunEngineeringRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Launch the full multi-agent engineering pipeline."""
    task_id = req.task_id or str(uuid.uuid4())
    if req.autonomous_mode:
        # Run async in background
        background_tasks.add_task(
            run_engineering_pipeline,
            task_id=task_id,
            task_type=req.task_type,
            requirements=req.requirements,
        )
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Multi-agent engineering pipeline launched",
            "agents": ["architect", "backend", "frontend", "qa", "devops", "security"],
            "track_at": f"/api/v1/tasks/{task_id}",
        }
    else:
        result = await run_engineering_pipeline(task_id, req.task_type, req.requirements)
        return {"task_id": task_id, "status": "completed", "result": result}


@router.post("/execute-code")
async def execute_code(req: ExecuteCodeRequest):
    """Execute code in an isolated sandbox environment."""
    result = await sandbox_engine.execute(
        code=req.code,
        language=req.language,
        timeout=req.timeout,
        environment=req.environment,
        install_packages=req.install_packages,
    )
    return result


@router.post("/debug")
async def debug_failure(req: DebugRequest):
    """Recursively analyze an error and generate patches."""
    result = await debug_engine.analyze_and_fix(
        error_message=req.error_message,
        stack_trace=req.stack_trace,
        code_context=req.code_context,
        task_id=req.task_id,
    )
    return result


@router.post("/analyze-ci")
async def analyze_ci_failure(req: AnalyzeCIRequest):
    """Analyze CI/CD pipeline failure logs and suggest fixes."""
    result = await debug_engine.analyze_ci_failure(req.ci_logs, req.workflow_name)
    return result


@router.get("/pipeline-status/{task_id}")
async def get_pipeline_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get real-time status of an engineering pipeline run."""
    from sqlalchemy import select
    result = await db.execute(
        select(EngineeringTask).where(EngineeringTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": task.status,
        "current_agent": task.agent_assignments,
        "generated_files": len(task.generated_code or {}),
        "test_results": task.test_results,
        "debug_iterations": len(task.debug_history or []),
    }


@router.post("/search-code")
async def search_code(query: str, repository_id: Optional[str] = None, language: Optional[str] = None):
    """Semantic code search across indexed repositories."""
    results = await memory_system.search_code(query, repository_id, language)
    return {"query": query, "results": results, "count": len(results)}
