# -*- coding: utf-8 -*-
"""
El simulador no arranca solo, y cuando arranca se dice.

Por qué existe. `modules/crew/simulator.py` genera la actividad de los agentes
con `random.randint(100, 600)`, la multiplica por una tabla de costes escrita a
mano y escribe el resultado en `crew_state.total_cost` — que después se compara
contra `crew_state.budget_limit` para parar la tripulación. Los dos puntos de
entrada lo lanzaban sin condición en su lifespan, así que todo el gasto que
mostraba el centro de mando en producción era un dado, y la guarda de
presupuesto que actuaba sobre él, también.

Un estado simulado es peor que una constante. La constante se ve de un golpe; el
simulador produce números que derivan de forma plausible y no se distinguen de
la telemetría. Es exactamente lo que hace que una interfaz parezca viva.
"""
import ast
import os

import pytest

from modules.crew.simulacion import VARIABLE, aviso_simulacion, simulacion_activa

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize("valor", ["on", "ON", "1", "true", "yes", "si", "sí",
                                   " on "])
def test_se_enciende_solo_si_se_pide(monkeypatch, valor):
    monkeypatch.setenv(VARIABLE, valor)
    assert simulacion_activa(), f"{valor!r} debería encender el simulador"


@pytest.mark.parametrize("valor", ["", "off", "0", "false", "no", "nope",
                                   "onn", "sim", "x"])
def test_cualquier_otra_cosa_lo_deja_apagado(monkeypatch, valor):
    """
    La respuesta segura a «¿debo inventarme los números?» es no. Una errata no
    puede encender un simulador.
    """
    monkeypatch.setenv(VARIABLE, valor)
    assert not simulacion_activa(), f"{valor!r} NO debería encenderlo"


def test_sin_la_variable_esta_apagado(monkeypatch):
    monkeypatch.delenv(VARIABLE, raising=False)
    assert not simulacion_activa(), (
        "El simulador arrancaba por defecto en los dos puntos de entrada: "
        "ese era el defecto."
    )


def test_el_aviso_dice_en_cual_de_los_dos_estados_esta(monkeypatch):
    """Un interruptor silencioso no se puede auditar desde el log."""
    monkeypatch.setenv(VARIABLE, "on")
    encendido = aviso_simulacion()
    monkeypatch.delenv(VARIABLE, raising=False)
    apagado = aviso_simulacion()
    assert encendido != apagado
    assert "NO son reales" in encendido, encendido
    assert VARIABLE in apagado, apagado


_ENTRADAS = ("core/app.py", "main.py")


@pytest.mark.parametrize("fichero", _ENTRADAS)
def test_ningun_punto_de_entrada_lanza_el_simulador_sin_condicion(fichero):
    """
    La comprobación que de verdad importa, y la que generaliza: apagarlo en un
    sitio no lo apagaba en el otro, porque `main.py` tiene su PROPIA copia de
    `simulate_agent_updates()`. Esto recorre el árbol sintáctico y exige que
    toda creación de esa tarea esté dentro de una condición.
    """
    ruta = os.path.join(BACKEND, fichero)
    arbol = ast.parse(open(ruta, encoding="utf-8").read())

    sin_condicion = []
    for n in ast.walk(arbol):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        es_create_task = (isinstance(f, ast.Attribute) and f.attr == "create_task")
        if not es_create_task:
            continue
        # ¿El argumento es simulate_agent_updates()?
        argumento = n.args[0] if n.args else None
        nombre = ""
        if isinstance(argumento, ast.Call):
            g = argumento.func
            nombre = (g.id if isinstance(g, ast.Name)
                      else g.attr if isinstance(g, ast.Attribute) else "")
        if "simulate" not in nombre:
            continue
        # Tiene que estar bajo una condición: un IfExp o dentro de un if.
        bajo_condicion = any(
            isinstance(p, (ast.If, ast.IfExp))
            for p in _antepasados(arbol, n))
        if not bajo_condicion:
            sin_condicion.append(getattr(n, "lineno", "?"))

    assert not sin_condicion, (
        f"{fichero} lanza el simulador sin condición en la línea o líneas "
        f"{sin_condicion}. Cada punto de entrada tiene su propia copia: "
        f"apagarlo en uno no lo apaga en el otro."
    )


def _antepasados(arbol, objetivo):
    """Los nodos que contienen a `objetivo`, para saber si está bajo un if."""
    encontrados = []

    def bajar(n, camino):
        if n is objetivo:
            encontrados.extend(camino)
            return True
        for hijo in ast.iter_child_nodes(n):
            if bajar(hijo, camino + [n]):
                return True
        return False

    bajar(arbol, [])
    return encontrados


def test_la_etiqueta_viaja_con_el_dato():
    """
    Que el simulador esté apagado no basta: cuando se encienda para una demo,
    la respuesta tiene que decirlo, o el número plausible volverá a pasar por
    medido.
    """
    for fichero, ruta_api in (("routers/crew.py", "/crew"),
                              ("routers/main.py", "/health"),
                              ("main.py", "/api/crew")):
        texto = open(os.path.join(BACKEND, fichero), encoding="utf-8").read()
        assert "datos_simulados" in texto, (
            f"{fichero} sirve {ruta_api} sin decir si el dato es simulado"
        )
