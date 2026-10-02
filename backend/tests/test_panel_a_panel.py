# -*- coding: utf-8 -*-
"""
Los dos lados cruzados: lo que pide la interfaz contra lo que sirve el backend.

Por qué no basta medir cada lado por separado. El backend puede tener rutas
impecables que ningún panel pide —trabajo hecho que no se ve— y la interfaz
puede estar perfectamente cableada, sin un dato escrito dentro, y llamar sólo a
endpoints que devuelven una semilla. Las dos mediciones salen bien y el producto
sigue mostrando cifras inventadas. Eso sólo se ve uniendo las listas.

Lo que se fija aquí es un trinquete, no un ideal: cuántas de las llamadas de la
interfaz llegan hoy a dato real. Si baja, algo se rompió. Cuando suba, se sube
el número y se celebra.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRUCE = os.path.join(BACKEND, "tools", "panel_a_panel.py")
FRONTEND = os.path.join(os.path.dirname(BACKEND), "mw-vision-app")

# Medido el 2026-10-02: de las 7 llamadas que hace la interfaz, 2 llegan a dato
# real, y las dos son el mismo WebSocket desde dos sitios. Todas las peticiones
# HTTP que hace la interfaz —agentes, un agente, historial de enrutado,
# estadísticas y ejecutar una tarea— caen en simulador o en semilla.
LLAMADAS_REALES_MINIMO = 2


def _cruce():
    if shutil.which("node") is None:
        pytest.skip("hace falta node para leer el frontend")
    if not os.path.isdir(os.path.join(FRONTEND, "node_modules", "typescript")):
        pytest.skip("hace falta el typescript del frontend instalado")
    p = subprocess.run(
        [sys.executable, CRUCE, "--backend", BACKEND, "--frontend", FRONTEND,
         "--json"], capture_output=True, text=True)
    assert p.returncode == 0, f"el cruce falló: {p.stderr[:600]}"
    return json.loads(p.stdout)


def test_no_baja_el_numero_de_paneles_que_llegan_a_dato_real():
    d = _cruce()
    reales = [p for p in d["paneles"] if p["veredicto"] == "REAL"]
    assert len(reales) >= LLAMADAS_REALES_MINIMO, (
        f"Sólo {len(reales)} de {len(d['paneles'])} llamadas de la interfaz "
        f"llegan a dato real; el mínimo fijado es {LLAMADAS_REALES_MINIMO}. "
        f"Algo que funcionaba dejó de hacerlo.\n" +
        "\n".join(f"  [{p['veredicto']}] {p['camino']} <- {p['fichero']}:"
                  f"{p['linea']}" for p in d["paneles"])
    )


def test_ninguna_llamada_de_la_interfaz_se_queda_sin_ruta():
    """
    Una llamada sin ruta es un panel ROTO, no uno falso: la interfaz pide algo
    que el backend no sirve. Es un fallo distinto y más barato de arreglar, y
    hay que verlo aparte.
    """
    d = _cruce()
    huerfanas = [p for p in d["paneles"] if p["veredicto"] == "SIN RUTA"]
    assert not huerfanas, (
        "La interfaz pide endpoints que el backend no sirve:\n" +
        "\n".join(f"  {p['clase']} {p['camino']} <- {p['fichero']}:"
                  f"{p['linea']} {p['donde']}()" for p in huerfanas)
    )


def test_el_cruce_ve_los_dos_lados():
    """
    El contrapeso. Si el extractor del frontend deja de encontrar llamadas, los
    dos tests de arriba pasarían con una lista vacía: cero llamadas sin ruta y
    cero que dejaron de ser reales. Un cruce que no cruza nada aprueba todo.
    """
    d = _cruce()
    assert d["paneles"], (
        "El cruce no encontró ninguna llamada en la interfaz. O el frontend "
        "cambió de forma de pedir datos, o el extractor se rompió."
    )
    assert d["rutas_que_nadie_pide"], (
        "El cruce no encontró ninguna ruta sin pedir, lo que sería una "
        "sorpresa: el backend sirve 32 rutas y la interfaz llama a 7."
    )
