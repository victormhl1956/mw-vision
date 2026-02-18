"""
YT Processor Integration Router for MW-Vision.

Exposes YTP capabilities (semantic search, video intelligence, channel harvesting)
as REST endpoints within the CW-Vision ecosystem.

Endpoints:
  GET  /api/yt/search?q=...&top_k=5   — Semantic search over indexed transcriptions
  GET  /api/yt/status                   — Index stats + OSINT DB stats
  POST /api/yt/index/build              — Rebuild semantic index from DB
  GET  /api/yt/video/{video_id}         — Get full intelligence report for a video
  GET  /api/yt/videos                   — List indexed videos (paginated)
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

# ── Path Setup ────────────────────────────────────────────────────────────────

_YTP_ROOT = Path(r"L:\nicedev-Project\Youtube-processor")
_OSINT_DB = Path(r"L:\nicedev-Project\OSINT-MW\backend\database\osint.db")

if str(_YTP_ROOT) not in sys.path:
    sys.path.insert(0, str(_YTP_ROOT))

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/yt", tags=["yt_processor"])

# Lazy-loaded semantic index (avoid slow startup)
_index = None
_index_built = False


def _get_index():
    global _index
    if _index is None:
        try:
            from modules.semantic_index import SemanticIndex
            _index = SemanticIndex()
            _index.load()  # try loading persisted index
        except ImportError as e:
            raise HTTPException(
                status_code=503,
                detail=f"SemanticIndex module not available: {e}",
            )
    return _index


# ── Models ────────────────────────────────────────────────────────────────────


class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    count: int
    backend: str


class IndexBuildResponse(BaseModel):
    status: str
    videos_indexed: int
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/search", response_model=SearchResponse)
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
    min_score: float = Query(0.05, ge=0.0, le=1.0),
):
    """
    Semantic search over YouTube video transcriptions indexed in OSINT-MW.
    Returns ranked results with snippets.
    """
    idx = _get_index()
    results = idx.search(query=q, top_k=top_k, min_score=min_score)
    stats = idx.stats()
    return SearchResponse(
        query=q,
        results=[r.to_dict() for r in results],
        count=len(results),
        backend=stats.get("backend", "unknown"),
    )


@router.get("/status")
async def yt_status():
    """Index statistics and OSINT DB overview."""
    idx_stats = {}
    try:
        idx = _get_index()
        idx_stats = idx.stats()
    except Exception as e:
        idx_stats = {"error": str(e)}

    db_stats = {}
    if _OSINT_DB.exists():
        try:
            conn = sqlite3.connect(str(_OSINT_DB))
            r = conn.execute(
                "SELECT COUNT(*) as n FROM youtube_videos WHERE has_transcript=1"
            ).fetchone()
            db_stats["videos_with_transcript"] = r[0] if r else 0
            r2 = conn.execute(
                "SELECT COUNT(*) as n FROM youtube_video_persons"
            ).fetchone()
            db_stats["total_persons"] = r2[0] if r2 else 0
            r3 = conn.execute(
                "SELECT COUNT(*) as n FROM youtube_video_claims"
            ).fetchone()
            db_stats["total_claims"] = r3[0] if r3 else 0
            conn.close()
        except Exception as e:
            db_stats["error"] = str(e)
    else:
        db_stats["error"] = "OSINT DB not found"

    return {
        "status": "ok",
        "semantic_index": idx_stats,
        "osint_db": db_stats,
        "ytp_root": str(_YTP_ROOT),
        "ytp_available": _YTP_ROOT.exists(),
    }


@router.post("/index/build", response_model=IndexBuildResponse)
async def build_index(
    background_tasks: BackgroundTasks,
    limit: int = Query(5000, ge=10, le=50000),
):
    """
    Rebuild semantic index from OSINT-MW database.
    Runs in background — check /status for completion.
    """
    def _do_build():
        global _index_built
        try:
            idx = _get_index()
            n = idx.build_from_db(limit=limit)
            _index_built = True
            return n
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Index build failed: {e}")

    background_tasks.add_task(_do_build)
    return IndexBuildResponse(
        status="building",
        videos_indexed=0,
        message=(
            f"Building index from OSINT-MW DB (limit={limit}). "
            "Check /api/yt/status for completion."
        ),
    )


@router.get("/video/{video_id}")
async def get_video_intelligence(video_id: str):
    """Get full intelligence report for a specific video from OSINT-MW."""
    if not _OSINT_DB.exists():
        raise HTTPException(status_code=503, detail="OSINT DB not accessible")

    conn = sqlite3.connect(str(_OSINT_DB))
    conn.row_factory = sqlite3.Row

    video = conn.execute(
        "SELECT * FROM youtube_videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")

    video_dict = dict(video)

    # Persons
    persons = conn.execute(
        "SELECT * FROM youtube_video_persons WHERE video_id = ? LIMIT 100",
        (video_id,),
    ).fetchall()
    video_dict["persons"] = [dict(p) for p in persons]

    # Claims
    claims = conn.execute(
        "SELECT * FROM youtube_video_claims WHERE video_id = ? LIMIT 50",
        (video_id,),
    ).fetchall()
    video_dict["claims"] = [dict(c) for c in claims]

    # Intelligence
    intel = conn.execute(
        "SELECT * FROM youtube_video_intelligence WHERE video_id = ?",
        (video_id,),
    ).fetchone()
    if intel:
        import json
        intel_dict = dict(intel)
        for key in ("intelligence_report", "topic_accordion", "tier1_forensics",
                    "communication_profile", "geopolitics", "social_graph"):
            if intel_dict.get(key):
                try:
                    intel_dict[key] = json.loads(intel_dict[key])
                except Exception:
                    pass
        video_dict["intelligence"] = intel_dict

    conn.close()
    video_dict["url"] = f"https://www.youtube.com/watch?v={video_id}"
    return video_dict


@router.get("/videos")
async def list_videos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    channel: Optional[str] = None,
):
    """List videos in OSINT-MW with pagination."""
    if not _OSINT_DB.exists():
        raise HTTPException(status_code=503, detail="OSINT DB not accessible")

    conn = sqlite3.connect(str(_OSINT_DB))
    conn.row_factory = sqlite3.Row

    q = """SELECT video_id, channel_name, title, published_at,
                  duration_seconds, view_count, has_transcript, scraped_at
           FROM youtube_videos"""
    params: list = []
    if channel:
        q += " WHERE channel_name LIKE ?"
        params.append(f"%{channel}%")
    q += " ORDER BY scraped_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(q, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM youtube_videos").fetchone()[0]
    conn.close()

    return {
        "videos": [dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
