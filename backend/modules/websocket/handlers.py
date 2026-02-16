"""
WebSocket Message Handlers
Processes incoming WebSocket messages with validation
"""

from datetime import datetime
from typing import Dict, Any

from ..agents.models import AgentStatus
from ..agents.state import agents
from ..crew.state import crew_state
from ..security.metrics import security_metrics
from .manager import manager


async def handle_message(message: Dict[str, Any]):
    """Process incoming WebSocket messages with validation."""
    msg_type = message.get("type")
    agent_id = message.get("agent_id")
    data = message.get("data", {})

    # Validate message type
    valid_types = {"crew_command", "agent_command", "ping"}
    if msg_type not in valid_types:
        security_metrics.increment("threats_detected")
        print(f"[WS] ⚠️ Invalid message type: {msg_type}")
        return

    print(f"[WS] Received: {msg_type} - {message}")

    if msg_type == "ping":
        await manager.broadcast({"type": "pong", "data": {"timestamp": datetime.now().isoformat()}})
        return

    if msg_type == "crew_command":
        await handle_crew_command(data)

    elif msg_type == "agent_command" and agent_id:
        await handle_agent_command(agent_id, data)


async def handle_crew_command(data: Dict[str, Any]):
    """Handle crew control commands"""
    command = data.get("command")
    valid_commands = {"launch", "pause", "stop"}

    if command not in valid_commands:
        security_metrics.increment("threats_detected")
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


async def handle_agent_command(agent_id: str, data: Dict[str, Any]):
    """Handle individual agent commands"""
    command = data.get("command")
    valid_commands = {"start", "pause", "stop"}

    if command not in valid_commands or agent_id not in agents:
        security_metrics.increment("threats_detected")
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
