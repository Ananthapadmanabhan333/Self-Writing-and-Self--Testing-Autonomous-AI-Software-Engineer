"""
NEXUS OS — Monitoring API Routes (Placeholder)
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_stats():
    return {"status": "healthy"}
