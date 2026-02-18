"""
Chat Processor Module for MW-Vision.

Universal multi-platform conversation intelligence engine.
Supports: ChatGPT, Claude, Gemini, Perplexity, DeepSeek.

Usage:
    from modules.chat_processor import router          # FastAPI router
    from modules.chat_processor import parse_conversation, detect_platform
    from modules.chat_processor import analyze_conversation
"""
from .analyzer import analyze_conversation
from .platforms import PLATFORM_REGISTRY, detect_platform, parse_conversation
from .router import router

__all__ = [
    "router",
    "parse_conversation",
    "detect_platform",
    "analyze_conversation",
    "PLATFORM_REGISTRY",
]
