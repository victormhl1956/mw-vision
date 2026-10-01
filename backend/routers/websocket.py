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
from src.security.websocket_auth import get_authenticator


router = APIRouter()

# Close code 1008 = policy violation. Sent before accepting the handshake, so an
# unauthenticated client never reaches the application protocol.
_WS_POLICY_VIOLATION = 1008


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint with security."""
    client_ip = websocket.client.host if websocket.client else "unknown"

    # Authenticate BEFORE accepting. This endpoint served any connection for
    # months while a correct HMAC verifier sat unimported in
    # src/security/websocket_auth.py: the fix existed and was never wired. The
    # server binds 0.0.0.0, so that was open to the whole tailnet, not just
    # localhost. tests/test_websocket_auth_wiring.py fails if this is undone.
    token = websocket.query_params.get("token", "")
    if not get_authenticator().verify_token(token):
        security_metrics.increment("rejected_connections")
        print(f"[WS] rejected unauthenticated connection from {client_ip}")
        await websocket.close(code=_WS_POLICY_VIOLATION)
        return

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
