"""
WebSocket Connection Manager with security features
"""

from typing import List, Dict
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections with security."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.max_connections_per_ip: Dict[str, int] = defaultdict(int)

    async def connect(self, websocket: WebSocket, client_ip: str) -> bool:
        """Connect a new WebSocket client with IP-based rate limiting"""
        await websocket.accept()

        # Limit connections per IP
        if self.max_connections_per_ip[client_ip] >= 5:
            print(f"[WS] ⚠️ Too many connections from {client_ip}")
            await websocket.close(code=1008)
            return False

        self.max_connections_per_ip[client_ip] += 1
        self.active_connections.append(websocket)
        print(f"[WS] Client connected from {client_ip}. Total: {len(self.active_connections)}")
        return True

    def disconnect(self, websocket: WebSocket, client_ip: str):
        """Disconnect a WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.max_connections_per_ip[client_ip] = max(0, self.max_connections_per_ip[client_ip] - 1)
        print(f"[WS] Client disconnected from {client_ip}. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Error sending message: {e}")

    def get_connection_count(self) -> int:
        """Get current active connection count"""
        return len(self.active_connections)

    def get_connections_per_ip(self) -> Dict[str, int]:
        """Get connection count per IP"""
        return dict(self.max_connections_per_ip)


# Global instance
manager = ConnectionManager()
