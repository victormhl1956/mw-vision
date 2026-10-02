# -*- coding: utf-8 -*-
"""
Un panel de seguridad que no puede fallar es peor que no tener panel.

El panel escrito a mano traía ocho comprobaciones, todas en 'pass', incluida
«Authentication», y siguió diciéndolo durante los ocho meses en que el endpoint
de WebSocket no autenticaba. Así que lo que se fija aquí no es que las
comprobaciones pasen: es que puedan FALLAR, y que lo que no se puede medir salga
como no_se en vez de como un visto bueno.
"""
import os

import pytest
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from modules.security.evidencia import (FALLA, NO_SE, PASA, SIN_EVIDENCIA,
                                        comprobar_autenticacion,
                                        comprobar_cabeceras, comprobar_cors,
                                        comprobar_limite_peticiones,
                                        evidencia_de_seguridad)

CLAVE_BUENA = "0123456789abcdef0123456789abcdef"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)


def _app(con_limite=True, con_cabeceras=True, cors=None):
    app = FastAPI()
    if con_limite:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    if con_cabeceras:
        app.add_middleware(SecurityHeadersMiddleware)
    if cors is not None:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(CORSMiddleware, allow_origins=cors)
    return app


# ── cada comprobación tiene que poder fallar ────────────────────────────────

def test_el_limite_de_peticiones_falla_si_no_esta():
    assert comprobar_limite_peticiones(_app(con_limite=True))["status"] == PASA
    fallo = comprobar_limite_peticiones(_app(con_limite=False))
    assert fallo["status"] == FALLA
    assert "no está registrado" in fallo["evidence"]


def test_el_limite_dice_cual_es():
    """Una evidencia que no da el número no se puede discutir."""
    c = comprobar_limite_peticiones(_app(con_limite=True))
    assert "100" in c["evidence"], c["evidence"]


def test_las_cabeceras_fallan_si_no_estan():
    assert comprobar_cabeceras(_app(con_cabeceras=True))["status"] == PASA
    assert comprobar_cabeceras(_app(con_cabeceras=False))["status"] == FALLA


def test_cors_abierto_a_todo_es_un_fallo_no_un_visto_bueno():
    """
    `allow_origins=["*"]` es la configuración que el panel escrito a mano
    habría mostrado como «Cross-origin restrictions configured».
    """
    c = comprobar_cors(_app(cors=["*"]))
    assert c["status"] == FALLA, c
    assert "*" in c["evidence"]


def test_cors_restringido_pasa_y_nombra_los_origenes():
    c = comprobar_cors(_app(cors=["http://localhost:5189"]))
    assert c["status"] == PASA
    assert "localhost:5189" in c["evidence"]


def test_sin_cors_registrado_es_no_se_no_un_fallo():
    """
    Sin CORSMiddleware el navegador aplica su propia política, que desde aquí no
    se ve. Eso es no_se: ni aprobar ni condenar lo que no se mide.
    """
    assert comprobar_cors(_app(cors=None))["status"] == NO_SE


# ── la que importaba: autenticación ─────────────────────────────────────────

def test_la_autenticacion_falla_sin_clave(monkeypatch):
    """La comprobación que el panel daba por pasada mientras no existía."""
    monkeypatch.delenv("HYDRA_SECRET_KEY", raising=False)
    monkeypatch.delenv("WS_SECRET_KEY", raising=False)
    monkeypatch.delenv("HYDRA_ALLOW_WEAK_KEY", raising=False)
    c = comprobar_autenticacion()
    assert c["status"] == FALLA, c


def test_la_autenticacion_falla_con_clave_debil(monkeypatch):
    monkeypatch.setenv("HYDRA_SECRET_KEY", "changeme")
    monkeypatch.delenv("HYDRA_ALLOW_WEAK_KEY", raising=False)
    assert comprobar_autenticacion()["status"] == FALLA


def test_la_autenticacion_falla_si_se_fuerza_una_clave_debil(monkeypatch):
    """
    La salida de emergencia hace que el autenticador arranque, así que sin esto
    la comprobación diría «pasa» con una clave de juguete: la peor combinación
    posible, porque el panel se pondría verde justamente cuando alguien se ha
    saltado la guarda.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", "changeme")
    monkeypatch.setenv("HYDRA_ALLOW_WEAK_KEY", "1")
    c = comprobar_autenticacion()
    assert c["status"] == FALLA, c
    assert "HYDRA_ALLOW_WEAK_KEY" in c["evidence"]


def test_la_autenticacion_pasa_con_una_clave_de_verdad(monkeypatch):
    """El contrapeso: una comprobación que siempre falla tampoco sirve."""
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    monkeypatch.delenv("HYDRA_ALLOW_WEAK_KEY", raising=False)
    assert comprobar_autenticacion()["status"] == PASA


# ── lo que no se puede medir sale no_se ─────────────────────────────────────

@pytest.mark.parametrize("nombre", sorted(SIN_EVIDENCIA))
def test_lo_que_no_se_puede_medir_no_aprueba(nombre, monkeypatch):
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    d = evidencia_de_seguridad(_app(cors=["http://localhost:5189"]))
    c = next(x for x in d["checks"] if x["name"] == nombre)
    assert c["status"] == NO_SE, c
    assert len(c["evidence"]) > 30, (
        f"{nombre} sale no_se sin explicar por qué; un «no lo sé» sin motivo "
        f"es indistinguible de un olvido")


def test_sin_aplicacion_las_comprobaciones_de_middleware_no_aprueban():
    """Una comprobación sin sujeto no puede aprobar por omisión."""
    d = evidencia_de_seguridad(None)
    for nombre in ("Rate Limiting", "Security Headers", "CORS Policy"):
        c = next(x for x in d["checks"] if x["name"] == nombre)
        assert c["status"] == NO_SE, c


# ── el estado global ────────────────────────────────────────────────────────

def test_un_fallo_manda_sobre_todo_lo_demas(monkeypatch):
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    d = evidencia_de_seguridad(_app(con_limite=False,
                                    cors=["http://localhost:5189"]))
    assert d["status"] == "critical", d["counts"]


def test_todo_medido_y_bien_no_es_secure_si_queda_algo_sin_medir(monkeypatch):
    """
    Con cuatro comprobaciones sin evidencia, el estado global no puede ser
    «secure»: no haber medido no es estar bien. El panel resolvía esto poniendo
    un 92.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    d = evidencia_de_seguridad(_app(cors=["http://localhost:5189"]))
    assert d["status"] == "partial", d
    assert d["counts"]["no_se"] >= len(SIN_EVIDENCIA)


def test_no_hay_puntuacion(monkeypatch):
    """
    A propósito. Una cifra única invita a promediar lo medido con lo no medido,
    y así es como «no lo sé» se convierte en «va bien»: el panel traía un 92
    fijo con cero comprobaciones reales.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    d = evidencia_de_seguridad(_app(cors=["http://localhost:5189"]))
    assert d["score"] is None
    assert "promediar" in d["score_explanation"]


def test_ninguna_comprobacion_se_queda_sin_evidencia(monkeypatch):
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    d = evidencia_de_seguridad(_app(cors=["http://localhost:5189"]))
    assert d["checks"], "no devolvió ninguna comprobación"
    for c in d["checks"]:
        assert c["evidence"].strip(), f"{c['name']} no dice en qué se basa"
        assert c["status"] in (PASA, FALLA, NO_SE), c


# ── y que llegue de verdad por HTTP, en los dos puntos de entrada ───────────

def test_la_evidencia_sale_por_api_security_en_el_entry_point_de_pm2(monkeypatch):
    """
    Un arreglo que no está en el camino de ejecución no es un arreglo. Esto
    monta la aplicación como la monta PM2 y pide la ruta de verdad.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    monkeypatch.delenv("HYDRA_ALLOW_WEAK_KEY", raising=False)
    from fastapi.testclient import TestClient

    # main_modular es lo que arranca PM2: create_app() construye la aplicación
    # y los routers los añade ESE fichero, así que probar create_app() a secas
    # da 404 en todas las rutas. Comprobarlo contra la aplicación equivocada es
    # cómo un arreglo pasa por cableado sin estarlo.
    import main_modular
    cliente = TestClient(main_modular.app)
    r = cliente.get("/api/security")
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    assert "evidence" in cuerpo, (
        "la evidencia no llega por HTTP: el módulo existe y nadie lo llama, "
        "que es el defecto de febrero otra vez")
    ev = cuerpo["evidence"]
    assert ev["checks"], ev
    # Las tres que dependen del middleware tienen que estar medidas de verdad
    # aquí: si salen no_se, es que no se pasó la aplicación.
    for nombre in ("Rate Limiting", "Security Headers"):
        c = next(x for x in ev["checks"] if x["name"] == nombre)
        assert c["status"] == PASA, (
            f"{nombre} salió {c['status']} en la aplicación real: "
            f"{c['evidence']}")
    aut = next(x for x in ev["checks"] if x["name"] == "Authentication")
    assert aut["status"] == PASA, aut
    assert ev["score"] is None


def test_lo_que_ya_devolvia_sigue_estando(monkeypatch):
    """No romper al añadir: el panel actual lee estas tres claves."""
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE_BUENA)
    from fastapi.testclient import TestClient

    import main_modular
    cuerpo = TestClient(main_modular.app).get("/api/security").json()
    for clave in ("security_metrics", "active_connections",
                  "per_ip_connections"):
        assert clave in cuerpo, f"desapareció {clave} de /api/security"
