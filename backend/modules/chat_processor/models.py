"""Data models for Chat Processor."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class SecurityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ParsedMessage:
    role: str  # user, assistant, system, tool
    content: str
    timestamp: Optional[datetime] = None
    message_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.timestamp:
            d["timestamp"] = self.timestamp.isoformat()
        return d


@dataclass
class ParsedConversation:
    messages: List[ParsedMessage]
    platform: str
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    source_url: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    security_findings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "conversation_id": self.conversation_id,
            "platform": self.platform,
            "title": self.title,
            "source_url": self.source_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "messages": [m.to_dict() for m in self.messages],
            "warnings": self.warnings,
            "security_findings": self.security_findings,
            "message_count": len(self.messages),
        }


@dataclass
class ConversationIntelligence:
    conversation_id: str
    main_topics: List[str]
    technologies_mentioned: List[str]
    decisions_made: List[str]
    code_artifacts: List[Dict[str, str]]
    knowledge_extracted: List[str]
    osint_relevance: str
    summary: str
    platform: str

    def to_dict(self) -> dict:
        return asdict(self)
