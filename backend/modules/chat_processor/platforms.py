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
    """
    Una plataforma soportada.

    Los nombres de los campos los fija quien los lee: `router.py` usa
    `display_name`, `icon` y `export_instructions`. El dataclass declaraba
    `import_instructions` y no tenía `icon`, así que aunque PLATFORM_REGISTRY
    hubiese existido, `/api/chat/platforms` habría reventado con AttributeError.
    `export_instructions` es además el nombre correcto: describen cómo exportar
    desde la plataforma de origen, no cómo importar aquí.
    """
    name: str
    display_name: str
    icon: str
    url_patterns: List[str]
    content_fingerprints: List[str]
    export_formats: List[str]
    export_instructions: str
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


_ROL_DE_SENDER = {"human": "user", "user": "user", "assistant": "assistant"}


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
            # Las exportaciones reales de Claude no traen `role`: traen
            # `sender` ("human" / "assistant") y el texto en `text` y en
            # bloques de `content`. Leer sólo `role` guardaba TODOS los
            # mensajes como "unknown": la memoria perdía quién dijo qué, y
            # nada fallaba, porque la prueba usaba un formato inventado.
            role = msg.get("role") or _ROL_DE_SENDER.get(
                str(msg.get("sender", "")).lower(), "unknown")
            raw_content = msg.get("content", "")
            if isinstance(raw_content, list):
                text = " ".join(
                    block.get("text", "") for block in raw_content
                    if isinstance(block, dict) and block.get("type") == "text"
                ).strip()
            else:
                text = str(raw_content).strip()
            if not text:
                text = str(msg.get("text", "")).strip()
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
    # Cadenas crudas: en una cadena normal, \s y \* son secuencias de escape
    # invalidas. Python las deja pasar hoy con un DeprecationWarning y las
    # convertira en error, asi que estos tres patrones dejarian de compilar en
    # una version futura y el analisis generico de markdown moriria con el
    # interprete, no con un cambio de codigo.
    patterns = [
        r"(?:^|\n)##\s*(User|Human|You|Assistant|AI|Claude|Gemini|GPT|DeepSeek|Perplexity):\s*\n(.*?)(?=\n##\s|\Z)",
        r"(?:^|\n)\*\*(User|Human|You|Assistant|AI|Claude|Gemini|GPT|DeepSeek):\*\*\s*\n(.*?)(?=\n\*\*|\Z)",
        r"(?:^|\n)(Human|User|Assistant|AI):\s*\n(.*?)(?=\n(?:Human|User|Assistant|AI):|\Z)",
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


# ─────────────────────────────────────────────────────────────────────────────
# El registro
#
# `platforms.py` terminaba en el quinto parser: PLATFORM_REGISTRY,
# detect_platform y parse_conversation nunca se escribieron, aunque
# `__init__.py` y `router.py` los importaban. `main.py` envolvía el import en
# `except Exception` e imprimía una línea, así que el subsistema completo quedó
# apagado en silencio desde el principio.
#
# Las rutas de menú de las instrucciones son de interfaces ajenas y cambian sin
# avisar: si alguien reporta que no encuentra la opción, esto es lo primero que
# hay que revisar, no el parser.
# ─────────────────────────────────────────────────────────────────────────────

PLATFORM_REGISTRY: Dict[str, PlatformConfig] = {
    "chatgpt": PlatformConfig(
        name="chatgpt",
        display_name="ChatGPT",
        icon="💬",
        url_patterns=[r"chatgpt\.com", r"chat\.openai\.com"],
        # Huellas del formato de exportación de OpenAI: el grafo de mensajes.
        content_fingerprints=["mapping", "current_node", "create_time"],
        export_formats=["json"],
        export_instructions=(
            "Ajustes → Controles de datos → Exportar datos. Llega un correo "
            "con un .zip; dentro, conversations.json. Sube ese archivo."),
        parse_fn=_parse_chatgpt,
    ),
    "claude": PlatformConfig(
        name="claude",
        display_name="Claude",
        icon="🅰️",
        url_patterns=[r"claude\.ai"],
        content_fingerprints=["chat_messages", "uuid", "sender"],
        export_formats=["json", "md"],
        export_instructions=(
            "Ajustes → Privacidad → Exportar datos. Llega un correo con "
            "conversations.json. También acepta un markdown pegado."),
        parse_fn=_parse_claude,
    ),
    "gemini": PlatformConfig(
        name="gemini",
        display_name="Gemini",
        icon="♊",
        url_patterns=[r"gemini\.google\.com", r"bard\.google\.com"],
        content_fingerprints=["history", "author", "candidates"],
        export_formats=["json", "md"],
        export_instructions=(
            "Google Takeout (takeout.google.com) → selecciona Gemini. "
            "También acepta un markdown pegado de la conversación."),
        parse_fn=_parse_gemini,
    ),
    "perplexity": PlatformConfig(
        name="perplexity",
        display_name="Perplexity",
        icon="🔍",
        url_patterns=[r"perplexity\.ai"],
        content_fingerprints=["query_str", "related_queries", "web_results"],
        export_formats=["md", "json"],
        export_instructions=(
            "Perplexity no exporta en bloque: usa Compartir → Copiar y pega "
            "el markdown de cada hilo."),
        parse_fn=_parse_perplexity,
    ),
    "deepseek": PlatformConfig(
        name="deepseek",
        display_name="DeepSeek",
        icon="🐋",
        url_patterns=[r"deepseek\.com"],
        content_fingerprints=["conversation", "model_class", "deepseek"],
        export_formats=["json", "md"],
        export_instructions=(
            "DeepSeek no tiene exportación propia: copia la conversación y "
            "pégala como markdown.  Ojo: jurisdicción extranjera, no subas "
            "aquí conversaciones con datos sensibles."),
        parse_fn=_parse_deepseek,
    ),
}

# Confianza de una coincidencia por URL. El dominio es inequívoco; las huellas
# de contenido no, así que puntúan más bajo y en proporción a cuántas aparecen.
_CONFIANZA_URL = 0.95
_CONFIANZA_HUELLA_MAX = 0.85
# Una sola huella suelta no basta: "create_time" o "author" aparecen en
# cualquier JSON. Hacen falta dos para que la respuesta valga algo.
_HUELLAS_MINIMAS = 2


def detect_platform(
    url: Optional[str] = None, content_sample: Optional[str] = None
) -> Tuple[Optional[str], float]:
    """
    Adivina de qué plataforma viene algo, por su URL o por su formato.

    Devuelve (nombre, confianza), o (None, 0.0) cuando no lo sabe — y eso es
    tan importante como acertar: un detector que siempre responde algo haría
    pasar cualquier archivo por el parser equivocado, y el resultado parecería
    un problema del contenido.
    """
    if url:
        for nombre, cfg in PLATFORM_REGISTRY.items():
            for patron in cfg.url_patterns:
                if re.search(patron, url, re.IGNORECASE):
                    return nombre, _CONFIANZA_URL

    if content_sample:
        muestra = content_sample[:20000].lower()
        mejor_nombre: Optional[str] = None
        mejor_aciertos = 0
        for nombre, cfg in PLATFORM_REGISTRY.items():
            aciertos = sum(
                1 for huella in cfg.content_fingerprints
                if huella.lower() in muestra)
            if aciertos > mejor_aciertos:
                mejor_nombre, mejor_aciertos = nombre, aciertos
        if mejor_nombre and mejor_aciertos >= _HUELLAS_MINIMAS:
            cfg = PLATFORM_REGISTRY[mejor_nombre]
            proporcion = mejor_aciertos / len(cfg.content_fingerprints)
            return mejor_nombre, round(_CONFIANZA_HUELLA_MAX * proporcion, 2)

    return None, 0.0


def parse_conversation(
    content: Any,
    platform: Optional[str] = None,
    source_url: Optional[str] = None,
) -> ParsedConversation:
    """
    Parsea una conversación con el lector de su plataforma.

    `platform` declarado manda. Si no se declara, se detecta por la URL y por
    el contenido. Si no se reconoce nada, se intenta el lector genérico de
    markdown y la conversación queda marcada `unknown`: un transcript de origen
    desconocido es un caso real y no hay por qué fingir que viene de algún sitio.

    Lanza ValueError si se declara una plataforma que no existe. Devolver una
    conversación vacía haría que un nombre mal escrito pareciera un archivo sin
    mensajes, y son dos problemas distintos.
    """
    if platform:
        cfg = PLATFORM_REGISTRY.get(platform.lower())
        if cfg is None:
            disponibles = ", ".join(sorted(PLATFORM_REGISTRY))
            raise ValueError(
                f"plataforma desconocida: {platform!r}. Disponibles: {disponibles}")
        return cfg.parse_fn(content, source_url)

    muestra = content if isinstance(content, str) else json.dumps(
        content, ensure_ascii=False, default=str)
    detectada, _ = detect_platform(url=source_url, content_sample=muestra)
    if detectada:
        return PLATFORM_REGISTRY[detectada].parse_fn(content, source_url)

    return _parse_markdown_generic(muestra, "unknown", source_url)
