"""
NEXUS OS — Knowledge API Routes (Placeholder)
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/graph")
async def get_graph():
    return {"nodes": [], "edges": []}
