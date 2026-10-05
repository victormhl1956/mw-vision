# -*- coding: utf-8 -*-
"""
Ningún fichero del frontend puede abrir un WebSocket sin pasar por `wsUrl()`.

Por qué. El backend autentica `/ws` desde el 1-oct, y `services/wsUrl.ts` se
escribió entonces para que el token viajara con cada conexión. Pero
`stores/crewStore.ts` —el único que importa media interfaz— armaba la URL a
mano, sin token, así que el backend cerraba cada conexión con 1008 y la pantalla
mostraba «Connection Error» sin causa. Los dos ficheros que SÍ usaban `wsUrl()`,
`hooks/useWebSocket.ts` y `services/websocketService.ts`, no los importa nadie.

El arreglo existía, era correcto y vivía en el camino que no se ejecuta. Es el
mismo defecto de febrero, en el frontend, cometido al arreglar febrero. Esto lo
fija recorriendo el árbol sintáctico, no el texto: `new WebSocket(...)` sólo
vale si su argumento sale de `wsUrl`.
"""
import json
import os
import re
import shutil
import subprocess

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(os.path.dirname(BACKEND), "mw-vision-app")
FUENTES = os.path.join(FRONTEND, "src")

# El único fichero que puede construir la URL es el que la construye.
CONSTRUCTOR = "services/wsUrl.ts"

_NEW_WS = re.compile(r"new\s+WebSocket\s*\(\s*([^)]*)\)", re.S)


def _viene_de_wsurl(argumento: str, fuente: str) -> bool:
    """
    ¿El argumento sale de `wsUrl()`, directa o a través de una variable local?

    La primera versión exigía la palabra `wsUrl` DENTRO del paréntesis, y eso
    marcaba como culpable un `const url = wsUrl('/ws')` seguido de
    `new WebSocket(url)`, que es correcto. Seguir la variable un nivel es la
    misma regla que usan los otros dos medidores; forzar el código a una forma
    que le guste a una regex débil sería al revés.
    """
    if "wsUrl" in argumento:
        return True
    nombre = argumento.strip()
    if not re.fullmatch(r"[A-Za-z_$][\w$]*", nombre):
        return False  # una expresión cualquiera: no se da por buena
    asignacion = re.compile(
        r"(?:const|let|var)\s+" + re.escape(nombre) +
        r"\s*(?::[^=]+)?=\s*[^;\n]*wsUrl\s*\(")
    return bool(asignacion.search(fuente))


def _ficheros():
    if not os.path.isdir(FUENTES):
        pytest.skip("no encuentro las fuentes del frontend")
    salida = []
    for base, dirs, nombres in os.walk(FUENTES):
        dirs[:] = [d for d in dirs if d not in {"node_modules", "dist"}]
        for n in nombres:
            if n.endswith((".ts", ".tsx")) and not n.endswith(".d.ts"):
                salida.append(os.path.join(base, n))
    return salida


def test_todo_websocket_del_frontend_pasa_por_wsurl():
    culpables = []
    for ruta in _ficheros():
        rel = os.path.relpath(ruta, FUENTES).replace(os.sep, "/")
        if rel == CONSTRUCTOR:
            continue
        texto = open(ruta, encoding="utf-8").read()
        # Sin comentarios: la explicación de este defecto los menciona.
        sin_com = re.sub(r"/\*.*?\*/", " ", texto, flags=re.S)
        sin_com = "\n".join(re.sub(r"//.*$", "", l) for l in sin_com.splitlines())
        for m in _NEW_WS.finditer(sin_com):
            argumento = m.group(1).strip()
            if _viene_de_wsurl(argumento, sin_com):
                continue
            linea = sin_com[:m.start()].count("\n") + 1
            culpables.append(f"{rel}:{linea} — new WebSocket({argumento[:60]})")
    assert not culpables, (
        "Estos ficheros abren un WebSocket sin pasar por wsUrl(), así que no "
        "mandan el token y el backend los cierra con 1008:\n" +
        "\n".join(f"  {c}" for c in culpables))


def test_el_constructor_manda_el_token_y_avisa_si_falta():
    """
    El contrapeso: si `wsUrl()` dejara de añadir el token, el test de arriba
    pasaría con todo el frontend roto.
    """
    texto = open(os.path.join(FUENTES, CONSTRUCTOR), encoding="utf-8").read()
    assert "token=" in texto, "wsUrl() ya no añade el token a la URL"
    assert "VITE_WS_TOKEN" in texto, "wsUrl() ya no lee el token de la configuración"
    assert "1008" in texto, (
        "wsUrl() ya no explica que el backend cierra con 1008 cuando falta el "
        "token; sin esa explicación, un fallo de configuración se lee como un "
        "fallo de red")


def test_el_store_que_de_verdad_se_usa_es_el_que_se_comprueba():
    """
    Lo que hizo invisible el defecto: wsUrl() estaba bien usado en dos ficheros
    que nadie importa. Esto exige que el store que media interfaz importa sea
    uno de los que pasan por wsUrl.
    """
    ruta = os.path.join(FUENTES, "stores", "crewStore.ts")
    if not os.path.exists(ruta):
        pytest.skip("crewStore.ts cambió de sitio")
    texto = open(ruta, encoding="utf-8").read()
    assert "wsUrl" in texto, (
        "crewStore.ts —el que importan App, FlowView, TeamView, MissionLog y "
        "los dos componentes— volvió a construir la URL por su cuenta")
