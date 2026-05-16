"""
NEXUS OS — Auth API Routes (Placeholder)
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/me")
async def get_current_user():
    return {"id": "001", "email": "admin@nexus-os.ai", "role": "admin"}
