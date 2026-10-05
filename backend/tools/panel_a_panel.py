#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panel por panel, hasta su origen: une lo que pide la interfaz con lo que el
backend sirve de verdad.

Por qué hace falta unir los dos lados. Medir sólo el backend dice qué rutas
devuelven dato real, pero no si alguien las usa: una ruta impecable que ningún
panel pide no es un panel. Y medir sólo el frontend dice que la interfaz está
cableada —llama a `fetch`, no tiene datos escritos dentro— y eso parece bueno
hasta que se mira a dónde llama. Una interfaz perfectamente cableada contra un
endpoint que devuelve una semilla de tres agentes sigue siendo un panel falso, y
eso sólo se ve cruzando las dos listas.

Lo que sale:

  · por cada llamada de la interfaz, qué ruta del backend la atiende y qué
    origen tiene el dato de esa ruta (CONSULTA, MEMORIA VIVA, SIMULADO,
    MEMORIA SEMILLA, CONSTANTE, MAQUETA, NO SÉ);
  · las llamadas que NO encuentran ruta: la interfaz pide algo que el backend
    no sirve, que es un panel roto, no uno falso;
  · las rutas que nadie pide: trabajo hecho que no se ve, o un cliente que no
    es esta interfaz.

Depende de dos herramientas que ya existen y no las repite:
  origen_datos.py   (backend, Python)
  ../mw-vision-app/tools/llamadas_ui.mjs   (frontend, TypeScript)

Uso:
  python panel_a_panel.py --backend .. --frontend ../../mw-vision-app
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
REAL = ("CONSULTA", "MEMORIA VIVA")


def medir_backend(raiz: str) -> dict:
    orden = [sys.executable, os.path.join(AQUI, "origen_datos.py"), raiz,
             "--json"]
    p = subprocess.run(orden, capture_output=True, text=True)
    if p.returncode not in (0, 1):
        raise RuntimeError(f"origen_datos.py falló ({p.returncode}): "
                           f"{p.stderr[:400]}")
    return json.loads(p.stdout)


def medir_frontend(raiz: str) -> dict:
    herramienta = os.path.join(raiz, "tools", "llamadas_ui.mjs")
    if not os.path.exists(herramienta):
        raise RuntimeError(f"no encuentro {herramienta}")
    fuentes = os.path.join(raiz, "src")
    p = subprocess.run(["node", herramienta, fuentes], capture_output=True,
                       text=True, cwd=raiz)
    if p.returncode != 0:
        raise RuntimeError(f"llamadas_ui.mjs falló: {p.stderr[:400]}")
    return json.loads(p.stdout)


def _regex_de_ruta(camino: str) -> re.Pattern:
    """
    Una ruta de FastAPI como patrón: /api/agents/{agent_id} casa con
    /api/agents/{param} y con /api/agents/UC123.
    """
    partes = []
    for trozo in camino.strip("/").split("/"):
        if trozo.startswith("{") and trozo.endswith("}"):
            partes.append(r"[^/]+")
        else:
            partes.append(re.escape(trozo))
    return re.compile("^/" + "/".join(partes) + "$")


def emparejar(llamada: str, rutas: list[dict]) -> list[dict]:
    """
    Las rutas que podrían atender esta llamada.

    Devuelve TODAS las que casan, no una: en este árbol la misma ruta la sirven
    varios puntos de entrada con orígenes de dato distintos —/api/agents es
    simulado en main.py y semilla en src/main.py—, y quedarse con la primera
    escondería justo eso.
    """
    salida = []
    for r in rutas:
        camino = r["camino"]
        if camino == llamada:
            salida.append(r)
            continue
        if "{" in camino and _regex_de_ruta(camino).match(
                llamada.replace("{param}", "X")):
            salida.append(r)
    return salida


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Cruza las llamadas de la interfaz con el origen del dato "
                    "de cada ruta del backend.")
    ap.add_argument("--backend", default=os.path.dirname(AQUI),
                    help="raíz del backend (por defecto, el padre de tools/)")
    ap.add_argument("--frontend", default=None,
                    help="raíz del frontend (por defecto, ../mw-vision-app)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    frontend = args.frontend or os.path.join(
        os.path.dirname(os.path.abspath(args.backend)), "mw-vision-app")

    back = medir_backend(args.backend)
    front = medir_frontend(frontend)

    rutas = back["rutas"]
    paneles = []
    for l in front["llamadas"]:
        candidatas = emparejar(l["camino"], rutas)
        origenes = sorted({r["origen"] for r in candidatas})
        if not candidatas:
            veredicto = "SIN RUTA"
        elif all(o in REAL for o in origenes):
            veredicto = "REAL"
        elif any(o in REAL for o in origenes):
            veredicto = "DEPENDE DEL ENTRY POINT"
        else:
            veredicto = "FALSO"
        paneles.append({**l, "veredicto": veredicto, "origenes": origenes,
                        "rutas": [f"{r['fichero']}:{r['linea']} {r['origen']}"
                                  for r in candidatas]})

    pedidos = set()
    for l in front["llamadas"]:
        for r in emparejar(l["camino"], rutas):
            pedidos.add((r["fichero"], r["linea"]))
    nadie_pide = [r for r in rutas
                  if (r["fichero"], r["linea"]) not in pedidos]

    if args.json:
        print(json.dumps({"paneles": paneles,
                          "rutas_que_nadie_pide": nadie_pide,
                          "llamadas_sin_resolver": front["sin_resolver"]},
                         ensure_ascii=False, indent=2))
        return 0

    print("=" * 78)
    print("PANEL POR PANEL: lo que pide la interfaz contra lo que sirve el "
          "backend")
    print("=" * 78)
    cuenta: dict[str, int] = {}
    for p in paneles:
        cuenta[p["veredicto"]] = cuenta.get(p["veredicto"], 0) + 1
    print(f"llamadas de la interfaz : {len(paneles)}")
    for k in ("REAL", "DEPENDE DEL ENTRY POINT", "FALSO", "SIN RUTA"):
        if k in cuenta:
            print(f"{k:<26}: {cuenta[k]}")

    reales = cuenta.get("REAL", 0)
    if paneles:
        print()
        print(f"De las {len(paneles)} llamadas que hace la interfaz, "
              f"{reales} llegan a dato real.")
        if reales == 0:
            print("  Ninguna. La interfaz está cableada; lo que hay detrás, no.")

    for p in paneles:
        print(f"\n[{p['veredicto']}] {p['clase']} {p['camino']}")
        print(f"         pedido por {p['fichero']}:{p['linea']} "
              f"{p['donde']}()")
        if p["rutas"]:
            for r in p["rutas"]:
                print(f"         atendido por {r}")
        else:
            print("         NINGUNA ruta del backend atiende esto")

    if nadie_pide:
        print(f"\n── Rutas que esta interfaz no pide ({len(nadie_pide)}) ──")
        print("   (puede ser otro cliente, o trabajo hecho que no se ve)")
        for r in sorted(nadie_pide, key=lambda x: (x["camino"], x["fichero"])):
            print(f"   {r['metodo']:<9} {r['camino']:<30} {r['origen']:<16} "
                  f"{r['fichero']}:{r['linea']}")

    if front["sin_resolver"]:
        print(f"\n── Llamadas de la interfaz que no pude resolver "
              f"({len(front['sin_resolver'])}) ──")
        for x in front["sin_resolver"]:
            print(f"   {x['fichero']}:{x['linea']} {x['clase']} -> "
                  f"{x['texto']}")

    print("\nLo que esto NO mide: si el panel pinta lo que el endpoint manda, "
          "y los paneles que no piden nada porque su dato llega por el "
          "WebSocket dentro de un mensaje.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
