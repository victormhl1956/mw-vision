"""
Agent State Management
In-memory state (for MVP - use database in production)
"""

from typing import Dict
from .models import AgentModel


# In-memory agent state
agents: Dict[str, AgentModel] = {
    "1": AgentModel(id="1", name="Debugger", model="claude-3-5-sonnet"),
    "2": AgentModel(id="2", name="Code Reviewer", model="deepseek-chat"),
    "3": AgentModel(id="3", name="Test Generator", model="gpt-4o"),
}
