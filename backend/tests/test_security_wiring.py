"""
El cableado de los arreglos de febrero, no su implementación.

La auditoría del 2026-02-17 declaró cinco vulnerabilidades corregidas en tres
archivos: `websocket_auth.py` (VULN-001, 002), `audit_logger.py` (VULN-003,
009) y `trust_manager.py` (VULN-007, 010). Las tres correcciones eran buenas.
Ninguno de los tres módulos era alcanzable desde ningún punto de entrada: nada
los importaba, así que nada de eso se ejecutaba. Los tests de aquella auditoría
pasaban porque importaban los módulos directamente — probaban un mundo en el
que el arreglo estaba cableado.

`websocket_auth.py` se cableó el 2026-10-01 y su test vive en
`test_websocket_auth_wiring.py`. Este archivo cubre los otros dos.

Regla que impone: ninguna corrección de seguridad está hecha si no hay un test
que falle cuando el arreglo se desconecta.
"""

from __future__ import annotations

import json
import os
import sys
import threading

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

os.environ.setdefault("HYDRA_SECRET_KEY", "clave-de-prueba-estable-para-los-tests")


# ── Utilidades ───────────────────────────────────────────────────────────────

def leer_eventos(directorio) -> list[dict]:
    """Todos los eventos escritos en el directorio de auditoría."""
    eventos = []
    for nombre in sorted(os.listdir(directorio)):
        if not nombre.endswith(".jsonl"):
            continue
        with open(os.path.join(directorio, nombre), encoding="utf-8") as fh:
            for linea in fh:
                if linea.strip():
                    eventos.append(json.loads(linea))
    return eventos


@pytest.fixture
def auditor(tmp_path, monkeypatch):
    """Un AuditLogger aislado, puesto como el singleton del módulo."""
    from src.security import audit_logger as mod
    destino = tmp_path / "auditoria"
    logger = mod.AuditLogger(log_dir=str(destino))
    monkeypatch.setattr(mod, "_audit_logger", logger)
    return logger, destino


# ── VULN-003 / VULN-009: el registro de auditoría ────────────────────────────

def test_el_rechazo_del_websocket_queda_registrado(auditor, monkeypatch):
    """
    Una conexión rechazada tiene que dejar rastro. Sin esto, el agujero que
    cerramos ayer se puede volver a abrir y nadie lo sabría: la métrica en
    memoria muere con el proceso.
    """
    _, destino = auditor
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect
    import routers.websocket as rw

    app = FastAPI()
    app.include_router(rw.router)
    with TestClient(app) as cliente:
        with pytest.raises(WebSocketDisconnect):
            with cliente.websocket_connect("/ws") as ws:
                ws.receive_json()

    eventos = [e for e in leer_eventos(destino) if e["event_type"] == "websocket_auth"]
    assert eventos, "el rechazo no dejó ningún evento de auditoría"
    assert eventos[-1]["result"] == "denied"
    assert eventos[-1]["resource"] == "/ws"


def test_la_conexion_valida_queda_registrada(auditor, monkeypatch):
    """
    El contrapeso: si sólo registrásemos los rechazos, un registro vacío sería
    indistinguible de un servidor que no se usa.
    """
    _, destino = auditor
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import routers.websocket as rw
    from src.security.websocket_auth import get_authenticator

    token = get_authenticator().generate_token(expires_hours=1)
    app = FastAPI()
    app.include_router(rw.router)
    with TestClient(app) as cliente:
        with cliente.websocket_connect(f"/ws?token={token}") as ws:
            ws.receive_json()

    eventos = [e for e in leer_eventos(destino) if e["event_type"] == "websocket_auth"]
    assert eventos, "la conexión aceptada no dejó ningún evento"
    assert eventos[-1]["result"] == "success"


def test_escritores_concurrentes_no_corrompen_el_registro(auditor):
    """
    VULN-003 en el camino real. El cerrojo sólo sirve si se ejecuta: con 40
    hilos escribiendo, cada línea tiene que seguir siendo JSON completo.
    """
    logger, destino = auditor
    hilos = [
        threading.Thread(target=logger.log_event, args=(
            "carga", f"hilo-{i}", "escribir", "registro", "success"))
        for i in range(40)
    ]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    eventos = leer_eventos(destino)
    assert len(eventos) == 40, f"se perdieron o se mezclaron líneas: {len(eventos)} de 40"
    assert len({e["actor"] for e in eventos}) == 40


def test_la_sanitizacion_quita_los_caracteres_de_control(auditor):
    """
    VULN-009 declara que los metadatos se sanean para evitar inyección en el
    registro. El test lo comprueba sobre el valor guardado, no sobre la
    intención: un consumidor que lea el campo no debe recibir saltos de línea
    ni NUL.
    """
    logger, destino = auditor
    logger.log_event(
        "prueba", "atacante", "inyectar", "registro", "denied",
        metadata={"nota": "primera\nsegunda\r\x00tercera"},
    )
    evento = leer_eventos(destino)[-1]
    valor = evento["metadata"]["nota"]
    assert "\n" not in valor and "\r" not in valor and "\x00" not in valor, \
        f"los caracteres de control sobrevivieron: {valor!r}"
    assert "primera" in valor and "tercera" in valor, "se perdió contenido"


# ── VULN-007 / VULN-010: la política de confianza de los modelos ─────────────

def test_la_compuerta_de_confianza_es_alcanzable_desde_el_arranque():
    """
    El cableado en sí. Si este import falla, la política no está conectada a
    nada y volvemos al estado de febrero.
    """
    from modules.agents.trust_gate import verificar_agentes
    assert callable(verificar_agentes)


def test_los_agentes_configurados_hoy_pasan_la_politica():
    """
    La configuración viva tiene que ser válida. Si falla, es la configuración
    la que hay que decidir, no el test el que hay que relajar.
    """
    from modules.agents.state import agents
    from modules.agents.trust_gate import verificar_agentes
    assert verificar_agentes(agents) == []


def test_un_agente_declarado_sensible_no_puede_usar_un_modelo_de_nube():
    """
    VULN-007: la eficiencia de costo no puede cruzar el límite de seguridad.
    Declarar un agente SENSITIVE y darle deepseek es contradictorio, y la
    contradicción tiene que detenerse en el arranque, no en producción.
    """
    from modules.agents.models import AgentModel
    from modules.agents.trust_gate import verificar_agentes
    violaciones = verificar_agentes({
        "x": AgentModel(id="x", name="Revisor OSINT",
                        model="deepseek-chat", sensitivity="SENSITIVE"),
    })
    assert len(violaciones) == 1
    assert "deepseek-chat" in violaciones[0]


def test_un_modelo_desconocido_es_una_violacion():
    """Un modelo que la política no conoce no puede aprobarse por omisión."""
    from modules.agents.models import AgentModel
    from modules.agents.trust_gate import verificar_agentes
    violaciones = verificar_agentes({
        "x": AgentModel(id="x", name="Typo", model="gtp-4o"),
    })
    assert len(violaciones) == 1


def test_la_denegacion_por_modelo_desconocido_se_registra(auditor):
    """
    VULN-010: devolver False en silencio era el defecto. El TrustManager acepta
    un auditor opcional y por omisión era None, así que el arreglo tampoco
    disparaba. La compuerta tiene que pasarle el auditor real.
    """
    _, destino = auditor
    from modules.agents.models import AgentModel
    from modules.agents.trust_gate import verificar_agentes
    verificar_agentes({"x": AgentModel(id="x", name="Typo", model="gtp-4o")})

    alertas = [e for e in leer_eventos(destino) if e["event_type"] == "SECURITY_ALERT"]
    assert alertas, "la denegación por modelo desconocido no dejó rastro"
    assert alertas[-1]["result"] == "DENIED_UNKNOWN_MODEL"


def test_el_arranque_de_la_app_ejecuta_la_compuerta(monkeypatch):
    """
    El test que importa: que la compuerta esté en el camino de arranque de la
    app viva, no solamente que exista. Falla si alguien quita la llamada.
    """
    import modules.agents.trust_gate as tg
    llamadas = []
    monkeypatch.setattr(tg, "verificar_agentes",
                        lambda agentes: llamadas.append(agentes) or [])

    from fastapi.testclient import TestClient
    import main
    monkeypatch.setattr(main, "verificar_agentes", tg.verificar_agentes,
                        raising=False)
    with TestClient(main.app):
        pass
    assert llamadas, "el arranque no llamó a la compuerta de confianza"


def test_los_eventos_perdidos_son_visibles_en_la_api(tmp_path, monkeypatch):
    """
    El contrapeso del manejador estrecho de OSError en la ruta de escritura.
    No propagar la excepción es correcto — esta clase instrumenta el handshake
    del WebSocket y un disco lleno no debe tumbar el servicio — pero sólo si el
    fallo se puede ver desde fuera. Si no, es un `except: pass` con buenos
    modales.
    """
    from fastapi.testclient import TestClient
    from src.security import audit_logger as mod
    import main

    logger = mod.AuditLogger(log_dir=str(tmp_path / "auditoria"))
    monkeypatch.setattr(mod, "_audit_logger", logger)
    antes = mod.AuditLogger.write_failures

    # Un directorio que no se puede crear: el nombre lo ocupa un archivo.
    bloqueado = tmp_path / "bloqueado"
    bloqueado.write_text("no soy un directorio")
    monkeypatch.setattr(logger, "log_dir", bloqueado / "dentro")
    logger.log_event("prueba", "x", "escribir", "registro", "success")

    assert mod.AuditLogger.write_failures == antes + 1, \
        "el fallo de escritura no se contó"
    with TestClient(main.app) as cliente:
        cuerpo = cliente.get("/api/security").json()
        assert cuerpo["audit_trail"]["write_failures"] >= 1
        assert cuerpo["audit_trail"]["directory"]
