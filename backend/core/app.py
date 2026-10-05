"""
FastAPI Application Factory
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict

from modules.security import RateLimitMiddleware, SecurityHeadersMiddleware
from modules.crew import (aviso_simulacion, simulacion_activa,
                          simulate_agent_updates)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background simulation task."""
    # La política de confianza de Hydra, aquí y no sólo en main.py. PM2 arranca
    # main_modular.py, que construye la app con create_app(): tener la compuerta
    # únicamente en el lifespan de main.py la dejaba fuera del entry point que
    # de verdad corre en producción. Mismo defecto que vengo arreglando — el
    # arreglo en un camino que la ejecución no toma — cometido al arreglarlo.
    # tests/test_entrypoints_wiring.py falla si se quita.
    from modules.agents.state import agents
    from modules.agents.trust_gate import exigir_agentes_confiables
    exigir_agentes_confiables(agents)

    # El simulador NO arranca por defecto. Generaba el coste con
    # random.randint() y lo escribía en crew_state.total_cost, que se compara
    # contra budget_limit para parar la tripulación: un dado moviendo una
    # guarda de presupuesto, en los dos puntos de entrada, en producción.
    # Apagado, los contadores quedan a cero, que es la verdad. MW_SIMULADOR=on
    # lo devuelve para una demo, y entonces /api/crew lo dice.
    print(aviso_simulacion())
    task = (asyncio.create_task(simulate_agent_updates())
            if simulacion_activa() else None)
    yield
    if task is not None:
        task.cancel()


# Los routers del ecosistema se cargan con guarda: si uno no importa, la
# aplicación arranca sin él y el MOTIVO queda visible en /api y en /health, en
# vez de desaparecer en una línea de consola que nadie lee.
ERRORES_ECOSISTEMA: Dict[str, str] = {}


def _router_opcional(punteado: str, etiqueta: str):
    """El router, o None con el motivo anotado."""
    try:
        modulo = __import__(punteado, fromlist=["router"])
        return getattr(modulo, "router")
    except Exception as e:  # noqa: BLE001 — cualquier fallo deja la causa
        ERRORES_ECOSISTEMA[etiqueta] = f"{type(e).__name__}: {e}"
        print(f"[MW-Vision] {etiqueta} no cargado: {e}")
        return None


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="MW-Vision Backend",
        description="Secure WebSocket backend for MW-Vision Visual Command Center",
        version="3.0.0",
        lifespan=lifespan
    )

    # Add security middleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    app.add_middleware(SecurityHeadersMiddleware)

    # Restricted CORS (only localhost for development)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5189", "http://127.0.0.1:5189"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # El ecosistema. Esto faltaba, y el agujero era el de febrero otra vez:
    # main.py registraba el procesador de conversaciones y el de YouTube, y
    # main_modular.py —que es lo que arranca PM2— no. Así que /api/chat/* y
    # /api/yt/* daban 404 en producción mientras el código existía, pasaba sus
    # tests y la interfaz los pedía. Lo encontré arrancando la aplicación de
    # verdad, no leyendo: tests/test_entrypoint_sirve_lo_pedido.py lo fija.
    for punteado, etiqueta, prefijo in (
            ("routers.yt_processor", "yt_processor", "/api/yt/*"),
            ("modules.chat_processor.router", "chat_processor", "/api/chat/*")):
        router = _router_opcional(punteado, etiqueta)
        if router is not None:
            app.include_router(router)
            print(f"[MW-Vision] {etiqueta} registrado ({prefijo})")

    return app
