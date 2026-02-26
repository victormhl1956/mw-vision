"""
Module: export_claude.py
Project: MW-Vision | MindWareHouse
Author: Claudia CLI (AI Field Commander)
Date: 2026-02-25
Purpose: Export and parse Claude conversation transcripts into a unified
         format for knowledge consolidation. Handles Claude Code JSONL
         transcripts and Anthropic API conversation logs.
Dependencies: json, pathlib, dataclasses
Integration Points: consolidator.py, rag/indexer.py
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("mw.export.claude")


@dataclass
class ConversationMessage:
    """A single message in a conversation."""

    role: str  # "human", "assistant", "system"
    content: str
    timestamp: str = ""
    model: str = ""
    tool_calls: list[str] = field(default_factory=list)
    token_count: int = 0


@dataclass
class ConversationExport:
    """Exported conversation with metadata."""

    source: str = "claude"
    conversation_id: str = ""
    title: str = ""
    timestamp: str = ""
    messages: list[ConversationMessage] = field(default_factory=list)
    total_tokens: int = 0
    model: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def assistant_messages(self) -> list[ConversationMessage]:
        return [m for m in self.messages if m.role == "assistant"]

    @property
    def human_messages(self) -> list[ConversationMessage]:
        return [m for m in self.messages if m.role == "human"]


def parse_jsonl_transcript(file_path: Path) -> ConversationExport:
    """
    Parse a Claude Code JSONL transcript file.

    Claude Code stores transcripts as JSONL with one JSON object
    per line, each containing role, content, and metadata.

    Args:
        file_path: Path to the .jsonl transcript file.

    Returns:
        ConversationExport with all messages.

    Raises:
        FileNotFoundError: If file_path does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Transcript not found: {file_path}")

    export = ConversationExport(
        source="claude_code",
        conversation_id=file_path.stem,
        timestamp=datetime.now(UTC).isoformat(),
    )

    lines = file_path.read_text(encoding="utf-8").strip().split("\n")

    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            msg = _parse_jsonl_entry(entry)
            if msg:
                export.messages.append(msg)
        except json.JSONDecodeError:
            logger.warning(
                "Skipping malformed JSONL line in %s", file_path
            )

    if export.messages:
        export.title = _infer_title(export.messages)

    return export


def _parse_jsonl_entry(entry: dict[str, Any]) -> ConversationMessage | None:
    """Parse a single JSONL entry into a ConversationMessage."""
    role = entry.get("role", "")
    if not role:
        return None

    content = ""
    raw_content = entry.get("content", "")
    if isinstance(raw_content, str):
        content = raw_content
    elif isinstance(raw_content, list):
        # Why: Anthropic API format uses list of content blocks
        text_parts = []
        tool_calls = []
        for block in raw_content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_calls.append(block.get("name", "unknown"))
        content = "\n".join(text_parts)
    else:
        content = str(raw_content)

    if not content and not entry.get("tool_calls"):
        return None

    return ConversationMessage(
        role=role,
        content=content,
        timestamp=entry.get("timestamp", ""),
        model=entry.get("model", ""),
        tool_calls=entry.get("tool_calls", []),
        token_count=entry.get("usage", {}).get("total_tokens", 0),
    )


def parse_api_conversation(
    messages: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> ConversationExport:
    """
    Parse an Anthropic API conversation (messages format).

    Args:
        messages: List of message dicts with role/content.
        metadata: Optional metadata (model, id, etc.).

    Returns:
        ConversationExport.
    """
    metadata = metadata or {}
    export = ConversationExport(
        source="claude_api",
        conversation_id=metadata.get("id", ""),
        model=metadata.get("model", ""),
        timestamp=datetime.now(UTC).isoformat(),
    )

    for msg in messages:
        parsed = _parse_jsonl_entry(msg)
        if parsed:
            export.messages.append(parsed)

    if export.messages:
        export.title = _infer_title(export.messages)

    return export


def _infer_title(messages: list[ConversationMessage]) -> str:
    """Infer a conversation title from the first human message."""
    for msg in messages:
        if msg.role == "human" and msg.content:
            title = msg.content[:100].strip()
            if "\n" in title:
                title = title.split("\n")[0]
            return title
    return "Untitled conversation"


def export_to_unified_format(
    export: ConversationExport,
) -> dict[str, Any]:
    """
    Convert to the unified MindWareHouse chat format.

    This format is consumed by consolidator.py and indexer.py.

    Args:
        export: ConversationExport to convert.

    Returns:
        Unified format dict.
    """
    return {
        "source": export.source,
        "conversation_id": export.conversation_id,
        "title": export.title,
        "timestamp": export.timestamp,
        "model": export.model,
        "message_count": export.message_count,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                "model": m.model,
                "token_count": m.token_count,
            }
            for m in export.messages
        ],
        "tags": export.tags,
    }


def scan_claude_transcripts(
    directory: Path,
) -> list[ConversationExport]:
    """
    Scan a directory for Claude Code JSONL transcripts.

    Args:
        directory: Directory to scan.

    Returns:
        List of parsed ConversationExports.
    """
    exports = []
    for jsonl_file in sorted(directory.glob("*.jsonl")):
        try:
            export = parse_jsonl_transcript(jsonl_file)
            exports.append(export)
            logger.info(
                "Parsed %s: %d messages",
                jsonl_file.name,
                export.message_count,
            )
        except (json.JSONDecodeError, FileNotFoundError) as exc:
            logger.warning("Skipping %s: %s", jsonl_file, exc)

    logger.info("Scanned %d Claude transcripts", len(exports))
    return exports
