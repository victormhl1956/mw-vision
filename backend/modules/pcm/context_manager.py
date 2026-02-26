"""
Module: context_manager.py
Project: MW-Vision | MindWareHouse
Author: Claudia CLI (AI Field Commander)
Date: 2026-02-25
Purpose: PCM (Persistent Context Memory) bridge for MW-Vision.
         Connects to the PCM server (localhost:8008) to store and recall
         context across sessions and agents.
Dependencies: httpx (async), json
Integration Points: rag/retriever.py, chat_processors/, CLAUDE.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("mw.pcm")

PCM_BASE_URL = "http://localhost:8008"


@dataclass
class MemoryEntry:
    """A single PCM memory entry."""

    content: str
    category: str = "fact"
    importance: float = 0.7
    timestamp: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class RecallResult:
    """Result from a PCM recall query."""

    query: str
    entries: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0

    @property
    def has_results(self) -> bool:
        return len(self.entries) > 0


async def remember(
    content: str,
    category: str = "fact",
    importance: float = 0.7,
    keywords: list[str] | None = None,
) -> bool:
    """
    Store a memory entry in PCM.

    Args:
        content: The content to remember.
        category: Memory category (decision, error_fix, learning,
                  preference, pattern, fact, insight).
        importance: Importance score 0-1.
        keywords: Optional keywords for retrieval.

    Returns:
        True if stored successfully.
    """
    try:
        import httpx

        payload = {
            "content": content,
            "category": category,
            "importance": importance,
        }
        if keywords:
            payload["keywords"] = keywords

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{PCM_BASE_URL}/memory/remember",
                json=payload,
            )
            if resp.status_code == 200:
                logger.info("PCM: remembered [%s] %s", category, content[:50])
                return True
            logger.warning(
                "PCM remember failed: %d", resp.status_code
            )
            return False
    except Exception as exc:
        logger.warning("PCM unavailable: %s", exc)
        return False


async def recall(
    query: str = "",
    category: str = "",
    limit: int = 10,
) -> RecallResult:
    """
    Recall memories from PCM.

    Args:
        query: Search query (semantic).
        category: Filter by category.
        limit: Maximum entries to return.

    Returns:
        RecallResult with matching entries.
    """
    result = RecallResult(query=query)

    try:
        import httpx

        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        if category:
            params["category"] = category

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{PCM_BASE_URL}/memory/recall",
                params=params,
            )
            if resp.status_code == 200:
                entries = resp.json()
                if isinstance(entries, list):
                    result.entries = entries
                    result.total = len(entries)
                return result
            logger.warning(
                "PCM recall failed: %d", resp.status_code
            )
    except Exception as exc:
        logger.warning("PCM unavailable for recall: %s", exc)

    return result


async def checkpoint(summary: str) -> bool:
    """
    Save a session checkpoint to PCM.

    Args:
        summary: Checkpoint summary text.

    Returns:
        True if saved successfully.
    """
    return await remember(
        content=f"CHECKPOINT: {summary}",
        category="session_checkpoint",
        importance=0.8,
    )


async def record_decision(decision: str) -> bool:
    """
    Record an architectural decision to PCM.

    Args:
        decision: Description of the decision.

    Returns:
        True if saved successfully.
    """
    return await remember(
        content=decision,
        category="decision",
        importance=0.9,
    )


async def record_error_fix(error: str, fix: str) -> bool:
    """
    Record an error and its fix to PCM.

    Args:
        error: Description of the error.
        fix: How it was fixed.

    Returns:
        True if saved successfully.
    """
    return await remember(
        content=f"ERROR: {error} | FIX: {fix}",
        category="error_fix",
        importance=0.95,
    )


async def health_check() -> bool:
    """
    Check if PCM server is available.

    Returns:
        True if PCM is healthy.
    """
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{PCM_BASE_URL}/memory/health"
            )
            return resp.status_code == 200
    except Exception:
        return False


def remember_sync(
    content: str,
    category: str = "fact",
    importance: float = 0.7,
) -> bool:
    """
    Synchronous version of remember for non-async contexts.

    Args:
        content: Content to remember.
        category: Memory category.
        importance: Importance score.

    Returns:
        True if stored successfully.
    """
    try:
        import httpx

        payload = {
            "content": content,
            "category": category,
            "importance": importance,
        }
        resp = httpx.post(
            f"{PCM_BASE_URL}/memory/remember",
            json=payload,
            timeout=10.0,
        )
        return resp.status_code == 200
    except Exception as exc:
        logger.warning("PCM sync remember failed: %s", exc)
        return False


def recall_sync(
    query: str = "",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Synchronous version of recall.

    Args:
        query: Search query.
        limit: Maximum entries.

    Returns:
        List of memory entries.
    """
    try:
        import httpx

        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query

        resp = httpx.get(
            f"{PCM_BASE_URL}/memory/recall",
            params=params,
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as exc:
        logger.warning("PCM sync recall failed: %s", exc)

    return []
