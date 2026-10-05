"""
El procesador de conversaciones: el registro de plataformas y su cableado.

Por qué existe. `modules/chat_processor/__init__.py` y `router.py` importan
`PLATFORM_REGISTRY`, `detect_platform` y `parse_conversation` de `platforms.py`,
y **ninguno de los tres existe en ese archivo**: termina en el quinto parser.
`main.py` envuelve el import en `except Exception` e imprime una línea, así que
el router nunca se registró y el subsistema completo lleva apagado desde que se
escribió. `/` lo reportaba como `chat_processor: false` sin decir por qué, y
`/health` seguía devolviendo `"healthy"` con un subsistema entero caído.

Tres defectos en uno: símbolos que faltan (el import), una degradación que se
traga la causa (D-08) y un estado escrito como literal en vez de medido (D-02).

Regla que impone este archivo: un subsistema opcional puede degradarse, pero no
en silencio, y nada que diga "healthy" puede ignorar lo que está caído.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

os.environ.setdefault("HYDRA_SECRET_KEY", "clave-de-prueba-estable-para-los-tests")


# ── El registro existe y tiene la forma que el router lee ────────────────────

def test_los_tres_simbolos_que_el_router_importa_existen():
    """El import que fallaba. Si esto falla, el router no se puede registrar."""
    from modules.chat_processor.platforms import (
        PLATFORM_REGISTRY, detect_platform, parse_conversation)
    assert PLATFORM_REGISTRY and callable(detect_platform)
    assert callable(parse_conversation)


def test_el_paquete_exporta_lo_que_promete_su_docstring():
    """`from modules.chat_processor import ...` tiene que funcionar."""
    import modules.chat_processor as cp
    for nombre in cp.__all__:
        assert hasattr(cp, nombre), f"__all__ promete {nombre} y no está"


def test_estan_las_cinco_plataformas_documentadas():
    from modules.chat_processor.platforms import PLATFORM_REGISTRY
    assert set(PLATFORM_REGISTRY) == {
        "chatgpt", "claude", "gemini", "perplexity", "deepseek"}


def test_cada_entrada_tiene_los_campos_que_el_router_lee():
    """
    El router lee `display_name`, `icon` y `export_instructions`. El dataclass
    declaraba `import_instructions` y no tenía `icon`: aunque el registro
    hubiera existido, `/api/chat/platforms` habría reventado con AttributeError.
    Este test fija la correspondencia entre el dataclass y sus lectores.
    """
    from modules.chat_processor.platforms import PLATFORM_REGISTRY
    for nombre, cfg in PLATFORM_REGISTRY.items():
        for campo in ("display_name", "icon", "export_instructions", "parse_fn"):
            assert hasattr(cfg, campo), f"{nombre} no tiene {campo}"
        assert callable(cfg.parse_fn)
        assert cfg.export_instructions.strip(), f"{nombre} sin instrucciones"


# ── Detección ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("url,esperada", [
    ("https://chatgpt.com/c/abc123", "chatgpt"),
    ("https://chat.openai.com/c/abc", "chatgpt"),
    ("https://claude.ai/chat/xyz", "claude"),
    ("https://gemini.google.com/app/1", "gemini"),
    ("https://www.perplexity.ai/search/algo", "perplexity"),
    ("https://chat.deepseek.com/a/chat/s/1", "deepseek"),
])
def test_detecta_la_plataforma_por_url(url, esperada):
    from modules.chat_processor.platforms import detect_platform
    nombre, confianza = detect_platform(url=url)
    assert nombre == esperada
    assert confianza > 0.5


def test_detecta_la_plataforma_por_contenido():
    """Sin URL, por las huellas del formato de exportación."""
    from modules.chat_processor.platforms import detect_platform
    nombre, confianza = detect_platform(
        content_sample=json.dumps({"mapping": {}, "create_time": 1,
                                   "current_node": "x"}))
    assert nombre == "chatgpt"
    assert confianza > 0.0

    nombre, _ = detect_platform(content_sample=json.dumps({
        "uuid": "a-b-c", "name": "algo",
        "chat_messages": [{"uuid": "m1", "sender": "human", "text": "hola"}]}))
    assert nombre == "claude"

    # Y una huella suelta no basta: "create_time" aparece en cualquier JSON.
    assert detect_platform(content_sample='{"create_time": 1}') == (None, 0.0)


def test_no_inventa_una_plataforma_cuando_no_la_reconoce():
    """
    El contrapeso. Un detector que siempre responde algo es inútil: haría pasar
    cualquier archivo por el parser equivocado y el resultado parecería un
    fallo del contenido.
    """
    from modules.chat_processor.platforms import detect_platform
    assert detect_platform(url="https://example.com/x") == (None, 0.0)
    assert detect_platform(content_sample="hola, qué tal") == (None, 0.0)
    assert detect_platform() == (None, 0.0)


# ── Despacho ─────────────────────────────────────────────────────────────────

def test_usa_el_parser_de_la_plataforma_declarada():
    from modules.chat_processor.platforms import parse_conversation
    conv = parse_conversation(
        content=json.dumps({"chat_messages": [
            {"role": "user", "content": "pregunta"},
            {"role": "assistant", "content": "respuesta"}]}),
        platform="claude")
    assert conv.platform == "claude"
    assert [m.role for m in conv.messages] == ["user", "assistant"]


def test_la_exportacion_real_de_claude_conserva_quien_habla():
    """
    El formato REAL de una exportación de Claude: `sender` y `text`, con el
    texto repetido en bloques de `content`, y sin campo `role`.

    La prueba de arriba usa `role`/`content`, un formato que Claude no
    exporta, y por eso pasaba mientras cada mensaje real se guardaba como
    «unknown». Encontrado guardando una exportación desde la pestaña Memoria
    en un navegador, el 2026-10-04.
    """
    from modules.chat_processor.platforms import parse_conversation
    conv = parse_conversation(content=json.dumps({
        "uuid": "11111111-2222-3333-4444-555555555555",
        "name": "Conversación real",
        "chat_messages": [
            {"uuid": "a1", "sender": "human", "text": "pregunta",
             "content": [{"type": "text", "text": "pregunta"}]},
            {"uuid": "a2", "sender": "assistant", "text": "respuesta",
             "content": [{"type": "text", "text": "respuesta"}]},
            # Exportaciones antiguas: sólo `text`, sin bloques.
            {"uuid": "a3", "sender": "human", "text": "seguimiento"},
        ]}))
    assert conv.platform == "claude"
    assert [m.role for m in conv.messages] == ["user", "assistant", "user"]
    assert [m.content for m in conv.messages] == [
        "pregunta", "respuesta", "seguimiento"]


def test_detecta_sola_cuando_no_se_declara_la_plataforma():
    from modules.chat_processor.platforms import parse_conversation
    conv = parse_conversation(content=json.dumps({
        "mapping": {"1": {"message": {"id": "1", "create_time": 1.0,
                                      "author": {"role": "user"},
                                      "content": {"parts": ["hola"]}}}},
        "create_time": 1.0, "title": "T"}))
    assert conv.platform == "chatgpt"
    assert conv.messages and conv.messages[0].content == "hola"


def test_una_plataforma_desconocida_no_se_traga_en_silencio():
    """
    Devolver una conversación vacía haría que un nombre mal escrito pareciera
    un archivo sin mensajes. Son dos problemas distintos y el mensaje tiene
    que distinguirlos.
    """
    from modules.chat_processor.platforms import parse_conversation
    with pytest.raises(ValueError) as e:
        parse_conversation(content="{}", platform="chatgpr")
    assert "chatgpr" in str(e.value)


def test_un_transcript_sin_plataforma_reconocible_se_intenta_igual():
    """
    Un markdown de origen desconocido es un caso real. Se parsea con el lector
    genérico y se marca `unknown`: no se finge que viene de ninguna parte.
    """
    from modules.chat_processor.platforms import parse_conversation
    conv = parse_conversation(content=(
        "## User:\nla pregunta\n\n## Assistant:\nla respuesta\n"))
    assert conv.platform == "unknown"
    assert len(conv.messages) == 2


# ── El cableado: el router vive dentro de la app ─────────────────────────────

def test_el_router_del_chat_processor_queda_registrado(tmp_path, monkeypatch):
    """
    El test que importa. Falla si el import vuelve a romperse, porque
    `except Exception` seguiría tragándoselo y sólo esto lo notaría.
    """
    monkeypatch.chdir(tmp_path)
    from fastapi.testclient import TestClient
    import main
    with TestClient(main.app) as cliente:
        r = cliente.get("/api/chat/platforms")
        assert r.status_code == 200, f"el router no está registrado: {r.status_code}"
        nombres = {p["name"] for p in r.json()["platforms"]}
        assert nombres == {"chatgpt", "claude", "gemini", "perplexity", "deepseek"}


def test_ingesta_de_punta_a_punta_por_la_api(tmp_path, monkeypatch):
    """Una exportación con forma de ChatGPT entra, se parsea y se guarda."""
    monkeypatch.chdir(tmp_path)
    from fastapi.testclient import TestClient
    import main
    carga = {"content": {
        "title": "Conversación de prueba", "create_time": 1700000000.0,
        "mapping": {
            "a": {"message": {"id": "a", "create_time": 1700000000.0,
                              "author": {"role": "user"},
                              "content": {"parts": ["¿cuántos nodos hay?"]}}},
            "b": {"message": {"id": "b", "create_time": 1700000001.0,
                              "author": {"role": "assistant"},
                              "content": {"parts": ["ciento noventa y dos"]}}},
        }}, "analyze": False}
    with TestClient(main.app) as cliente:
        r = cliente.post("/api/chat/ingest", json=carga)
        assert r.status_code == 200, r.text
        cuerpo = r.json()
        assert cuerpo["platform"] == "chatgpt"
        assert cuerpo["message_count"] == 2


# ── D-08 y D-02: la degradación deja de ser silenciosa y "healthy" de mentir ─

def test_la_raiz_dice_por_que_falta_un_subsistema(tmp_path, monkeypatch):
    """
    `chat_processor: false` sin causa obligaba a leer la salida estándar del
    proceso para saber qué pasó. La causa va en la respuesta.
    """
    monkeypatch.chdir(tmp_path)
    from fastapi.testclient import TestClient
    import main
    with TestClient(main.app) as cliente:
        # Con todo cargado: ningún error que reportar.
        eco = cliente.get("/").json()["ecosystem"]
        assert eco["chat_processor"] is True
        assert eco["errors"] == {}

        # Simulamos la caída: el booleano y la causa son hechos distintos y
        # tienen que viajar los dos.
        monkeypatch.setattr(main, "_chat_router", None)
        monkeypatch.setitem(main._ecosystem_errors, "chat_processor",
                            "ImportError: cannot import name 'PLATFORM_REGISTRY'")
        eco = cliente.get("/").json()["ecosystem"]
        assert eco["chat_processor"] is False
        assert "PLATFORM_REGISTRY" in eco["errors"]["chat_processor"]


def test_health_no_dice_healthy_con_un_subsistema_caido(tmp_path, monkeypatch):
    """
    D-02 en su forma más pura: `"status": "healthy"` era un literal, no una
    medición. Un subsistema entero podía estar caído y la respuesta no cambiaba.
    """
    monkeypatch.chdir(tmp_path)
    from fastapi.testclient import TestClient
    import main
    with TestClient(main.app) as cliente:
        assert cliente.get("/health").json()["status"] == "healthy"
        monkeypatch.setitem(main._ecosystem_errors, "chat_processor", "fallo")
        cuerpo = cliente.get("/health").json()
        assert cuerpo["status"] == "degraded"
        assert "chat_processor" in cuerpo["degraded_subsystems"]
