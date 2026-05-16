"""
NEXUS OS — Agents API Routes
Status monitoring and direct interaction with autonomous agents.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from core.redis_client import redis_client
from pydantic import BaseModel

router = APIRouter()

class AgentStatus(BaseModel):
    name: str
    type: str
    status: str
    current_task: Optional[str] = None
    heartbeat: str

@router.get("/status")
async def get_all_agents_status():
    """Get current status of all 10 autonomous agents from Redis."""
    agent_types = [
        "architect", "backend", "frontend", "devops", 
        "qa", "security", "debug", "refactor", "sre", "release"
    ]
    
    statuses = []
    for agent in agent_types:
        data = await redis_client.get(f"agent:status:{agent}")
        if data:
            import json
            statuses.append(json.loads(data))
        else:
            statuses.append({
                "name": f"{agent.capitalize()} Agent",
                "type": agent,
                "status": "standby",
                "heartbeat": "N/A"
            })
            
    return statuses

@router.get("/{agent_type}/history")
async def get_agent_history(agent_type: str, limit: int = 10):
    """Get recent activity history for a specific agent."""
    # This would query the AgentExecution table
    return {"agent": agent_type, "history": []}

