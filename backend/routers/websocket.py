"""
WebSocket Router
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from modules.websocket.manager import manager
from modules.websocket.handlers import handle_message
from modules.agents.state import agents
from modules.crew.state import crew_state
from modules.security.metrics import security_metrics


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint with security."""
    client_ip = websocket.client.host if websocket.client else "unknown"

    # Connect with rate limiting per IP
    connected = await manager.connect(websocket, client_ip)
    if not connected:
        return

    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": {
                "agents": [a.model_dump() for a in agents.values()],
                "crew": crew_state.model_dump()
            }
        })

        # Handle incoming messages with validation
        message_count = 0
        while True:
            try:
                data = await websocket.receive_text()
                message_count += 1

                # Limit messages per connection (1000 per minute)
                if message_count > 1000:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Message rate limit exceeded"}
                    })
                    break

                # Validate JSON
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    security_metrics.increment("invalid_messages")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Invalid JSON format"}
                    })
                    continue

                await handle_message(message)

            except json.JSONDecodeError:
                security_metrics.increment("invalid_messages")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, client_ip)
