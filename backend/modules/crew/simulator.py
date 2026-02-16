"""
Agent Activity Simulator
Background task to simulate agent activity and cost tracking
"""

import asyncio
import random
from datetime import datetime

from ..agents.models import AgentStatus
from ..agents.state import agents
from ..websocket.manager import manager
from .state import crew_state


# Model Cost Configuration (per 1K tokens)
MODEL_COSTS = {
    "claude-3-5-sonnet": 0.015,
    "deepseek-chat": 0.002,
    "gpt-4o": 0.03,
    "gpt-4": 0.06,
    "ollama": 0.0,
}


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
