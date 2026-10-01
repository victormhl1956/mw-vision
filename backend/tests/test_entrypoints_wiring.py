"""
Los tres puntos de entrada, no sólo el que yo miré.

Qué se me escapó. El 2026-10-01 cablé la autenticación del WebSocket en
`routers/websocket.py` y la política de confianza de Hydra en el `lifespan` de
`main.py`. Pero este backend tiene **tres** puntos de entrada:

  · main.py            — lo arranca RUN-MW-VISION.bat (uvicorn main:app)
  · main_modular.py    — lo arranca PM2, que es lo que sobrevive a un reinicio
  · src/main.py        — no lo arranca nada, y tiene su propio /ws

De modo que la compuerta de confianza quedó en el entry point que PM2 **no**
usa: en producción no se aplicaba. Y `src/main.py` conserva un `/ws` que acepta
cualquier conexión, igual que el agujero que supuestamente cerré.

Es la misma clase de defecto que vengo persiguiendo, cometida por mí: el
arreglo existe, en un camino que la ejecución real no toma.

El último test de este archivo es el que generaliza: recorre el árbol, busca
cada endpoint WebSocket declarado y exige que su módulo autentique. Si mañana
aparece un cuarto `/ws`, falla sin que nadie se acuerde de este archivo.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

os.environ.setdefault("HYDRA_SECRET_KEY", "clave-de-prueba-estable-para-los-tests")


def _rechazado(cliente, url: str) -> bool:
    """True si el servidor cierra en vez de atender."""
    from starlette.websockets import WebSocketDisconnect
    try:
        with cliente.websocket_connect(url) as ws:
            ws.receive_json()
        return False
    except WebSocketDisconnect:
        return True
    except Exception:
        return True


# ── La compuerta de confianza en el entry point de producción ────────────────

def test_la_compuerta_de_confianza_corre_en_el_arranque_modular(monkeypatch):
    """
    PM2 arranca main_modular.py, que construye la app con core.app.create_app.
    Si la compuerta sólo vive en el lifespan de main.py, producción no la aplica.
    """
    import core.app as capp
    from fastapi.testclient import TestClient

    llamadas = []
    import modules.agents.trust_gate as tg
    monkeypatch.setattr(tg, "exigir_agentes_confiables",
                        lambda agentes: llamadas.append(agentes))
    with TestClient(capp.create_app()):
        pass
    assert llamadas, "create_app() no aplica la política de confianza"


def test_el_arranque_modular_completo_funciona():
    """main_modular tal cual, sin parches: arranca y responde."""
    from fastapi.testclient import TestClient
    import main_modular
    with TestClient(main_modular.app) as cliente:
        assert cliente.get("/health").status_code == 200


# ── El /ws de cada entry point ──────────────────────────────────────────────

def test_el_websocket_modular_rechaza_sin_token():
    from fastapi.testclient import TestClient
    import main_modular
    with TestClient(main_modular.app) as cliente:
        assert _rechazado(cliente, "/ws"), "main_modular sirve /ws sin token"


def test_el_websocket_de_main_rechaza_sin_token():
    """
    main.py define su propio /ws y no incluye routers/websocket.py, así que la
    corrección del 2026-10-01 nunca llegó aquí — y RUN-MW-VISION.bat arranca
    precisamente `uvicorn main:app`. El test de árbol de abajo lo encontró; este
    comprueba el comportamiento, no la presencia de una cadena de texto.
    """
    from fastapi.testclient import TestClient
    import main
    with TestClient(main.app) as cliente:
        assert _rechazado(cliente, "/ws"), "main.py sirve /ws sin token"


def test_el_websocket_de_main_acepta_un_token_valido():
    from fastapi.testclient import TestClient
    import main
    from src.security.websocket_auth import get_authenticator

    token = get_authenticator().generate_token(expires_hours=1)
    with TestClient(main.app) as cliente:
        with cliente.websocket_connect(f"/ws?token={token}") as ws:
            assert ws.receive_json()


def test_el_websocket_de_src_main_rechaza_sin_token():
    from fastapi.testclient import TestClient
    import src.main as sm
    with TestClient(sm.app) as cliente:
        assert _rechazado(cliente, "/ws"), "src/main.py sirve /ws sin token"


def test_el_websocket_de_src_main_acepta_un_token_valido():
    """
    El contrapeso. Sin esto, una compuerta que rechaza todo pasaría el test
    anterior y rompería la aplicación.
    """
    from fastapi.testclient import TestClient
    import src.main as sm
    from src.security.websocket_auth import get_authenticator

    token = get_authenticator().generate_token(expires_hours=1)
    with TestClient(sm.app) as cliente:
        with cliente.websocket_connect(f"/ws?token={token}") as ws:
            assert ws.receive_json()


# ── El que generaliza ───────────────────────────────────────────────────────

_DECL_WS = re.compile(r"@\s*\w+\s*\.\s*websocket\s*\(")
_OMITIR = {"venv", ".venv", "__pycache__", "node_modules", "tests"}


def _modulos_con_websocket() -> list[str]:
    hallados = []
    for raiz, subdirs, archivos in os.walk(BACKEND):
        subdirs[:] = [d for d in subdirs if d not in _OMITIR]
        for nombre in archivos:
            if not nombre.endswith(".py"):
                continue
            ruta = os.path.join(raiz, nombre)
            with open(ruta, encoding="utf-8", errors="replace") as fh:
                texto = fh.read()
            if _DECL_WS.search(texto):
                hallados.append(ruta)
    return hallados


def test_todo_endpoint_websocket_del_arbol_autentica():
    """
    La red que habría cazado mi propio olvido. No comprueba la implementación:
    comprueba que el módulo que declara un `/ws` llama al verificador. Un
    endpoint nuevo sin autenticación falla aquí sin que nadie recuerde este
    archivo.
    """
    modulos = _modulos_con_websocket()
    assert modulos, "no encontré ningún endpoint WebSocket: el test se quedó ciego"

    sin_autenticar = [
        os.path.relpath(m, BACKEND) for m in modulos
        if "verify_token" not in open(m, encoding="utf-8", errors="replace").read()
    ]
    assert not sin_autenticar, (
        f"endpoints WebSocket que no verifican el token: {sin_autenticar}")
