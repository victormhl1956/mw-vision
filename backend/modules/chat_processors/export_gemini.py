"""
Module: export_gemini.py
Project: MW-Vision | MindWareHouse
Author: Claudia CLI (AI Field Commander)
Date: 2026-02-25
Purpose: Export and parse Google Gemini conversation logs into the unified
         MindWareHouse format. Handles Gemini API response format and
         Google AI Studio exports.
Dependencies: json, pathlib, dataclasses
Integration Points: consolidator.py, rag/indexer.py
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from export_claude import ConversationExport, ConversationMessage

logger = logging.getLogger("mw.export.gemini")


def parse_gemini_json(file_path: Path) -> ConversationExport:
    """
    Parse a Gemini conversation JSON export.

    Google AI Studio exports conversations as JSON with contents[]
    array containing parts[].text for each role.

    Args:
        file_path: Path to the Gemini JSON export.

    Returns:
        ConversationExport with all messages.

    Raises:
        FileNotFoundError: If file_path does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Gemini export not found: {file_path}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini JSON %s: %s", file_path, exc)
        return ConversationExport(
            source="gemini",
            conversation_id=file_path.stem,
            timestamp=datetime.now(UTC).isoformat(),
        )
    export = ConversationExport(
        source="gemini",
        conversation_id=file_path.stem,
        timestamp=datetime.now(UTC).isoformat(),
    )

    # Why: Gemini exports can have different structures
    contents = data if isinstance(data, list) else data.get("contents", [])

    for entry in contents:
        msg = _parse_gemini_entry(entry)
        if msg:
            export.messages.append(msg)

    if export.messages:
        export.title = _infer_gemini_title(export.messages)

    export.model = data.get("model", "gemini") if isinstance(data, dict) else "gemini"

    return export


def _parse_gemini_entry(entry: dict[str, Any]) -> ConversationMessage | None:
    """Parse a single Gemini content entry."""
    role = entry.get("role", "")
    # Why: Gemini uses "user"/"model", normalize to "human"/"assistant"
    if role == "user":
        role = "human"
    elif role == "model":
        role = "assistant"

    if not role:
        return None

    parts = entry.get("parts", [])
    text_parts = []
    for part in parts:
        if isinstance(part, dict):
            if "text" in part:
                text_parts.append(part["text"])
        elif isinstance(part, str):
            text_parts.append(part)

    content = "\n".join(text_parts)
    if not content:
        return None

    return ConversationMessage(
        role=role,
        content=content,
        model="gemini",
    )


def parse_gemini_api_response(
    response: dict[str, Any],
    prompt: str = "",
) -> ConversationExport:
    """
    Parse a Gemini API generateContent response.

    Args:
        response: Raw API response dict.
        prompt: The original prompt sent.

    Returns:
        ConversationExport with the exchange.
    """
    export = ConversationExport(
        source="gemini_api",
        timestamp=datetime.now(UTC).isoformat(),
    )

    # Why: add the prompt as human message
    if prompt:
        export.messages.append(
            ConversationMessage(role="human", content=prompt)
        )

    # Why: extract response from candidates
    candidates = response.get("candidates", [])
    for candidate in candidates:
        content_obj = candidate.get("content", {})
        parts = content_obj.get("parts", [])
        text = "\n".join(
            p.get("text", "") for p in parts if isinstance(p, dict)
        )
        if text:
            export.messages.append(
                ConversationMessage(
                    role="assistant",
                    content=text,
                    model=response.get("modelVersion", "gemini"),
                )
            )

    # Why: extract token usage
    usage = response.get("usageMetadata", {})
    export.total_tokens = usage.get("totalTokenCount", 0)

    if export.messages:
        export.title = _infer_gemini_title(export.messages)

    return export


def _infer_gemini_title(messages: list[ConversationMessage]) -> str:
    """Infer title from first human message."""
    for msg in messages:
        if msg.role == "human" and msg.content:
            title = msg.content[:100].strip()
            if "\n" in title:
                title = title.split("\n")[0]
            return title
    return "Untitled Gemini conversation"


def scan_gemini_exports(
    directory: Path,
) -> list[ConversationExport]:
    """
    Scan a directory for Gemini JSON exports.

    Args:
        directory: Directory to scan for .json files.

    Returns:
        List of parsed ConversationExports.
    """
    exports = []
    for json_file in sorted(directory.glob("*.json")):
        try:
            export = parse_gemini_json(json_file)
            exports.append(export)
            logger.info(
                "Parsed Gemini %s: %d messages",
                json_file.name,
                export.message_count,
            )
        except (json.JSONDecodeError, FileNotFoundError) as exc:
            logger.warning("Skipping %s: %s", json_file, exc)

    logger.info("Scanned %d Gemini exports", len(exports))
    return exports
