"""
Crew API Router
"""

from fastapi import APIRouter

from modules.crew.state import crew_state


router = APIRouter(prefix="/api")


@router.get("/crew")
async def get_crew_state():
    return crew_state.model_dump()
