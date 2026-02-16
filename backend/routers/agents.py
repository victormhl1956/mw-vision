"""
Agents API Router
"""

from fastapi import APIRouter

from modules.agents.state import agents
from modules.crew.state import crew_state


router = APIRouter(prefix="/api")


@router.get("/agents")
async def get_agents():
    return {
        "agents": list(agents.values()),
        "total_cost": crew_state.total_cost
    }
