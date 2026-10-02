# -*- coding: utf-8 -*-
"""
La interfaz tampoco puede inventarse el dato por su cuenta.

Por qué existe, y es una corrección de un informe mío. Medí las llamadas que
hace el frontend, vi que todas pasaban por `fetch` o por el WebSocket, y escribí
«el frontend no es el problema». No lo había medido. Lo medí después y había
tres cosas:

  · `SecurityDashboard.tsx` es un `useState` con ocho comprobaciones de
    seguridad escritas a mano, TODAS en 'pass' —incluida «Authentication»— y una
    puntuación de 92 fija. Mientras la autenticación del WebSocket estuvo sin
    cablear, ese panel decía que pasaba. Es el falso verde de febrero en forma
    de interfaz. Y `/api/security`, que sirve métricas reales, es una de las
    rutas que nadie pide.
  · su botón «refrescar» suma amenazas detectadas con `Math.random()`.
  · `FlowView.handleLaunch()` reparte `Math.random() * 2` como coste de cada
    agente dos segundos después de lanzar la tripulación. Es un SEGUNDO
    simulador, independiente del backend: apagar el del backend (MW_SIMULADOR)
    no para este.

Así que el coste que se ve puede venir de dos sitios distintos que inventan, uno
por lado del cable. Esto fija los dos que hay y prohíbe un tercero.
"""
import json
import os
import re
import shutil
import subprocess

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(os.path.dirname(BACKEND), "mw-vision-app")
HERRAMIENTA = os.path.join(FRONTEND, "tools", "llamadas_ui.mjs")

# Deuda declarada, con su motivo. Borrar una línea es la forma de exigir que se
# arregle; añadir una debería costar una conversación.
SIMULACIONES_CONOCIDAS = {
    "components/security/SecurityDashboard.tsx":
        "el botón de refrescar suma peticiones bloqueadas y amenazas con "
        "Math.random(); el panel entero debería leer /api/security, que ya "
        "sirve métricas reales y nadie pide",
    "views/FlowView.tsx":
        "handleLaunch() reparte Math.random() * 2 como coste de cada agente; "
        "es un simulador independiente del backend, así que MW_SIMULADOR=off "
        "no lo apaga",
}

LITERALES_CONOCIDOS = {
    "components/security/SecurityDashboard.tsx":
        "ocho comprobaciones de seguridad escritas a mano, todas en 'pass', y "
        "una puntuación de 92 fija",
    "views/BlueprintView.tsx":
        "initialMockFiles, y handleGitHubImport() que devuelve cuatro ficheros "
        "inventados tras un setTimeout de 3 s y anuncia «Imported 4 files»",
}


def _medir():
    if shutil.which("node") is None:
        pytest.skip("hace falta node para leer el frontend")
    if not os.path.isdir(os.path.join(FRONTEND, "node_modules", "typescript")):
        pytest.skip("hace falta el typescript del frontend instalado")
    p = subprocess.run(["node", HERRAMIENTA, os.path.join(FRONTEND, "src")],
                       capture_output=True, text=True, cwd=FRONTEND)
    assert p.returncode == 0, f"llamadas_ui.mjs falló: {p.stderr[:500]}"
    return json.loads(p.stdout)


def test_ningun_fichero_nuevo_inventa_cifras_en_el_navegador():
    d = _medir()
    ficheros = sorted({s["fichero"] for s in d["simulaciones"]})
    nuevos = [f for f in ficheros if f not in SIMULACIONES_CONOCIDAS]
    assert not nuevos, (
        "Ficheros del frontend que generan cifras con Math.random() y no están "
        "declarados:\n" + "\n".join(f"  {f}" for f in nuevos) +
        "\nSi es un identificador o una clave de React, el medidor debería "
        "excluirlo; si es un dato, no puede inventarse en el navegador."
    )


def test_ningun_panel_nuevo_pinta_datos_escritos_a_mano():
    d = _medir()
    ficheros = sorted({l["fichero"] for l in d["literales"]})
    nuevos = [f for f in ficheros if f not in LITERALES_CONOCIDOS]
    assert not nuevos, (
        "Componentes o vistas con listas de datos escritas dentro y no "
        "declaradas:\n" + "\n".join(f"  {f}" for f in nuevos)
    )


def test_la_deuda_declarada_sigue_siendo_real():
    """
    El contrapeso de los dos de arriba: si el medidor se rompe, los dos pasan
    con una lista vacía. Esto exige que lo que declaramos como deuda siga
    apareciendo — y cuando se arregle de verdad, el test dice que se borre la
    línea.
    """
    d = _medir()
    vistos_sim = {s["fichero"] for s in d["simulaciones"]}
    vistos_lit = {l["fichero"] for l in d["literales"]}
    for f in SIMULACIONES_CONOCIDAS:
        assert f in vistos_sim, (
            f"{f} está declarado como simulador y el medidor ya no lo ve: o se "
            f"arregló (bórralo de SIMULACIONES_CONOCIDAS) o el medidor dejó de "
            f"verlo, que es peor."
        )
    for f in LITERALES_CONOCIDOS:
        assert f in vistos_lit, (
            f"{f} está declarado con datos escritos a mano y el medidor ya no "
            f"lo ve: o se arregló (bórralo) o el medidor se rompió."
        )


def test_el_panel_de_seguridad_no_puede_declararse_sano_a_si_mismo():
    """
    El caso que más duele, y el que explica cómo pudo declararse «Security
    100%» en febrero: el panel de seguridad trae ocho comprobaciones fijas en
    'pass'. Mientras VULN-001 estuvo abierta, ese panel decía que la
    autenticación pasaba.

    Esto no exige que el panel esté arreglado —aún no lo está— sino que el día
    que alguien lo toque, no pueda dejar las comprobaciones cableadas a 'pass'
    sin que esto se entere.
    """
    ruta = os.path.join(FRONTEND, "src", "components", "security",
                        "SecurityDashboard.tsx")
    if not os.path.exists(ruta):
        pytest.skip("el panel de seguridad ya no está donde estaba")
    texto = open(ruta, encoding="utf-8").read()
    # Con coma al final: así se cuenta el VALOR escrito a mano y no la
    # declaración del tipo `status: 'pass' | 'fail' | ...`, que es legítima.
    # Contar sin la coma daba 9 y me hizo escribir un trinquete con un número
    # que no había medido.
    fijas = len(re.findall(r"status:\s*'pass'\s*,", texto))
    assert fijas <= 8, (
        f"{fijas} comprobaciones de seguridad cableadas a 'pass' en el panel. "
        f"Había 8 el 2026-10-02 y es deuda declarada; añadir más es ir hacia "
        f"atrás. La salida: leer /api/security, que ya sirve métricas reales."
    )
    if "fetch" in texto or "/api/security" in texto:
        assert fijas == 0, (
            "El panel ya pide /api/security, así que no puede quedar ninguna "
            "comprobación cableada a 'pass': bórralas y usa la respuesta."
        )
