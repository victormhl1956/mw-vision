"""FastAPI router for Chat Processor endpoints."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from .platforms import PLATFORM_REGISTRY, detect_platform, parse_conversation
from .security import scan_messages
from .analyzer import analyze_conversation
from .storage import (
    init_db,
    save_conversation,
    save_intelligence,
    list_conversations,
    get_conversation,
    search_conversations,
)

router = APIRouter(prefix="/api/chat", tags=["chat_processor"])

_DB_PATH = Path(__file__).parent.parent.parent / "chat_processor.db"
init_db(_DB_PATH)


class IngestRequest(BaseModel):
    content: Any
    platform: Optional[str] = None
    source_url: Optional[str] = None
    analyze: bool = True


class DetectRequest(BaseModel):
    url: Optional[str] = None
    content_sample: Optional[str] = None


@router.post("/ingest")
async def ingest_conversation(req: IngestRequest) -> Dict:
    """Ingest a conversation from any supported platform."""
    try:
        # Normalize content to string (may arrive as dict from JSON body)
        raw_content = req.content
        if isinstance(raw_content, (dict, list)):
            import json as _json
            content_str = _json.dumps(raw_content, ensure_ascii=False)
        else:
            content_str = str(raw_content)
        conversation = parse_conversation(
            content=content_str,
            platform=req.platform,
            source_url=req.source_url,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Parse failed: {e}")

    if not conversation.messages:
        raise HTTPException(
            status_code=422,
            detail="No messages extracted. Check format or platform.",
        )

    findings = scan_messages(conversation.messages)
    conversation.security_findings = [f.to_dict() for f in findings]

    if findings:
        conversation.warnings.append(
            f"{len(findings)} security finding(s) detected"
        )

    cid = save_conversation(conversation, _DB_PATH)

    intelligence = None
    if req.analyze:
        intel = analyze_conversation(conversation)
        if intel:
            save_intelligence(intel, _DB_PATH)
            intelligence = intel.to_dict()

    return {
        "status": "ok",
        "conversation_id": cid,
        "platform": conversation.platform,
        "message_count": len(conversation.messages),
        "security_findings": len(findings),
        "warnings": conversation.warnings,
        "intelligence": intelligence,
    }


@router.post("/detect-platform")
async def detect_platform_endpoint(req: DetectRequest) -> Dict:
    """Detect platform from URL and/or content sample for dynamic menu."""
    platform_name, confidence = detect_platform(
        url=req.url, content_sample=req.content_sample
    )
    if platform_name and platform_name in PLATFORM_REGISTRY:
        cfg = PLATFORM_REGISTRY[platform_name]
        return {
            "detected": True,
            "platform": platform_name,
            "display_name": cfg.display_name,
            "confidence": round(confidence, 2),
            "instructions": cfg.export_instructions,
        }
    return {
        "detected": False,
        "platform": None,
        "confidence": 0.0,
        "available_platforms": [
            {
                "name": k,
                "display_name": v.display_name,
                "instructions": v.export_instructions,
            }
            for k, v in PLATFORM_REGISTRY.items()
        ],
    }


@router.get("/platforms")
async def list_platforms() -> Dict:
    """List all supported platforms and their import instructions."""
    return {
        "platforms": [
            {
                "name": k,
                "display_name": v.display_name,
                "icon": v.icon,
                "instructions": v.export_instructions,
            }
            for k, v in PLATFORM_REGISTRY.items()
        ]
    }


@router.get("/conversations")
async def list_convs(
    platform: Optional[str] = None, limit: int = 50
) -> Dict:
    """List stored conversations (metadata only)."""
    convs = list_conversations(limit=limit, platform=platform, db_path=_DB_PATH)
    return {"conversations": convs, "total": len(convs)}


@router.get("/conversations/{conversation_id}")
async def get_conv(conversation_id: str) -> Dict:
    """Get full conversation including messages and intelligence."""
    conv = get_conversation(conversation_id, _DB_PATH)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("/search")
async def search_convs(q: str, limit: int = 20) -> Dict:
    """Search conversations by content."""
    results = search_conversations(q, limit=limit, db_path=_DB_PATH)
    return {"query": q, "results": results, "count": len(results)}


@router.post("/ingest/upload")
async def ingest_upload(
    file: UploadFile = File(...),
    platform: Optional[str] = Form(None),
    analyze: bool = Form(True),
) -> Dict:
    """Upload a conversation file (JSON, MD, TXT)."""
    raw = await file.read()
    try:
        content_str = raw.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    try:
        content: Any = json.loads(content_str)
    except json.JSONDecodeError:
        content = content_str

    req = IngestRequest(
        content=content,
        platform=platform,
        source_url=f"upload://{file.filename}",
        analyze=analyze,
    )
    return await ingest_conversation(req)
