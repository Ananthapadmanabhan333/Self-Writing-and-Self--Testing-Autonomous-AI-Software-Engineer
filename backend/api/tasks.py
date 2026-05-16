"""
NEXUS OS — Tasks API Routes
Management of engineering tasks and their autonomous execution state.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db, EngineeringTask, AgentExecution
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TaskSummary(BaseModel):
    id: UUID
    title: str
    status: str
    type: str
    priority: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TaskSummary])
async def list_tasks(
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List engineering tasks with optional filtering."""
    query = select(EngineeringTask)
    if project_id:
        query = query.where(EngineeringTask.project_id == project_id)
    if status:
        query = query.where(EngineeringTask.status == status)
    
    query = query.order_by(desc(EngineeringTask.created_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{task_id}")
async def get_task_details(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get detailed state of a specific task including agent executions."""
    query = select(EngineeringTask).where(EngineeringTask.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Fetch execution history
    exec_query = select(AgentExecution).where(AgentExecution.task_id == task_id).order_by(AgentExecution.started_at)
    exec_result = await db.execute(exec_query)
    executions = exec_result.scalars().all()
    
    return {
        **task.to_dict(),
        "executions": [e.to_dict() for e in executions]
    }

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Cancel a running engineering task."""
    query = select(EngineeringTask).where(EngineeringTask.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = "cancelled"
    await db.commit()
    return {"status": "cancelled"}
