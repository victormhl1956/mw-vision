"""
Agent Models
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class AgentModel(BaseModel):
    id: str
    name: str
    model: str
    status: AgentStatus = AgentStatus.IDLE
    cost: float = 0.0
    last_update: Optional[str] = None
