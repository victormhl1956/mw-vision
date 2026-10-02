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

# Un trinquete, no un ideal: cuántas llamadas de la interfaz llegan hoy a dato
# real. Si baja, algo se rompió; cuando sube, se sube el número.
#
#   2 de 7   al mediodía del 2026-10-02: sólo el WebSocket, desde dos sitios.
#   3 de 8   al cablear el panel de seguridad a /api/security.
#   7 de 13  al cablear la memoria — con el medidor TODAVÍA CIEGO.
#   6 de 12  el número honrado, una vez el medidor recorre el grafo de imports.
#
# Los tres primeros están medidos con un instrumento que contaba un `fetch` por
# existir en un fichero de src/, no por ser alcanzable desde main.tsx. Lo
# descubrí desconectando la pestaña de la memoria a propósito y viendo pasar
# este mismo test. Al arreglarlo, el número BAJÓ: `hooks/useWebSocket.ts` no lo
# importa nadie — es código muerto, y una de las dos llamadas que contaba como
# real no tenía consumidor.
LLAMADAS_REALES_MINIMO = 6

# La memoria del proyecto, por su nombre. Si alguna desaparece de lo que la
# interfaz pide, es que la pantalla dejó de usarla: capacidad que vuelve al
# cajón, que es de donde la sacamos.
MEMORIA = ("/api/chat/conversations", "/api/chat/search",
           "/api/chat/conversations/{param}", "/api/chat/ingest")


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


def test_la_memoria_sigue_cableada_y_sirviendo_dato_real():
    """
    Las cuatro rutas del procesador de conversaciones son la memoria del
    proyecto. Estuvieron construidas y sin usar: consultas de verdad sobre
    SQLite que ninguna pantalla pedía. Esto fija las dos mitades a la vez — que
    la interfaz las pide, y que lo que las atiende sigue siendo una consulta.
    """
    d = _cruce()
    por_camino = {p["camino"]: p for p in d["paneles"]}
    for camino in MEMORIA:
        p = por_camino.get(camino)
        assert p is not None, (
            f"la interfaz ya no pide {camino}: la memoria volvió a ser "
            f"capacidad sin usar.\nPide: {sorted(por_camino)}")
        assert p["veredicto"] == "REAL", (
            f"{camino} lo pide la interfaz pero ya no llega a dato real: "
            f"{p['veredicto']} — {p['origenes']}")


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
