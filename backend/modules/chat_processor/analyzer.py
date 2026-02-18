"""Conversation Analysis Layer - OpenRouter LLM intelligence extraction."""
import json
import os
import logging
from typing import Optional

import requests

from .models import ConversationIntelligence, ParsedConversation


_SYSTEM_PROMPT = """Eres un analista experto en extraer inteligencia de conversaciones AI.
Analiza la conversacion y devuelve SOLO JSON con este formato exacto:
{
  "summary": "resumen en 2-3 oraciones",
  "main_topics": ["tema1", "tema2"],
  "technologies_mentioned": ["Python", "FastAPI"],
  "decisions_made": ["decision1"],
  "code_artifacts": [{"language": "python", "description": "desc", "snippet": "..."}],
  "knowledge_extracted": ["insight1"],
  "osint_relevance": "por que es relevante",
  "content_type": "TECHNICAL|RESEARCH|PLANNING|CREATIVE|ANALYSIS|GENERIC"
}"""


def analyze_conversation(
    conversation: ParsedConversation,
    api_key: Optional[str] = None,
    model: str = "google/gemini-2.5-flash",
) -> Optional[ConversationIntelligence]:
    """Analyze a parsed conversation and return structured intelligence."""
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return None

    lines = []
    for msg in conversation.messages[:60]:
        role_label = "USUARIO" if msg.role == "user" else "ASISTENTE"
        lines.append(f"{role_label}: {msg.content[:800]}")
    conv_text = chr(10).join(lines)

    if len(conv_text) < 50:
        return None

    title = conversation.title or "Sin titulo"
    prompt = (
        f"PLATAFORMA: {conversation.platform}" + chr(10)
        + f"TITULO: {title}" + chr(10)
        + f"MENSAJES: {len(conversation.messages)}" + chr(10) + chr(10)
        + "CONVERSACION:" + chr(10) + conv_text[:12000]
    )

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data["choices"][0]["message"]["content"]
        result = json.loads(raw)
        return ConversationIntelligence(
            conversation_id=conversation.conversation_id,
            platform=conversation.platform,
            main_topics=result.get("main_topics", []),
            technologies_mentioned=result.get("technologies_mentioned", []),
            decisions_made=result.get("decisions_made", []),
            code_artifacts=result.get("code_artifacts", []),
            knowledge_extracted=result.get("knowledge_extracted", []),
            osint_relevance=result.get("osint_relevance", ""),
            summary=result.get("summary", ""),
        )
    except Exception as exc:
        logging.getLogger(__name__).warning("Conversation analysis failed: %s", exc)
        return None
