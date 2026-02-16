"""
MW-Vision Backend - Modular Architecture
Run with: uvicorn main_modular:app --host 0.0.0.0 --port 8000

Features:
- Modular structure following MindWarehouse paradigm
- WebSocket endpoint for real-time communication
- Agent status management
- Cost tracking simulation
- Crew control (launch, pause, stop)
- Rate limiting (100 requests/minute)
- Security headers
- Restricted CORS
"""

from core.app import create_app
from routers import (
    main_router,
    agents_router,
    crew_router,
    security_router,
    websocket_router
)

# Create application
app = create_app()

# Register routers
app.include_router(main_router)
app.include_router(agents_router)
app.include_router(crew_router)
app.include_router(security_router)
app.include_router(websocket_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
