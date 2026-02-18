"""Platform registry - 5 major AI chat platforms."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from .models import ParsedConversation, ParsedMessage


@dataclass
class PlatformConfig:
    name: str
    display_name: str
    url_patterns: List[str]
    content_fingerprints: List[str]
    export_formats: List[str]
    import_instructions: str
    parse_fn: Callable


def _parse_chatgpt(content: Any, source_url: str = None) -> ParsedConversation:
    if isinstance(content, str):
        content = json.loads(content)
    messages: List[ParsedMessage] = []
    title = None
    created_at = None
    if isinstance(content, list):
        conv = content[0] if content else {}
    else:
        conv = content
    title = conv.get("title")
    if conv.get("create_time"):
        created_at = datetime.fromtimestamp(conv["create_time"])
    mapping = conv.get("mapping", {})
    nodes = sorted(
        [v for v in mapping.values() if v.get("message")],
        key=lambda x: x.get("message", {}).get("create_time") or 0,
    )
    for node in nodes:
        msg = node.get("message", {})
        if not msg:
            continue
        author = msg.get("author", {})
        role = author.get("role", "unknown")
        if role in ("system", "tool"):
            continue
        parts = msg.get("content", {}).get("parts", [])
        text = " ".join(str(pt) for pt in parts if isinstance(pt, str)).strip()
        if not text:
            continue
        ts_raw = msg.get("create_time")
        ts = datetime.fromtimestamp(ts_raw) if ts_raw else None
        messages.append(ParsedMessage(
            role=role, content=text, message_id=msg.get("id"),
            timestamp=ts,
            metadata={"model": msg.get("metadata", {}).get("model_slug")},
        ))
    return ParsedConversation(
        messages=messages, platform="chatgpt", title=title,
        created_at=created_at, source_url=source_url,
    )


def _parse_claude(content: Any, source_url: str = None) -> ParsedConversation:
    messages: List[ParsedMessage] = []
    title = None
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return _parse_markdown_generic(content, "claude", source_url)
    if isinstance(content, dict):
        title = content.get("name") or content.get("title")
        raw_msgs = content.get("chat_messages", content.get("messages", []))
        for msg in raw_msgs:
            role = msg.get("role", "unknown")
            raw_content = msg.get("content", "")
            if isinstance(raw_content, list):
                text = " ".join(
                    block.get("text", "") for block in raw_content
                    if isinstance(block, dict) and block.get("type") == "text"
                ).strip()
            else:
                text = str(raw_content).strip()
            if not text:
                continue
            messages.append(ParsedMessage(role=role, content=text))
    return ParsedConversation(
        messages=messages, platform="claude", title=title, source_url=source_url,
    )


def _parse_gemini(content: Any, source_url: str = None) -> ParsedConversation:
    messages: List[ParsedMessage] = []
    title = None
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return _parse_markdown_generic(content, "gemini", source_url)
    if isinstance(content, dict):
        title = content.get("title") or content.get("name")
        raw_msgs = content.get("messages", content.get("history", []))
        for msg in raw_msgs:
            author = msg.get("author", msg.get("role", "unknown"))
            role = "user" if author in ("user", "human") else "assistant"
            raw_content = msg.get("content", msg.get("text", ""))
            if isinstance(raw_content, list):
                text = " ".join(
                    pt.get("text", "") for pt in raw_content if isinstance(pt, dict)
                ).strip()
            else:
                text = str(raw_content).strip()
            if not text:
                continue
            messages.append(ParsedMessage(role=role, content=text))
    return ParsedConversation(
        messages=messages, platform="gemini", title=title, source_url=source_url,
    )


def _parse_perplexity(content: Any, source_url: str = None) -> ParsedConversation:
    if isinstance(content, str):
        try:
            data = json.loads(content)
            msgs_raw = data.get("messages", [])
            messages = []
            for msg in msgs_raw:
                role = msg.get("role", "unknown")
                text = msg.get("content", "").strip()
                if text:
                    messages.append(ParsedMessage(role=role, content=text))
            return ParsedConversation(
                messages=messages, platform="perplexity",
                title=data.get("title"), source_url=source_url,
            )
        except json.JSONDecodeError:
            return _parse_markdown_generic(content, "perplexity", source_url)
    return ParsedConversation(messages=[], platform="perplexity", source_url=source_url)


def _parse_deepseek(content: Any, source_url: str = None) -> ParsedConversation:
    messages: List[ParsedMessage] = []
    title = None
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return _parse_markdown_generic(content, "deepseek", source_url)
    if isinstance(content, dict):
        title = content.get("title") or content.get("name")
        raw_msgs = content.get("messages", content.get("conversation", []))
        for msg in raw_msgs:
            role = msg.get("role", "unknown")
            text = msg.get("content", "").strip()
            if isinstance(text, list):
                text = " ".join(
                    block.get("text", "") for block in text if isinstance(block, dict)
                ).strip()
            if role not in ("system",) and text:
                messages.append(ParsedMessage(role=role, content=text))
    return ParsedConversation(
        messages=messages, platform="deepseek", title=title, source_url=source_url,
    )


def _parse_markdown_generic(
    content: str, platform: str, source_url: str = None
) -> ParsedConversation:
    messages: List[ParsedMessage] = []
    patterns = [
        "(?:^|\n)##\s*(User|Human|You|Assistant|AI|Claude|Gemini|GPT|DeepSeek|Perplexity):\s*\n(.*?)(?=\n##\s|\Z)",
        "(?:^|\n)\*\*(User|Human|You|Assistant|AI|Claude|Gemini|GPT|DeepSeek):\*\*\s*\n(.*?)(?=\n\*\*|\Z)",
        "(?:^|\n)(Human|User|Assistant|AI):\s*\n(.*?)(?=\n(?:Human|User|Assistant|AI):|\Z)",
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
        if matches:
            for m in matches:
                speaker = m.group(1).strip().lower()
                text = m.group(2).strip()
                if not text:
                    continue
                role = "user" if speaker in ("user", "human", "you") else "assistant"
                messages.append(ParsedMessage(role=role, content=text))
            break
    return ParsedConversation(messages=messages, platform=platform, source_url=source_url)


