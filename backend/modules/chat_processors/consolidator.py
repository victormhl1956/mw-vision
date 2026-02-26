"""
Module: consolidator.py
Project: MW-Vision | MindWareHouse
Author: Claudia CLI (AI Field Commander)
Date: 2026-02-25
Purpose: Merge all chat exports (Claude, Gemini, etc.) into a unified
         knowledge corpus. Deduplicates, tags, and prepares for RAG indexing.
Dependencies: json, pathlib, hashlib
Integration Points: export_claude.py, export_gemini.py, rag/indexer.py
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from export_claude import (
    ConversationExport,
    export_to_unified_format,
    scan_claude_transcripts,
)
from export_gemini import scan_gemini_exports

logger = logging.getLogger("mw.consolidator")


@dataclass
class ConsolidatedCorpus:
    """Unified knowledge corpus from all chat sources."""

    timestamp: str = ""
    total_conversations: int = 0
    total_messages: int = 0
    sources: dict[str, int] = field(default_factory=dict)
    conversations: list[dict[str, Any]] = field(default_factory=list)
    deduplicated: int = 0

    @property
    def source_summary(self) -> str:
        parts = [f"{k}: {v}" for k, v in self.sources.items()]
        return ", ".join(parts)


def _content_hash(content: str) -> str:
    """Generate a short hash for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def consolidate_exports(
    exports: list[ConversationExport],
) -> ConsolidatedCorpus:
    """
    Merge multiple conversation exports into a unified corpus.

    Deduplicates by content hash.

    Args:
        exports: List of ConversationExport from various sources.

    Returns:
        ConsolidatedCorpus ready for RAG indexing.
    """
    corpus = ConsolidatedCorpus(
        timestamp=datetime.now(UTC).isoformat(),
    )

    seen_hashes: set[str] = set()

    for export in exports:
        unified = export_to_unified_format(export)

        # Why: dedup by content hash of first message
        if export.messages:
            first_content = export.messages[0].content[:200]
            content_hash = _content_hash(first_content)
            if content_hash in seen_hashes:
                corpus.deduplicated += 1
                continue
            seen_hashes.add(content_hash)

        corpus.conversations.append(unified)
        corpus.total_conversations += 1
        corpus.total_messages += export.message_count

        source = export.source
        corpus.sources[source] = corpus.sources.get(source, 0) + 1

    logger.info(
        "Consolidated %d conversations (%d deduplicated)",
        corpus.total_conversations,
        corpus.deduplicated,
    )

    return corpus


def consolidate_from_directories(
    claude_dir: Path | None = None,
    gemini_dir: Path | None = None,
) -> ConsolidatedCorpus:
    """
    Scan directories and consolidate all chat exports.

    Args:
        claude_dir: Directory with Claude JSONL transcripts.
        gemini_dir: Directory with Gemini JSON exports.

    Returns:
        ConsolidatedCorpus.
    """
    all_exports: list[ConversationExport] = []

    if claude_dir and claude_dir.exists():
        claude_exports = scan_claude_transcripts(claude_dir)
        all_exports.extend(claude_exports)

    if gemini_dir and gemini_dir.exists():
        gemini_exports = scan_gemini_exports(gemini_dir)
        all_exports.extend(gemini_exports)

    return consolidate_exports(all_exports)


def save_corpus(
    corpus: ConsolidatedCorpus,
    output_path: Path,
) -> Path:
    """
    Save consolidated corpus to a JSON file.

    Args:
        corpus: The corpus to save.
        output_path: Path for the output file.

    Returns:
        Path to saved file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(corpus)
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(
        "Corpus saved: %s (%d conversations, %d messages)",
        output_path,
        corpus.total_conversations,
        corpus.total_messages,
    )
    return output_path


def load_corpus(corpus_path: Path) -> ConsolidatedCorpus:
    """
    Load a previously saved corpus.

    Args:
        corpus_path: Path to the corpus JSON file.

    Returns:
        ConsolidatedCorpus.

    Raises:
        FileNotFoundError: If corpus_path does not exist.
    """
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    data = json.loads(corpus_path.read_text(encoding="utf-8"))

    return ConsolidatedCorpus(
        timestamp=data.get("timestamp", ""),
        total_conversations=data.get("total_conversations", 0),
        total_messages=data.get("total_messages", 0),
        sources=data.get("sources", {}),
        conversations=data.get("conversations", []),
        deduplicated=data.get("deduplicated", 0),
    )


def extract_knowledge_chunks(
    corpus: ConsolidatedCorpus,
    max_chunk_chars: int = 2000,
) -> list[dict[str, Any]]:
    """
    Extract indexable knowledge chunks from the corpus.

    Splits conversations into chunks suitable for RAG indexing.

    Args:
        corpus: Consolidated corpus.
        max_chunk_chars: Maximum characters per chunk.

    Returns:
        List of chunk dicts with text, metadata, and source info.
    """
    chunks = []

    for conv in corpus.conversations:
        conv_id = conv.get("conversation_id", "")
        source = conv.get("source", "unknown")
        title = conv.get("title", "")

        current_chunk = ""
        chunk_messages = 0

        for msg in conv.get("messages", []):
            content = msg.get("content", "")
            role = msg.get("role", "")

            # Why: prefix with role for context
            text = f"[{role}]: {content}\n"

            if len(current_chunk) + len(text) > max_chunk_chars:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "source": source,
                        "conversation_id": conv_id,
                        "title": title,
                        "message_count": chunk_messages,
                    })
                current_chunk = text
                chunk_messages = 1
            else:
                current_chunk += text
                chunk_messages += 1

        # Why: add remaining chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "source": source,
                "conversation_id": conv_id,
                "title": title,
                "message_count": chunk_messages,
            })

    logger.info(
        "Extracted %d knowledge chunks from %d conversations",
        len(chunks),
        corpus.total_conversations,
    )
    return chunks
