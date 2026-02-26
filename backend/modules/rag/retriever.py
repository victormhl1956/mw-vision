"""
Module: retriever.py
Project: MW-Vision | MindWareHouse
Author: Claudia CLI (AI Field Commander)
Date: 2026-02-25
Purpose: Query the indexed knowledge base for semantic retrieval.
         Supports FAISS vector search and keyword fallback.
Dependencies: json, pathlib
Integration Points: indexer.py, pcm/context_manager.py
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from indexer import IndexedChunk, KnowledgeIndexer

logger = logging.getLogger("mw.rag.retriever")


@dataclass
class RetrievalResult:
    """A single retrieval result with relevance score."""

    chunk_id: int
    text: str
    score: float
    source: str = ""
    conversation_id: str = ""
    title: str = ""


@dataclass
class RetrievalResponse:
    """Response from a retrieval query."""

    query: str
    results: list[RetrievalResult] = field(default_factory=list)
    total_searched: int = 0
    method: str = ""  # "faiss", "keyword", "hybrid"

    @property
    def top_result(self) -> RetrievalResult | None:
        return self.results[0] if self.results else None

    @property
    def has_results(self) -> bool:
        return len(self.results) > 0


class KnowledgeRetriever:
    """
    Retrieve relevant knowledge chunks from the indexed corpus.

    Supports:
    - Vector search via FAISS (semantic similarity)
    - Keyword search (TF-IDF-like scoring)
    - Hybrid search (combines both)
    """

    def __init__(self, indexer: KnowledgeIndexer):
        self.indexer = indexer

    def search(
        self,
        query: str,
        top_k: int = 5,
        method: str = "auto",
        min_score: float = 0.0,
    ) -> RetrievalResponse:
        """
        Search the knowledge base.

        Args:
            query: Natural language query.
            top_k: Maximum results to return.
            method: Search method ("faiss", "keyword", "auto").
            min_score: Minimum score threshold.

        Returns:
            RetrievalResponse with ranked results.
        """
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")
        if method not in ("auto", "faiss", "keyword"):
            logger.warning("Unknown method '%s', falling back to keyword", method)
            method = "keyword"

        if not self.indexer.chunks:
            return RetrievalResponse(
                query=query,
                total_searched=0,
                method="none",
            )

        # Why: auto-select method based on FAISS availability
        if method == "auto":
            method = "faiss" if self.indexer._use_faiss else "keyword"

        if method == "faiss":
            response = self._faiss_search(query, top_k)
        elif method == "keyword":
            response = self._keyword_search(query, top_k)
        else:
            response = self._keyword_search(query, top_k)

        # Why: filter by minimum score
        if min_score > 0:
            response.results = [
                r for r in response.results if r.score >= min_score
            ]

        return response

    def _faiss_search(
        self, query: str, top_k: int
    ) -> RetrievalResponse:
        """Search using FAISS vector similarity."""
        response = RetrievalResponse(
            query=query,
            total_searched=len(self.indexer.chunks),
            method="faiss",
        )

        embedding = self.indexer._compute_embedding(query)

        try:
            import numpy as np

            vec = np.array([embedding], dtype=np.float32)
            distances, indices = self.indexer._faiss_index.search(
                vec, min(top_k, len(self.indexer.chunks))
            )

            for dist, idx in zip(distances[0], indices[0], strict=False):
                if idx < 0 or idx >= len(self.indexer.chunks):
                    continue

                chunk = self.indexer.chunks[idx]
                # Why: convert L2 distance to similarity score (0-1)
                score = 1.0 / (1.0 + float(dist))

                response.results.append(
                    RetrievalResult(
                        chunk_id=chunk.chunk_id,
                        text=chunk.text,
                        score=score,
                        source=chunk.source,
                        conversation_id=chunk.conversation_id,
                        title=chunk.title,
                    )
                )

        except Exception as exc:
            logger.error("FAISS search failed: %s", exc)
            return self._keyword_search(query, top_k)

        return response

    def _keyword_search(
        self, query: str, top_k: int
    ) -> RetrievalResponse:
        """Search using keyword matching with TF-IDF-like scoring."""
        response = RetrievalResponse(
            query=query,
            total_searched=len(self.indexer.chunks),
            method="keyword",
        )

        query_terms = set(
            re.findall(r"\w+", query.lower())
        )
        if not query_terms:
            return response

        scored: list[tuple[float, IndexedChunk]] = []

        for chunk in self.indexer.chunks:
            chunk_terms = set(
                re.findall(r"\w+", chunk.text.lower())
            )
            if not chunk_terms:
                continue

            # Why: Jaccard-like similarity with term frequency boost
            intersection = query_terms & chunk_terms
            if not intersection:
                continue

            # Why: score = matched terms / query terms * IDF-like boost
            base_score = len(intersection) / len(query_terms)

            # Why: boost for exact phrase matches
            if query.lower() in chunk.text.lower():
                base_score *= 1.5

            # Why: boost for title matches
            if chunk.title and any(
                t in chunk.title.lower() for t in query_terms
            ):
                base_score *= 1.2

            scored.append((base_score, chunk))

        # Why: sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        for score, chunk in scored[:top_k]:
            response.results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=score,
                    source=chunk.source,
                    conversation_id=chunk.conversation_id,
                    title=chunk.title,
                )
            )

        return response

    def get_context_for_prompt(
        self,
        query: str,
        max_tokens: int = 2000,
        top_k: int = 3,
    ) -> str:
        """
        Retrieve relevant context formatted for LLM prompt injection.

        Args:
            query: The user's question or topic.
            max_tokens: Approximate max tokens for context.
            top_k: Number of chunks to retrieve.

        Returns:
            Formatted context string for prompt augmentation.
        """
        response = self.search(query, top_k=top_k)

        if not response.has_results:
            return ""

        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # rough token-to-char estimate

        for result in response.results:
            if total_chars + len(result.text) > max_chars:
                break

            context_parts.append(
                f"[Source: {result.source} | {result.title}]\n"
                f"{result.text}\n"
            )
            total_chars += len(result.text)

        return "\n---\n".join(context_parts)


def format_retrieval_response(
    response: RetrievalResponse,
) -> str:
    """Format retrieval response for display."""
    lines = [
        f"Query: {response.query}",
        f"Method: {response.method}",
        f"Results: {len(response.results)}/{response.total_searched}",
        "",
    ]

    for i, result in enumerate(response.results, 1):
        lines.append(
            f"  [{i}] Score: {result.score:.3f}"
            f" | {result.source} | {result.title}"
        )
        preview = result.text[:100].replace("\n", " ")
        lines.append(f"      {preview}...")
        lines.append("")

    return "\n".join(lines)
