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


class Sensitivity(str, Enum):
    """
    Qué clase de datos maneja un agente. Es una declaración, no una deducción:
    la política de confianza de Hydra sabe qué modelo vale para cada nivel,
    pero nadie puede adivinar el nivel de un agente leyendo su nombre.

    SAFE es el valor por omisión porque es lo que la configuración actual ya
    implica (hay agentes en modelos de nube). Declarar SENSITIVE o CRITICAL
    activa la restricción de VULN-007 sobre ese agente en el arranque.
    """
    SAFE = "SAFE"
    SENSITIVE = "SENSITIVE"
    CRITICAL = "CRITICAL"


class AgentModel(BaseModel):
    id: str
    name: str
    model: str
    sensitivity: Sensitivity = Sensitivity.SAFE
    status: AgentStatus = AgentStatus.IDLE
    cost: float = 0.0
    last_update: Optional[str] = None
