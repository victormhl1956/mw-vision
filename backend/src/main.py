"""
MW-Vision Backend Server
Real-time telemetry for MoE operations
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import random
import uuid

# Agent state management
class Agent:
    def __init__(self, id: str, name: str, model: str):
        self.id = id
        self.name = name
        self.model = model
        self.status = "idle"  # idle, running, paused, error
        self.tasks_completed = 0
        self.total_cost = 0.0
        self.last_response_time = 0.0
        self.last_update = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "status": self.status,
            "tasksCompleted": self.tasks_completed,
            "totalCost": round(self.total_cost, 4),
            "lastResponseTime": round(self.last_response_time, 2),
            "lastUpdate": self.last_update
        }

# Initialize agents
agents: Dict[str, Agent] = {
    "debugger": Agent("debugger", "Debugger", "claude-3-5-sonnet"),
    "code-reviewer": Agent("code-reviewer", "Code Reviewer", "deepseek-chat"),
    "test-generator": Agent("test-generator", "Test Generator", "gpt-4o")
}

# Strategic Coordinator decisions
routing_history: List[dict] = []

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WebSocket] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        if not self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

# Background task: Simulate agent activity
async def simulate_agent_activity():
    """
    Background task that simulates MoE operations
    In real implementation, this would listen to actual agent events
    """
    while True:
        await asyncio.sleep(10)  # Every 10 seconds

        # Randomly pick an agent to "execute" a task
        agent_id = random.choice(list(agents.keys()))
        agent = agents[agent_id]

        # Simulate Strategic Coordinator routing decision
        complexity = random.randint(1, 10)
        should_use_haiku = complexity < 5

        decision = {
            "timestamp": datetime.now().isoformat(),
            "query": f"Simulated task #{agent.tasks_completed + 1}",
            "complexity": complexity,
            "selectedModel": "claude-3-haiku" if should_use_haiku else agent.model,
            "reasoning": (
                f"Low complexity ({complexity}/10) - routing to Haiku for cost efficiency"
                if should_use_haiku
                else f"High complexity ({complexity}/10) - routing to {agent.model} for quality"
            ),
            "estimatedCost": 0.001 if should_use_haiku else 0.01
        }

        routing_history.append(decision)

        # Update agent status
        agent.status = "running"
        agent.last_update = datetime.now().isoformat()

        await manager.broadcast({
            "type": "agent_status_changed",
            "agent": agent.to_dict()
        })

        await manager.broadcast({
            "type": "routing_decision",
            "decision": decision
        })

        # Simulate execution time
        execution_time = random.uniform(0.5, 2.5)  # 0.5 to 2.5 seconds
        await asyncio.sleep(execution_time)

        # Task completed
        actual_cost = decision["estimatedCost"] * random.uniform(0.8, 1.2)  # ±20% variance

        agent.tasks_completed += 1
        agent.total_cost += actual_cost
        agent.last_response_time = execution_time
        agent.status = "idle"
        agent.last_update = datetime.now().isoformat()

        await manager.broadcast({
            "type": "task_completed",
            "agent": agent.to_dict(),
            "decision": decision,
            "actualCost": round(actual_cost, 4),
            "responseTime": round(execution_time, 2)
        })

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(simulate_agent_activity())
    print("[Backend] Background task started")
    yield
    # Shutdown
    task.cancel()
    print("[Backend] Background task stopped")

# FastAPI app
app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5189", "http://127.0.0.1:5189"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API Endpoints
@app.get("/")
async def root():
    return {"status": "MW-Vision Backend Online", "version": "1.0.0"}

@app.get("/api/agents")
async def get_agents():
    """Get all agents status"""
    return [agent.to_dict() for agent in agents.values()]

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent status"""
    if agent_id not in agents:
        return {"error": "Agent not found"}, 404
    return agents[agent_id].to_dict()

@app.post("/api/agents/{agent_id}/execute")
async def execute_task(agent_id: str, task: dict):
    """Execute a task on specific agent"""
    if agent_id not in agents:
        return {"error": "Agent not found"}, 404

    agent = agents[agent_id]

    # Simulate Strategic Coordinator routing
    complexity = random.randint(1, 10)
    should_use_haiku = complexity < 5

    decision = {
        "timestamp": datetime.now().isoformat(),
        "query": task.get("task", "Manual execution"),
        "complexity": complexity,
        "selectedModel": "claude-3-haiku" if should_use_haiku else agent.model,
        "reasoning": (
            f"Low complexity ({complexity}/10) - routing to Haiku"
            if should_use_haiku
            else f"High complexity ({complexity}/10) - routing to {agent.model}"
        ),
        "estimatedCost": 0.001 if should_use_haiku else 0.01
    }

    routing_history.append(decision)

    # Update status
    agent.status = "running"
    agent.last_update = datetime.now().isoformat()

    await manager.broadcast({
        "type": "agent_status_changed",
        "agent": agent.to_dict()
    })

    await manager.broadcast({
        "type": "routing_decision",
        "decision": decision
    })

    # Simulate execution
    execution_time = random.uniform(0.5, 2.5)
    await asyncio.sleep(execution_time)

    # Complete task
    actual_cost = decision["estimatedCost"] * random.uniform(0.8, 1.2)

    agent.tasks_completed += 1
    agent.total_cost += actual_cost
    agent.last_response_time = execution_time
    agent.status = "idle"
    agent.last_update = datetime.now().isoformat()

    await manager.broadcast({
        "type": "task_completed",
        "agent": agent.to_dict(),
        "decision": decision,
        "actualCost": round(actual_cost, 4),
        "responseTime": round(execution_time, 2)
    })

    return {
        "success": True,
        "agent": agent.to_dict(),
        "decision": decision,
        "actualCost": round(actual_cost, 4),
        "responseTime": round(execution_time, 2)
    }

@app.get("/api/routing-history")
async def get_routing_history():
    """Get recent routing decisions"""
    return routing_history[-50:]  # Last 50 decisions

@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    total_cost = sum(agent.total_cost for agent in agents.values())
    total_tasks = sum(agent.tasks_completed for agent in agents.values())
    active_agents = sum(1 for agent in agents.values() if agent.status == "running")

    # Calculate savings vs all-Sonnet
    avg_sonnet_cost = 0.01
    all_sonnet_cost = total_tasks * avg_sonnet_cost
    savings = all_sonnet_cost - total_cost

    return {
        "totalCost": round(total_cost, 4),
        "totalTasks": total_tasks,
        "activeAgents": active_agents,
        "savings": round(savings, 4),
        "allSonnetCost": round(all_sonnet_cost, 4)
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time updates"""
    await manager.connect(websocket)

    # Send initial state
    await websocket.send_text(json.dumps({
        "type": "initial_state",
        "agents": [agent.to_dict() for agent in agents.values()],
        "routingHistory": routing_history[-10:]
    }))

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back (for ping/pong)
            await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("MW-VISION BACKEND STARTING")
    print("=" * 60)
    print(f"REST API: http://localhost:8000")
    print(f"WebSocket: ws://localhost:8000/ws")
    print(f"Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
