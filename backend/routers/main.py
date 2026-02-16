"""
Main API Router
"""

from datetime import datetime
from fastapi import APIRouter

from modules.websocket.manager import manager
from modules.crew.state import crew_state
from modules.security.metrics import security_metrics


router = APIRouter()


@router.get("/")
async def root():
    return {
        "name": "MW-Vision Backend",
        "status": "running",
        "version": "3.0.0",
        "security": {
            "rate_limiting": "100 requests/minute",
            "cors": "restricted",
            "security_headers": "enabled"
        },
        "endpoints": {
            "websocket": "ws://localhost:8000/ws",
            "health": "/health",
            "agents": "/api/agents",
            "crew": "/api/crew",
            "security": "/api/security"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    metrics = security_metrics.get_all()
    uptime = (datetime.now() - datetime.fromisoformat(metrics["start_time"])).total_seconds()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_clients": manager.get_connection_count(),
        "crew_running": crew_state.is_running,
        "total_cost": crew_state.total_cost,
        "uptime_seconds": round(uptime, 2)
    }
