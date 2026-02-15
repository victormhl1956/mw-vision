"""
MW-Vision Backend - FastAPI with WebSocket Support
Enhanced with Security Features

Features:
- WebSocket endpoint for real-time communication
- Agent status management
- Cost tracking simulation
- Crew control (launch, pause, stop)
- Rate limiting (100 requests/minute)
- Security headers
- Restricted CORS

Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
from collections import defaultdict
from threading import Lock

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from enum import Enum

# ============================================================================
# Security: Rate Limiting
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 100 requests per minute per IP"""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()
    
    def cleanup_old_requests(self, ip: str, current_time: float):
        """Remove requests older than 1 minute"""
        cutoff = current_time - 60
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
    
    def is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        """Check if IP is rate limited"""
        current_time = time.time()
        with self.lock:
            self.cleanup_old_requests(ip, current_time)
            request_count = len(self.requests[ip])
            
            if request_count >= self.requests_per_minute:
                # Find when the oldest request will expire
                oldest = min(self.requests[ip]) if self.requests[ip] else current_time
                retry_after = int(oldest + 60 - current_time) + 1
                return True, retry_after
            
            self.requests[ip].append(current_time)
            return False, 0
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for WebSocket and health endpoints
        if request.url.path in ["/ws", "/health"] or request.url.path.startswith("/ws"):
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        limited, retry_after = self.is_rate_limited(client_ip)
        
        if limited:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "message": f"Too many requests. Retry in {retry_after} seconds."
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        response = await call_next(request)
        return response

# ============================================================================
# Security Headers Middleware
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

# ============================================================================
# Models
# ============================================================================

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

class CrewState(BaseModel):
    is_running: bool = False
    total_cost: float = 0.0
    budget_limit: float = 10.0

class WebSocketMessage(BaseModel):
    type: str
    agent_id: Optional[str] = None
    data: Optional[Dict] = None

# ============================================================================
# In-Memory State (for MVP - use database in production)
# ============================================================================

agents: Dict[str, AgentModel] = {
    "1": AgentModel(id="1", name="Debugger", model="claude-3-5-sonnet"),
    "2": AgentModel(id="2", name="Code Reviewer", model="deepseek-chat"),
    "3": AgentModel(id="3", name="Test Generator", model="gpt-4o"),
}

crew_state = CrewState()
connected_clients: List[WebSocket] = []

# ============================================================================
# Model Cost Configuration (per 1K tokens)
# ============================================================================

MODEL_COSTS = {
    "claude-3-5-sonnet": 0.015,
    "deepseek-chat": 0.002,
    "gpt-4o": 0.03,
    "gpt-4": 0.06,
    "ollama": 0.0,
}

# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections with security."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.max_connections_per_ip: Dict[str, int] = defaultdict(int)
    
    async def connect(self, websocket: WebSocket, client_ip: str):
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

manager = ConnectionManager()

# ============================================================================
# Security Metrics
# ============================================================================

security_metrics = {
    "requests_blocked": 0,
    "threats_detected": 0,
    "invalid_messages": 0,
    "start_time": datetime.now().isoformat()
}

# ============================================================================
# Simulation Task
# ============================================================================

async def simulate_agent_updates():
    """Background task to simulate agent activity."""
    while True:
        if crew_state.is_running:
            for agent_id, agent in agents.items():
                if agent.status == AgentStatus.RUNNING:
                    tokens = random.randint(100, 600)
                    cost_per_token = MODEL_COSTS.get(agent.model, 0.01)
                    cost_increment = (tokens / 1000) * cost_per_token
                    
                    agent.cost = round(agent.cost + cost_increment, 4)
                    agent.last_update = datetime.now().isoformat()
                    
                    crew_state.total_cost = round(
                        sum(a.cost for a in agents.values()), 4
                    )
                    
                    if crew_state.total_cost > crew_state.budget_limit:
                        crew_state.is_running = False
                        await manager.broadcast({
                            "type": "crew_status",
                            "data": {
                                "is_running": False,
                                "message": "Budget limit exceeded. Crew paused."
                            }
                        })
                        print(f"[Crew] 🛑 Budget exceeded! Total: ${crew_state.total_cost:.4f}")
                        break
                    
                    await manager.broadcast({
                        "type": "cost_update",
                        "agent_id": agent_id,
                        "data": {
                            "cost": agent.cost,
                            "status": agent.status.value
                        }
                    })
        
        await asyncio.sleep(2)

# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background simulation task."""
    task = asyncio.create_task(simulate_agent_updates())
    yield
    task.cancel()

app = FastAPI(
    title="MW-Vision Backend",
    description="Secure WebSocket backend for MW-Vision Visual Command Center",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
app.add_middleware(SecurityHeadersMiddleware)

# Restricted CORS (only localhost for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5189", "http://127.0.0.1:5189"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REST Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {
        "name": "MW-Vision Backend",
        "status": "running",
        "version": "2.0.0",
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now() - datetime.fromisoformat(security_metrics["start_time"])).total_seconds()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_clients": len(manager.active_connections),
        "crew_running": crew_state.is_running,
        "total_cost": crew_state.total_cost,
        "uptime_seconds": round(uptime, 2)
    }

@app.get("/api/agents")
async def get_agents():
    return {
        "agents": list(agents.values()),
        "total_cost": crew_state.total_cost
    }

@app.get("/api/crew")
async def get_crew_state():
    return crew_state.model_dump()

@app.get("/api/security")
async def get_security_metrics():
    """Security metrics endpoint."""
    return {
        "security_metrics": security_metrics,
        "active_connections": len(manager.active_connections),
        "per_ip_connections": dict(manager.max_connections_per_ip)
    }

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
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
                    security_metrics["invalid_messages"] += 1
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Invalid JSON format"}
                    })
                    continue
                
                await handle_message(message)
                
            except json.JSONDecodeError:
                security_metrics["invalid_messages"] += 1
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, client_ip)

async def handle_message(message: dict):
    """Process incoming WebSocket messages with validation."""
    msg_type = message.get("type")
    agent_id = message.get("agent_id")
    data = message.get("data", {})
    
    # Validate message type
    valid_types = {"crew_command", "agent_command", "ping"}
    if msg_type not in valid_types:
        security_metrics["threats_detected"] += 1
        print(f"[WS] ⚠️ Invalid message type: {msg_type}")
        return
    
    print(f"[WS] Received: {msg_type} - {message}")
    
    if msg_type == "ping":
        await manager.broadcast({"type": "pong", "data": {"timestamp": datetime.now().isoformat()}})
        return
    
    if msg_type == "crew_command":
        command = data.get("command")
        valid_commands = {"launch", "pause", "stop"}
        
        if command not in valid_commands:
            security_metrics["threats_detected"] += 1
            return
        
        if command == "launch":
            crew_state.is_running = True
            for agent in agents.values():
                agent.status = AgentStatus.RUNNING
                agent.last_update = datetime.now().isoformat()
            
            await manager.broadcast({
                "type": "crew_status",
                "data": {"is_running": True}
            })
            print("[Crew] 🚀 Launched")
            
        elif command == "pause":
            crew_state.is_running = False
            for agent in agents.values():
                if agent.status == AgentStatus.RUNNING:
                    agent.status = AgentStatus.PAUSED
            
            await manager.broadcast({
                "type": "crew_status",
                "data": {"is_running": False}
            })
            print("[Crew] ⏸️ Paused")
            
        elif command == "stop":
            crew_state.is_running = False
            for agent in agents.values():
                agent.status = AgentStatus.IDLE
            
            await manager.broadcast({
                "type": "crew_status",
                "data": {"is_running": False}
            })
            print("[Crew] ⏹️ Stopped")
    
    elif msg_type == "agent_command" and agent_id:
        command = data.get("command")
        valid_commands = {"start", "pause", "stop"}
        
        if command not in valid_commands or agent_id not in agents:
            security_metrics["threats_detected"] += 1
            return
        
        if agent_id in agents:
            agent = agents[agent_id]
            
            if command == "start":
                agent.status = AgentStatus.RUNNING
            elif command == "pause":
                agent.status = AgentStatus.PAUSED
            elif command == "stop":
                agent.status = AgentStatus.IDLE
            
            await manager.broadcast({
                "type": "agent_update",
                "agent_id": agent_id,
                "data": {"status": agent.status.value}
            })

# ============================================================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
