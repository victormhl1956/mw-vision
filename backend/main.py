"""
MW-Vision Backend - FastAPI with WebSocket Support

Minimal backend for MW-Vision Visual Command Center.
Provides WebSocket connections for real-time agent updates.

Features:
- WebSocket endpoint for real-time communication
- Agent status management
- Cost tracking simulation
- Crew control (launch, pause, stop)

Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum

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
    type: str  # agent_update, cost_update, task_complete, crew_status, error
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
    "ollama": 0.0,  # Free (local)
}

# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Error sending message: {e}")

manager = ConnectionManager()

# ============================================================================
# Simulation Task
# ============================================================================

async def simulate_agent_updates():
    """Background task to simulate agent activity."""
    while True:
        if crew_state.is_running:
            for agent_id, agent in agents.items():
                if agent.status == AgentStatus.RUNNING:
                    # Simulate token usage (100-600 tokens)
                    tokens = random.randint(100, 600)
                    cost_per_token = MODEL_COSTS.get(agent.model, 0.01)
                    cost_increment = (tokens / 1000) * cost_per_token
                    
                    # Update agent cost
                    agent.cost = round(agent.cost + cost_increment, 4)
                    agent.last_update = datetime.now().isoformat()
                    
                    # Update crew total
                    crew_state.total_cost = round(
                        sum(a.cost for a in agents.values()), 4
                    )
                    
                    # Check budget
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
                    
                    # Broadcast update
                    await manager.broadcast({
                        "type": "cost_update",
                        "agent_id": agent_id,
                        "data": {
                            "cost": agent.cost,
                            "status": agent.status.value
                        }
                    })
        
        await asyncio.sleep(2)  # Update every 2 seconds

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
    description="WebSocket backend for MW-Vision Visual Command Center",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "endpoints": {
            "websocket": "ws://localhost:8000/ws",
            "health": "/health",
            "agents": "/api/agents",
            "crew": "/api/crew"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_clients": len(manager.active_connections),
        "crew_running": crew_state.is_running,
        "total_cost": crew_state.total_cost
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

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": {
                "agents": [a.model_dump() for a in agents.values()],
                "crew": crew_state.model_dump()
            }
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_message(message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_message(message: dict):
    """Process incoming WebSocket messages."""
    msg_type = message.get("type")
    agent_id = message.get("agent_id")
    data = message.get("data", {})
    
    print(f"[WS] Received: {msg_type} - {message}")
    
    if msg_type == "crew_command":
        command = data.get("command")
        
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
