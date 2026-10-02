# -*- coding: utf-8 -*-
"""
What the application can actually prove about its own security, and what it
cannot.

Why this exists. The security panel in the interface held eight checks written by
hand, every one of them 'pass', including "Authentication: JWT token validation
active". While the WebSocket authentication sat unwired — February to 1 October —
that panel reported it passing. A security dashboard that cannot fail is worse
than no dashboard: it converts the absence of measurement into the appearance of
safety, and it is the most direct explanation of how a report could declare
"Security 100%".

So every check here reports one of three states and the evidence behind it:

  pasa    the application inspected itself and found the protection in place
  falla   it inspected itself and the protection is absent or unsafe
  no_se   there is no evidence available from inside the process

`no_se` is the important one. HTTPS termination is decided by whatever serves the
app, not by the app; input validation is spread across every handler and cannot
be asserted from one place. Saying so is the honest answer, and it is what lets a
panel show "unknown" instead of inventing a green tick.

Nothing here reaches outside the process: the evidence is the app's own
middleware stack, its own configuration and its own counters.
"""

from __future__ import annotations

import os
from typing import Any

PASA, FALLA, NO_SE = "pasa", "falla", "no_se"


def _middleware_presente(app, nombre: str):
    """
    The middleware entry whose class is named `nombre`, or None.

    Starlette keeps what was registered in `user_middleware`, so this is the
    app's own account of itself rather than a guess from the source.
    """
    for entrada in getattr(app, "user_middleware", []):
        cls = getattr(entrada, "cls", None)
        if cls is not None and getattr(cls, "__name__", "") == nombre:
            return entrada
    return None


def _opciones(entrada) -> dict:
    """The keyword arguments a middleware was registered with."""
    if entrada is None:
        return {}
    opciones = getattr(entrada, "kwargs", None)
    if isinstance(opciones, dict):
        return opciones
    # Starlette's older Middleware kept them in `options`.
    opciones = getattr(entrada, "options", None)
    return opciones if isinstance(opciones, dict) else {}


def _comprobacion(nombre: str, estado: str, evidencia: str) -> dict:
    return {"name": nombre, "status": estado, "evidence": evidencia}


def comprobar_limite_peticiones(app) -> dict:
    entrada = _middleware_presente(app, "RateLimitMiddleware")
    if entrada is None:
        return _comprobacion(
            "Rate Limiting", FALLA,
            "RateLimitMiddleware no está registrado en esta aplicación")
    por_minuto = _opciones(entrada).get("requests_per_minute")
    if por_minuto is None:
        return _comprobacion(
            "Rate Limiting", PASA,
            "RateLimitMiddleware registrado; no pude leer su límite")
    return _comprobacion("Rate Limiting", PASA,
                         f"RateLimitMiddleware registrado, "
                         f"{por_minuto} peticiones por minuto")


def comprobar_cabeceras(app) -> dict:
    entrada = _middleware_presente(app, "SecurityHeadersMiddleware")
    if entrada is None:
        return _comprobacion(
            "Security Headers", FALLA,
            "SecurityHeadersMiddleware no está registrado en esta aplicación")
    return _comprobacion("Security Headers", PASA,
                         "SecurityHeadersMiddleware registrado")


def comprobar_cors(app) -> dict:
    entrada = _middleware_presente(app, "CORSMiddleware")
    if entrada is None:
        return _comprobacion(
            "CORS Policy", NO_SE,
            "CORSMiddleware no está registrado: el navegador aplicará su "
            "política por defecto y desde aquí no se puede saber cuál")
    origenes = _opciones(entrada).get("allow_origins")
    if origenes is None:
        return _comprobacion("CORS Policy", NO_SE,
                             "CORSMiddleware registrado; no pude leer "
                             "allow_origins")
    if "*" in list(origenes):
        return _comprobacion(
            "CORS Policy", FALLA,
            "allow_origins incluye «*»: cualquier origen puede llamar a esta "
            "API desde un navegador")
    return _comprobacion("CORS Policy", PASA,
                         f"allow_origins restringido a "
                         f"{', '.join(list(origenes)[:4])}")


def comprobar_autenticacion() -> dict:
    """
    Can the WebSocket authenticator actually start?

    This is the check the hand-written panel claimed as passing while the
    endpoint was unauthenticated. It is answerable now: the authenticator
    refuses to be constructed without a strong signing key, so building one is
    itself the evidence.
    """
    try:
        from src.security.websocket_auth import WebSocketAuthenticator
    except ImportError as e:
        return _comprobacion(
            "Authentication", NO_SE,
            f"no pude importar el autenticador de WebSocket: {e}")
    try:
        WebSocketAuthenticator()
    except RuntimeError as e:
        return _comprobacion(
            "Authentication", FALLA,
            f"el autenticador no puede arrancar: {e}".replace("\n", " ")[:300])
    except Exception as e:  # noqa: BLE001 - cualquier fallo aquí es un falla
        return _comprobacion(
            "Authentication", FALLA,
            f"el autenticador falló al construirse: {type(e).__name__}")
    if os.getenv("HYDRA_ALLOW_WEAK_KEY") == "1":
        return _comprobacion(
            "Authentication", FALLA,
            "HYDRA_ALLOW_WEAK_KEY=1: se está aceptando una clave de firma "
            "débil a propósito, lo que nunca debe ocurrir en producción")
    return _comprobacion(
        "Authentication", PASA,
        "el autenticador de WebSocket arranca con una clave de firma que pasa "
        "las comprobaciones de fuerza")


def comprobar_registro_auditoria() -> dict:
    try:
        from src.security.audit_logger import AuditLogger, get_audit_logger
    except ImportError as e:
        return _comprobacion("Audit Trail", NO_SE,
                             f"no pude importar el registro de auditoría: {e}")
    fallos = getattr(AuditLogger, "write_failures", None)
    try:
        directorio = str(get_audit_logger().log_dir)
    except Exception as e:  # noqa: BLE001
        return _comprobacion(
            "Audit Trail", FALLA,
            f"el registro de auditoría no se pudo abrir: {type(e).__name__}")
    if fallos is None:
        return _comprobacion("Audit Trail", NO_SE,
                             f"escribiendo en {directorio}; el contador de "
                             f"fallos no está disponible")
    if fallos:
        return _comprobacion(
            "Audit Trail", FALLA,
            f"{fallos} evento(s) de auditoría no se pudieron escribir en "
            f"{directorio}: hay huecos en el rastro")
    return _comprobacion("Audit Trail", PASA,
                         f"escribiendo en {directorio}, sin fallos de "
                         f"escritura")


# Comprobaciones que el panel escrito a mano daba por pasadas y que desde dentro
# del proceso NO se pueden afirmar. Decirlo es la respuesta honrada; inventar un
# visto bueno es lo que hacía el panel.
SIN_EVIDENCIA = {
    "HTTPS/TLS": "lo termina lo que sirva la aplicación (un proxy, el túnel de "
                 "desarrollo), no la aplicación: desde aquí no se puede saber "
                 "si la conexión del navegador iba cifrada",
    "Input Validation": "la validación vive en cada manejador por separado; no "
                        "hay un sitio desde el que se pueda afirmar que todos "
                        "la hacen",
    "XSS Protection": "depende de las cabeceras que llegan al navegador y de "
                      "cómo pinta el frontend; la aplicación no lo observa",
    "Database Security": "no hay una comprobación que recorra las consultas; "
                         "lo que sí está medido es que los sensores abren las "
                         "bases en sólo-lectura, que es otra cosa",
}


def evidencia_de_seguridad(app=None) -> dict[str, Any]:
    """
    Las comprobaciones con su estado y su evidencia, más el recuento.

    `app` es la aplicación FastAPI cuyo propio registro de middleware se
    inspecciona. Sin ella, las tres comprobaciones que dependen del middleware
    salen no_se en vez de salir pasa por omisión: una comprobación sin sujeto no
    puede aprobar.
    """
    comprobaciones: list[dict] = []
    if app is not None:
        comprobaciones += [comprobar_limite_peticiones(app),
                           comprobar_cabeceras(app),
                           comprobar_cors(app)]
    else:
        for nombre in ("Rate Limiting", "Security Headers", "CORS Policy"):
            comprobaciones.append(_comprobacion(
                nombre, NO_SE,
                "no se pasó la aplicación, así que no pude mirar su "
                "middleware"))
    comprobaciones.append(comprobar_autenticacion())
    comprobaciones.append(comprobar_registro_auditoria())
    for nombre, porque in SIN_EVIDENCIA.items():
        comprobaciones.append(_comprobacion(nombre, NO_SE, porque))

    pasan = sum(1 for c in comprobaciones if c["status"] == PASA)
    fallan = sum(1 for c in comprobaciones if c["status"] == FALLA)
    sin_saber = sum(1 for c in comprobaciones if c["status"] == NO_SE)

    # El estado global no se promedia: un falla manda. Y «todo lo demás es
    # no_se» nunca es «seguro», porque no haber medido no es estar bien.
    if fallan:
        estado = "critical"
    elif pasan == 0:
        estado = "unknown"
    elif sin_saber:
        estado = "partial"
    else:
        estado = "secure"

    return {
        "status": estado,
        "checks": comprobaciones,
        "counts": {"pasa": pasan, "falla": fallan, "no_se": sin_saber},
        # Deliberadamente NO hay puntuación. El panel traía un 92 fijo, y una
        # cifra única invita a promediar lo medido con lo no medido, que es
        # como «no lo sé» se convierte en «va bien».
        "score": None,
        "score_explanation": (
            "no hay puntuación a propósito: promediar comprobaciones medidas "
            "con comprobaciones sin evidencia convierte «no lo sé» en «va "
            "bien»"),
    }
