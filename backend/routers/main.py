"""
Main API Router
"""

from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from modules.websocket.manager import manager
from modules.crew.state import crew_state
from modules.security.metrics import security_metrics


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirects to frontend UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=http://localhost:5189/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MW-Vision Backend</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        h1 { margin: 0 0 1rem 0; font-size: 2.5rem; }
        p { font-size: 1.2rem; opacity: 0.9; }
        a {
            display: inline-block;
            margin-top: 1.5rem;
            padding: 1rem 2rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        a:hover { transform: scale(1.05); }
        .info {
            margin-top: 2rem;
            font-size: 0.9rem;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 MW-Vision Backend</h1>
        <p>API Server Running on Port 8000</p>
        <p>Redirecting to UI...</p>
        <a href="http://localhost:5189/">Open MW-Vision UI</a>
        <div class="info">
            <p>Backend API: <code>http://localhost:8000</code></p>
            <p>Frontend UI: <code>http://localhost:5189</code></p>
        </div>
    </div>
</body>
</html>
    """


@router.get("/api")
async def api_info():
    """API information endpoint (JSON)"""
    return {
        "name": "MW-Vision Backend",
        "status": "running",
        "version": "3.0.0",
        "frontend_url": "http://localhost:5189",
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
