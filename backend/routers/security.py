"""
Security API Router
"""

from fastapi import APIRouter, Request

from modules.websocket.manager import manager
from modules.security.evidencia import evidencia_de_seguridad
from modules.security.metrics import security_metrics


router = APIRouter(prefix="/api")


@router.get("/security")
async def get_security_metrics(request: Request):
    """
    Security metrics, plus what the application can actually prove about itself.

    `evidence` is the part the interface needs. The hand-written panel held eight
    checks, all 'pass', and kept saying so for the eight months the WebSocket
    endpoint did not authenticate. Here each check reports pasa / falla / no_se
    with the evidence behind it, and what cannot be measured from inside the
    process says so instead of showing a green tick.
    """
    return {
        "security_metrics": security_metrics.get_all(),
        "active_connections": manager.get_connection_count(),
        "per_ip_connections": manager.get_connections_per_ip(),
        "evidence": evidencia_de_seguridad(request.app),
    }
