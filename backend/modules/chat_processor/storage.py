"""SQLite storage for parsed conversations and intelligence."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import ConversationIntelligence, ParsedConversation

_DEFAULT_DB = Path(__file__).parent.parent.parent / "chat_processor.db"


def _get_conn(db_path: Path = _DEFAULT_DB) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: Path = _DEFAULT_DB) -> None:
    """Create tables if they do not exist."""
    conn = _get_conn(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_conversations (
            conversation_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            title TEXT,
            source_url TEXT,
            message_count INTEGER DEFAULT 0,
            created_at TEXT,
            ingested_at TEXT NOT NULL,
            messages_json TEXT NOT NULL,
            warnings_json TEXT,
            security_findings_json TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_intelligence (
            conversation_id TEXT PRIMARY KEY,
            platform TEXT,
            summary TEXT,
            main_topics_json TEXT,
            technologies_json TEXT,
            decisions_json TEXT,
            code_artifacts_json TEXT,
            knowledge_json TEXT,
            osint_relevance TEXT,
            analyzed_at TEXT NOT NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cc_platform ON chat_conversations(platform)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cc_ingested ON chat_conversations(ingested_at)"
    )
    conn.commit()
    conn.close()


def save_conversation(
    conversation: ParsedConversation, db_path: Path = _DEFAULT_DB
) -> str:
    """Persist a ParsedConversation. Returns conversation_id."""
    conn = _get_conn(db_path)
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT OR REPLACE INTO chat_conversations
           (conversation_id, platform, title, source_url, message_count,
            created_at, ingested_at, messages_json, warnings_json,
            security_findings_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            conversation.conversation_id,
            conversation.platform,
            conversation.title,
            conversation.source_url,
            len(conversation.messages),
            conversation.created_at.isoformat() if conversation.created_at else None,
            now,
            json.dumps([m.to_dict() for m in conversation.messages], ensure_ascii=False),
            json.dumps(conversation.warnings, ensure_ascii=False),
            json.dumps(conversation.security_findings, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()
    return conversation.conversation_id


def save_intelligence(
    intel: ConversationIntelligence, db_path: Path = _DEFAULT_DB
) -> None:
    """Persist intelligence analysis results."""
    conn = _get_conn(db_path)
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT OR REPLACE INTO chat_intelligence
           (conversation_id, platform, summary, main_topics_json,
            technologies_json, decisions_json, code_artifacts_json,
            knowledge_json, osint_relevance, analyzed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            intel.conversation_id,
            intel.platform,
            intel.summary,
            json.dumps(intel.main_topics, ensure_ascii=False),
            json.dumps(intel.technologies_mentioned, ensure_ascii=False),
            json.dumps(intel.decisions_made, ensure_ascii=False),
            json.dumps(intel.code_artifacts, ensure_ascii=False),
            json.dumps(intel.knowledge_extracted, ensure_ascii=False),
            intel.osint_relevance,
            now,
        ),
    )
    conn.commit()
    conn.close()


def list_conversations(
    limit: int = 50,
    platform: Optional[str] = None,
    db_path: Path = _DEFAULT_DB,
) -> List[Dict]:
    """List stored conversations (metadata only, no messages)."""
    conn = _get_conn(db_path)
    q = (
        "SELECT conversation_id, platform, title, source_url, "
        "message_count, created_at, ingested_at "
        "FROM chat_conversations"
    )
    params: list = []
    if platform:
        q += " WHERE platform = ?"
        params.append(platform)
    q += " ORDER BY ingested_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversation(
    conversation_id: str, db_path: Path = _DEFAULT_DB
) -> Optional[Dict]:
    """Get full conversation including messages."""
    conn = _get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM chat_conversations WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    intel_row = conn.execute(
        "SELECT * FROM chat_intelligence WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    result["messages"] = json.loads(result.pop("messages_json", "[]"))
    result["warnings"] = json.loads(result.pop("warnings_json", "[]"))
    result["security_findings"] = json.loads(
        result.pop("security_findings_json", "[]")
    )
    if intel_row:
        intel = dict(intel_row)
        intel["main_topics"] = json.loads(intel.pop("main_topics_json", "[]"))
        intel["technologies"] = json.loads(intel.pop("technologies_json", "[]"))
        intel["decisions"] = json.loads(intel.pop("decisions_json", "[]"))
        intel["code_artifacts"] = json.loads(intel.pop("code_artifacts_json", "[]"))
        intel["knowledge"] = json.loads(intel.pop("knowledge_json", "[]"))
        result["intelligence"] = intel
    return result


def search_conversations(
    query: str, limit: int = 20, db_path: Path = _DEFAULT_DB
) -> List[Dict]:
    """Full-text search over conversation messages (SQLite LIKE)."""
    conn = _get_conn(db_path)
    rows = conn.execute(
        """SELECT conversation_id, platform, title, message_count, ingested_at
           FROM chat_conversations
           WHERE messages_json LIKE ?
           ORDER BY ingested_at DESC LIMIT ?""",
        (f"%{query}%", limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
