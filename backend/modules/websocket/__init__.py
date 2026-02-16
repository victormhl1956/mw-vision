"""
MW-Vision WebSocket Module
Manages WebSocket connections and message handling
"""

from .manager import ConnectionManager, manager
from .handlers import handle_message

__all__ = [
    'ConnectionManager',
    'manager',
    'handle_message'
]
