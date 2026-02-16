"""
Crew Models
"""

from pydantic import BaseModel


class CrewState(BaseModel):
    is_running: bool = False
    total_cost: float = 0.0
    budget_limit: float = 10.0
