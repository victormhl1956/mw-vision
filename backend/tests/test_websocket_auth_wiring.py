"""
El cableado de la autenticación del WebSocket, no su implementación.

Por qué existe este archivo: VULN-001 se corrigió el 2026-02-17 dentro de
`src/security/websocket_auth.py`, y la corrección es buena — HMAC-SHA256 con
comparación en tiempo constante y control de expiración. Pero nada importaba ese
módulo, así que el endpoint `/ws` seguía aceptando cualquier conexión. El arreglo
existía y estaba desconectado.

Una auditoría que lee el archivo del arreglo concluye "parcheado". Estos tests
leen el camino de ejecución, que es donde vivía el agujero.

Regla que impone este archivo: ninguna corrección de seguridad se considera
hecha si no hay un test que falle cuando el arreglo se desconecta.
"""

from __future__ import annotations

import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

# Una clave fija para los tests: así `generate_token` y el endpoint comparten
# secreto, en vez de depender de la clave efímera por proceso.
os.environ.setdefault("HYDRA_SECRET_KEY", "clave-solo-para-tests-" + "0" * 24)


@pytest.fixture()
def client() -> TestClient:
    from routers.websocket import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture()
def token() -> str:
    from src.security.websocket_auth import get_authenticator

    return get_authenticator().generate_token(expires_hours=1)


def _rechazado(client: TestClient, url: str) -> bool:
    """True si el servidor cierra la conexión en vez de servirla."""
    try:
        with client.websocket_connect(url) as ws:
            ws.receive_json()  # un servidor que autentica no llega a enviar nada
        return False
    except WebSocketDisconnect:
        return True
    except Exception:
        # Cualquier otro cierre también es un rechazo; lo que falla el test es
        # que la conexión se sirva con normalidad.
        return True


def test_sin_token_se_rechaza(client: TestClient):
    """El agujero real: `/ws` aceptaba conexiones sin ninguna credencial."""
    assert _rechazado(client, "/ws"), (
        "El endpoint /ws sirvió una conexión SIN token. "
        "verify_token existe en src/security/websocket_auth.py pero no está "
        "cableado al endpoint."
    )


def test_token_invalido_se_rechaza(client: TestClient):
    assert _rechazado(client, "/ws?token=no-es-un-token"), (
        "El endpoint /ws aceptó un token con formato inválido."
    )


def test_firma_manipulada_se_rechaza(client: TestClient, token: str):
    """Cambiar la firma debe invalidar el token: eso prueba que se verifica."""
    payload, firma = token.rsplit(".", 1)
    alterada = ("a" if firma[0] != "a" else "b") + firma[1:]
    assert _rechazado(client, f"/ws?token={payload}.{alterada}"), (
        "El endpoint /ws aceptó un token cuya firma HMAC no corresponde."
    )


def test_token_expirado_se_rechaza(client: TestClient):
    from src.security.websocket_auth import get_authenticator

    caducado = get_authenticator().generate_token(expires_hours=-1)
    assert _rechazado(client, f"/ws?token={caducado}"), (
        "El endpoint /ws aceptó un token ya expirado."
    )


def test_token_valido_se_acepta(client: TestClient, token: str):
    """El contrapeso: la compuerta debe dejar pasar lo legítimo.

    Sin este test, cerrar siempre la conexión pasaría los cuatro anteriores —
    una compuerta que rechaza todo es tan inútil como una que acepta todo.
    """
    with client.websocket_connect(f"/ws?token={token}") as ws:
        inicial = ws.receive_json()
    assert inicial["type"] == "init", (
        "Un token válido no obtuvo el estado inicial: la compuerta rechaza "
        "incluso lo legítimo."
    )


def test_secreto_ausente_falla_al_arrancar(monkeypatch):
    """HYDRA_SECRET_KEY ausente debe fallar, no degradarse en silencio.

    El constructor emitía un `warnings.warn` y generaba una clave efímera por
    proceso. Con varios workers de PM2, los tokens firmados por uno los rechaza
    otro: autenticación que funciona a medias, y los fallos se achacan a la red.
    """
    import importlib

    import src.security.websocket_auth as wa

    monkeypatch.delenv("HYDRA_SECRET_KEY", raising=False)
    monkeypatch.delenv("WS_SECRET_KEY", raising=False)
    importlib.reload(wa)
    with pytest.raises(RuntimeError, match="HYDRA_SECRET_KEY"):
        wa.WebSocketAuthenticator()


def test_revoke_token_no_finge_exito():
    """Una revocación que no revoca no puede devolver éxito en silencio.

    `revoke_token` tenía un cuerpo `pass` con un TODO: devolvía None — forma de
    éxito — sin revocar nada. Quien lo cablee creyendo que hay revocación la
    tiene de adorno.
    """
    from src.security.websocket_auth import get_authenticator

    auth = get_authenticator()
    with pytest.raises(NotImplementedError):
        auth.revoke_token(auth.generate_token(expires_hours=1))
