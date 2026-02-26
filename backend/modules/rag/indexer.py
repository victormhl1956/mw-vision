"""
Module: indexer.py
Project: MW-Vision | MindWareHouse
Author: Claudia CLI (AI Field Commander)
Date: 2026-02-25
Purpose: Index consolidated chat knowledge into a vector store for
         semantic retrieval. Uses sentence embeddings and FAISS for
         fast similarity search.
Dependencies: json, pathlib, numpy (optional), faiss-cpu (optional)
Integration Points: consolidator.py, retriever.py
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("mw.rag.indexer")

INDEX_DIR = Path(__file__).parent.parent.parent / "data" / "rag_index"


@dataclass
class IndexedChunk:
    """A chunk stored in the index."""

    chunk_id: int
    text: str
    source: str = ""
    conversation_id: str = ""
    title: str = ""
    embedding: list[float] = field(default_factory=list)


@dataclass
class IndexStats:
    """Statistics about the current index."""

    total_chunks: int = 0
    total_conversations: int = 0
    sources: dict[str, int] = field(default_factory=dict)
    index_size_bytes: int = 0
    embedding_dim: int = 0
    last_updated: str = ""


class KnowledgeIndexer:
    """
    Index knowledge chunks for semantic retrieval.

    Supports two backends:
    - FAISS (fast, requires faiss-cpu): Vector similarity search
    - Simple (fallback): Keyword-based search with TF-IDF-like scoring
    """

    def __init__(
        self,
        index_dir: Path | None = None,
        embedding_dim: int = 384,
    ):
        if embedding_dim < 1:
            raise ValueError(f"embedding_dim must be >= 1, got {embedding_dim}")

        self.index_dir = index_dir or INDEX_DIR
        self.embedding_dim = embedding_dim
        self.chunks: list[IndexedChunk] = []
        self._faiss_index = None
        self._use_faiss = False

        # Why: try to use FAISS, fall back to simple search
        try:
            import faiss

            self._faiss_index = faiss.IndexFlatL2(embedding_dim)
            self._use_faiss = True
            logger.info("FAISS backend initialized (dim=%d)", embedding_dim)
        except ImportError:
            logger.info(
                "FAISS not available, using simple keyword search"
            )

    def add_chunks(
        self,
        chunks: list[dict[str, Any]],
        compute_embeddings: bool = True,
    ) -> int:
        """
        Add knowledge chunks to the index.

        Args:
            chunks: List of chunk dicts from consolidator.
            compute_embeddings: Whether to compute embeddings.

        Returns:
            Number of chunks added.
        """
        added = 0

        for chunk_data in chunks:
            chunk = IndexedChunk(
                chunk_id=len(self.chunks),
                text=chunk_data.get("text", ""),
                source=chunk_data.get("source", ""),
                conversation_id=chunk_data.get(
                    "conversation_id", ""
                ),
                title=chunk_data.get("title", ""),
            )

            if not chunk.text:
                continue

            if compute_embeddings and self._use_faiss:
                embedding = self._compute_embedding(chunk.text)
                chunk.embedding = embedding
                self._add_to_faiss(embedding)

            self.chunks.append(chunk)
            added += 1

        logger.info("Added %d chunks to index", added)
        return added

    def _compute_embedding(self, text: str) -> list[float]:
        """
        Compute embedding for a text chunk.

        Uses a simple bag-of-words approach as fallback when
        sentence-transformers is not available.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        try:
            # Why: try sentence-transformers first
            from sentence_transformers import SentenceTransformer

            if not hasattr(self, "_model"):
                self._model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
            embedding = self._model.encode(text).tolist()
            return embedding
        except ImportError:
            # Why: simple hash-based embedding as fallback
            return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> list[float]:
        """Generate a simple deterministic embedding from text."""
        import hashlib

        words = text.lower().split()
        embedding = [0.0] * self.embedding_dim

        for i, word in enumerate(words):
            h = int(
                hashlib.sha256(word.encode()).hexdigest(), 16
            )
            idx = h % self.embedding_dim
            embedding[idx] += 1.0 / (i + 1)

        # Why: normalize
        magnitude = sum(v * v for v in embedding) ** 0.5
        if magnitude > 0:
            embedding = [v / magnitude for v in embedding]

        return embedding

    def _add_to_faiss(self, embedding: list[float]) -> None:
        """Add a single embedding to the FAISS index."""
        if self._faiss_index is not None:
            import numpy as np

            vec = np.array([embedding], dtype=np.float32)
            self._faiss_index.add(vec)

    def save(self) -> Path:
        """
        Save the index to disk.

        Returns:
            Path to the index directory.
        """
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Why: save chunks as JSON
        chunks_path = self.index_dir / "chunks.json"
        chunks_data = [
            {
                "chunk_id": c.chunk_id,
                "text": c.text,
                "source": c.source,
                "conversation_id": c.conversation_id,
                "title": c.title,
            }
            for c in self.chunks
        ]
        chunks_path.write_text(
            json.dumps(chunks_data, ensure_ascii=False),
            encoding="utf-8",
        )

        # Why: save FAISS index if available
        if self._use_faiss and self._faiss_index is not None:
            import faiss

            faiss_path = self.index_dir / "faiss.index"
            faiss.write_index(
                self._faiss_index, str(faiss_path)
            )

        # Why: save metadata
        stats = self.get_stats()
        meta_path = self.index_dir / "metadata.json"
        meta_path.write_text(
            json.dumps(
                {
                    "total_chunks": stats.total_chunks,
                    "embedding_dim": self.embedding_dim,
                    "use_faiss": self._use_faiss,
                    "last_updated": stats.last_updated,
                    "sources": stats.sources,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        logger.info(
            "Index saved: %s (%d chunks)", self.index_dir, len(self.chunks)
        )
        return self.index_dir

    def load(self) -> bool:
        """
        Load index from disk.

        Returns:
            True if loaded successfully.
        """
        chunks_path = self.index_dir / "chunks.json"
        if not chunks_path.exists():
            logger.warning("No index found at %s", self.index_dir)
            return False

        try:
            chunks_data = json.loads(
                chunks_path.read_text(encoding="utf-8")
            )
            self.chunks = [
                IndexedChunk(**c) for c in chunks_data
            ]

            # Why: reload FAISS index
            faiss_path = self.index_dir / "faiss.index"
            if self._use_faiss and faiss_path.exists():
                import faiss

                self._faiss_index = faiss.read_index(
                    str(faiss_path)
                )

            logger.info(
                "Index loaded: %d chunks", len(self.chunks)
            )
            return True
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load index: %s", exc)
            return False

    def get_stats(self) -> IndexStats:
        """Get current index statistics."""
        sources: dict[str, int] = {}
        conv_ids: set[str] = set()

        for chunk in self.chunks:
            sources[chunk.source] = (
                sources.get(chunk.source, 0) + 1
            )
            if chunk.conversation_id:
                conv_ids.add(chunk.conversation_id)

        return IndexStats(
            total_chunks=len(self.chunks),
            total_conversations=len(conv_ids),
            sources=sources,
            embedding_dim=self.embedding_dim,
            last_updated=datetime.now(UTC).isoformat(),
        )
