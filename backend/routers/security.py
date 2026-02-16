"""
Security API Router
"""

from fastapi import APIRouter

from modules.websocket.manager import manager
from modules.security.metrics import security_metrics


router = APIRouter(prefix="/api")


@router.get("/security")
async def get_security_metrics():
    """Security metrics endpoint."""
    return {
        "security_metrics": security_metrics.get_all(),
        "active_connections": manager.get_connection_count(),
        "per_ip_connections": manager.get_connections_per_ip()
    }
