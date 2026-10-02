# -*- coding: utf-8 -*-
"""
Ningún panel de producción puede servir dato inventado sin que esto falle.

Por qué existe. La etapa 1 del programa de MWH Phase 1 pedía un comprobador que
fallara en CI si una ruta de producción importaba de `fixtures/`, `mocks/` o
`seed/`. En este árbol NO EXISTE ninguno de esos tres directorios, así que esa
regla habría salido verde con los paneles inventados: el dato falso no está
importado, está escrito en el handler o en la semilla de un objeto de módulo.

Así que lo que se comprueba aquí no es de qué directorio viene el dato, sino de
dónde SALE: una consulta a una fuente de verdad, estado del proceso que algo
escribe, o un literal que nadie toca nunca.

La lista de excepciones es explícita y pequeña a propósito. Añadir una cuesta
una línea y queda escrita con su motivo; lo que no puede pasar es que un panel
de estado sea una constante y nadie lo note.
"""
import os
import subprocess
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIDOR = os.path.join(BACKEND, "tools", "origen_datos.py")

# Rutas que son constantes A PROPÓSITO, con el motivo. Cada entrada es una
# afirmación que alguien tiene que poder defender en una revisión.
CONSTANTES_LEGITIMAS = {
    "/": "endpoint de información: nombre y versión del servicio",
    "/api": "índice de la API; su contenido ES la lista de rutas",
    "/platforms": "PLATFORM_REGISTRY es configuración —las plataformas "
                  "soportadas— no estado del sistema",
    "/detect-platform": "calcula desde lo que le mandan, y consulta la misma "
                        "configuración de plataformas",
}

# Rutas que hoy sirven dato inventado y que el equipo acepta mientras se
# cablean. Cada una es deuda declarada, no una excepción permanente: borrar la
# línea es la forma de exigir que se arregle.
DEUDA_ACEPTADA = {
    # Las SIMULADAS: el número que muestran lo genera simulate_agent_updates()
    # con random.randint(). Es la deuda más grave de la lista, porque una
    # constante se ve y un simulador produce números que derivan de forma
    # plausible. crew_state.total_cost, además, se compara contra budget_limit
    # para parar la tripulación: una guarda de presupuesto movida por un dado.
    "/agents": "SIMULADO: crew_state lo escribe modules/crew/simulator.py",
    "/crew": "SIMULADO: crew_state lo escribe modules/crew/simulator.py",
    "/health": "SIMULADO: el health incluye crew_state, que escribe el "
               "simulador; lo de «estoy vivo» sí es real",
    "/api/crew": "SIMULADO: crew_state lo escribe la copia del simulador que "
                 "vive en main.py",
    "/api/routing-history": "SIMULADO: el historial de enrutado de src/main.py",
    # Las SEMILLA: estado en memoria que nadie escribe nunca.
    "/api/agents": "semilla de tres agentes escritos a mano en src/main.py, y "
                   "simulado en main.py; modules/agents/state.py es OTRA "
                   "semilla de los mismos tres — no hay registro real",
    "/api/agents/{agent_id}": "la misma semilla de tres agentes",
    "/api/stats": "estadísticas calculadas sobre esa misma semilla",
}


def _ejecutar(permitidas):
    orden = [sys.executable, MEDIDOR, BACKEND, "--comprobar"]
    for camino in permitidas:
        orden += ["--permitir", camino]
    return subprocess.run(orden, capture_output=True, text=True)


def test_ninguna_ruta_de_produccion_sirve_dato_inventado():
    """
    La comprobación de verdad. Si falla, el mensaje nombra la ruta, el fichero
    y la línea, y por qué no muestra nada verdadero.
    """
    permitidas = list(CONSTANTES_LEGITIMAS) + list(DEUDA_ACEPTADA)
    r = _ejecutar(permitidas)
    assert r.returncode == 0, (
        "Hay rutas de producción que no muestran nada verdadero y no están "
        "declaradas:\n" + r.stderr +
        "\nSi alguna es constante a propósito, añádela a CONSTANTES_LEGITIMAS "
        "con su motivo. Si es un panel que falta cablear, a DEUDA_ACEPTADA."
    )


def test_la_comprobacion_puede_fallar():
    """
    El contrapeso, y la lección de este árbol: un comprobador que no puede
    fallar no comprueba nada. Sin las excepciones declaradas, las rutas que hoy
    sirven semilla TIENEN que salir señaladas. Si este test empieza a fallar
    porque ya no hay ninguna, borra DEUDA_ACEPTADA y celébralo.
    """
    r = _ejecutar(list(CONSTANTES_LEGITIMAS))
    assert r.returncode == 1, (
        "Sin las excepciones de deuda, el comprobador debería señalar algo. "
        "Si de verdad no queda ninguna ruta con dato inventado, vacía "
        "DEUDA_ACEPTADA y borra este test."
    )
    for camino in DEUDA_ACEPTADA:
        assert camino in r.stderr, (
            f"{camino} está declarada como deuda pero el comprobador ya no la "
            f"señala: o se arregló (bórrala de DEUDA_ACEPTADA) o el medidor "
            f"dejó de verla, que es peor."
        )


@pytest.mark.parametrize("camino,motivo", sorted(CONSTANTES_LEGITIMAS.items()))
def test_cada_excepcion_tiene_motivo(camino, motivo):
    """Una excepción sin motivo escrito es una excepción que nadie revisará."""
    assert len(motivo) > 20, f"{camino}: el motivo no explica nada"
