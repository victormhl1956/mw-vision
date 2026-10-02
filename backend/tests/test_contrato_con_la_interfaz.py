# -*- coding: utf-8 -*-
"""
La forma de la respuesta, no sólo su existencia.

Esta es la capa que faltaba. Las otras comprobaciones dicen que la ruta existe
(alcanzabilidad), que su dato sale de una consulta (origen_datos) y que el
entrypoint la sirve (openapi). Ninguna mira QUÉ devuelve.

Y ahí había un defecto que dejaba la aplicación EN BLANCO: el frontend se
escribió contra `src/main.py`, que devuelve `[ {id, name, totalCost, …} ]`, y
PM2 arranca `routers/agents.py`, que devuelve `{agents: [ {id, name, cost,
last_update} ], total_cost}`. Un `agents.find(...)` sobre un objeto lanza, React
desmonta el árbol entero y no queda ni un botón en pantalla.

No se veía porque el 404 de /api/stats mataba la inicialización antes de llegar
ahí: un fallo tapando a otro. Lo encontré al arreglar el primero y mirar la
página con un navegador.
"""
import os

import pytest
from fastapi.testclient import TestClient

CLAVE = "0123456789abcdef0123456789abcdef"


@pytest.fixture()
def cliente(monkeypatch):
    monkeypatch.setenv("HYDRA_SECRET_KEY", CLAVE)
    import main_modular
    return TestClient(main_modular.app)


def test_agents_devuelve_algo_que_la_interfaz_puede_recorrer(cliente):
    """
    El frontend normaliza dos formas: una lista, o `{agents: [...]}`. Cualquier
    otra cosa le deja sin agentes. Esto fija que la respuesta sea una de las
    dos, que es el contrato de verdad.
    """
    cuerpo = cliente.get("/api/agents").json()
    es_lista = isinstance(cuerpo, list)
    es_envoltorio = isinstance(cuerpo, dict) and isinstance(
        cuerpo.get("agents"), list)
    assert es_lista or es_envoltorio, (
        "/api/agents no devuelve ni una lista ni {agents: [...]}, así que la "
        f"interfaz se queda sin agentes: {str(cuerpo)[:200]}")


def test_cada_agente_trae_los_campos_que_la_pantalla_lee(cliente):
    """
    Los cuatro que TeamView pinta siempre. Los numéricos y la fecha los
    normaliza el frontend desde varios nombres posibles, así que no se exigen
    aquí; estos cuatro no tienen alternativa.
    """
    cuerpo = cliente.get("/api/agents").json()
    agentes = cuerpo if isinstance(cuerpo, list) else cuerpo["agents"]
    assert agentes, "/api/agents no devolvió ningún agente"
    for a in agentes:
        for campo in ("id", "name", "model", "status"):
            assert campo in a, (
                f"a un agente le falta «{campo}», que la pantalla pinta "
                f"siempre: {str(a)[:160]}")


def test_el_coste_viaja_con_alguno_de_sus_nombres(cliente):
    """
    `totalCost`, `cost` o `total_cost`: el frontend acepta los tres porque los
    dos entrypoints usan nombres distintos. Lo que no puede faltar es el valor,
    o el panel de coste muestra cero sin saber que no lo sabe.
    """
    cuerpo = cliente.get("/api/agents").json()
    agentes = cuerpo if isinstance(cuerpo, list) else cuerpo["agents"]
    for a in agentes:
        assert any(k in a for k in ("totalCost", "cost", "total_cost")), (
            f"el agente {a.get('id')} no trae el coste con ninguno de los tres "
            f"nombres que la interfaz reconoce: {sorted(a)}")


def test_security_trae_la_evidencia_que_el_panel_pinta(cliente):
    """El panel de seguridad lee `evidence.checks` y `evidence.counts`."""
    cuerpo = cliente.get("/api/security").json()
    ev = cuerpo.get("evidence")
    assert isinstance(ev, dict), "/api/security ya no trae «evidence»"
    assert isinstance(ev.get("checks"), list) and ev["checks"], (
        "evidence.checks vacío o ausente: el panel se queda sin comprobaciones")
    assert isinstance(ev.get("counts"), dict), "evidence.counts ausente"
    for c in ev["checks"]:
        assert {"name", "status", "evidence"} <= set(c), (
            f"una comprobación sin nombre, estado o evidencia: {c}")
    assert ev.get("score") is None, (
        "volvió la puntuación global: una cifra única promedia lo medido con "
        "lo no medido")


def test_la_memoria_devuelve_la_forma_que_la_pestana_recorre(cliente):
    """`{conversations: [...], total}`, y cada fila con lo que la lista pinta."""
    cuerpo = cliente.get("/api/chat/conversations").json()
    assert isinstance(cuerpo.get("conversations"), list), (
        f"/api/chat/conversations no trae la lista: {str(cuerpo)[:160]}")
    for c in cuerpo["conversations"]:
        for campo in ("conversation_id", "platform", "message_count",
                      "ingested_at"):
            assert campo in c, (
                f"a una conversación le falta «{campo}»: {sorted(c)}")


def test_la_comprobacion_puede_fallar(cliente):
    """
    El contrapeso. Si el cliente devolviera siempre algo vacío, los tests de
    arriba pasarían en vacío. Esto exige que la aplicación conteste de verdad.
    """
    r = cliente.get("/api/agents")
    assert r.status_code == 200, r.text[:200]
    assert r.json(), "/api/agents devolvió un cuerpo vacío"
    assert cliente.get("/api/ruta-que-no-existe").status_code == 404
