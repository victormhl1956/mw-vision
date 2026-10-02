#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MWH-Probe: una nota del proyecto que se puede reproducir y discutir.

Por qué existe. El informe consolidado de DEEPEX da «Security 100%» a este
repositorio. Lo que DEEPEX recibe para puntuar es un objeto de metadatos —líneas
de código, cuenta de ficheros por nombre de carpeta y una descripción escrita a
mano— y no una sola línea de código; esa descripción además declara
«FastAPI + PostgreSQL» cuando el backend usa SQLite. La nota salió del 100%
mientras el endpoint `/ws` no autenticaba a nadie. Y su implementación vive en
`L:/nicedev-Project/...`, así que no corre en ningún otro sitio ni se puede
revisar.

Probe no puntúa. Hace cuatro preguntas que se contestan leyendo el código, y de
cada una da el número Y SU DENOMINADOR:

  1. ¿Hay arreglos que nadie ejecuta?        reachability.py
  2. ¿De dónde sale el dato de cada ruta?    tools/origen_datos.py
  3. ¿Qué pide la interfaz, y se lo sirve
     algo de verdad?                         tools/panel_a_panel.py
  4. ¿Se inventa la interfaz sus cifras?     ../mw-vision-app/tools/llamadas_ui.mjs

Tres reglas, que son las que a DEEPEX le faltaban:

  · ninguna medida sin denominador. «61% real» sin decir sobre cuántas y cuántas
    quedaron sin clasificar no es una medida, es una impresión con decimales.
  · lo que no se puede medir se dice. Probe nunca convierte un «no sé» en un
    punto a favor ni en uno en contra; lo cuenta aparte y lo deja fuera del
    porcentaje.
  · ninguna nota global. Una cifra única invita a promediar lo medido con lo no
    medido, y así «no lo sé» se vuelve «va bien». Es exactamente cómo se llega a
    un 100%.

Código de salida: 0 si no hay nada que mirar, 1 si hay hallazgos accionables,
2 si alguna pregunta quedó sin contestar, 3 si Probe no pudo ejecutarse.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict

AQUI = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(AQUI, "backend")
FRONTEND = os.path.join(AQUI, "mw-vision-app")


@dataclass
class Respuesta:
    """Una pregunta contestada, o declarada sin contestar."""
    pregunta: str
    contestada: bool
    titular: str = ""
    # Las cifras con su denominador, siempre juntas.
    cifras: dict = field(default_factory=dict)
    hallazgos: list = field(default_factory=list)
    porque_no: str = ""


def _correr(orden: list[str], cwd: str | None = None,
            tiempo: int = 300) -> tuple[int, str, str]:
    try:
        p = subprocess.run(orden, capture_output=True, text=True, cwd=cwd,
                           timeout=tiempo)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        return 127, "", str(e)
    except subprocess.TimeoutExpired:
        return 124, "", f"pasó de {tiempo} s"


# ── 1. Arreglos que nadie ejecuta ───────────────────────────────────────────

def pregunta_alcanzabilidad(bateria: str | None) -> Respuesta:
    r = Respuesta("¿Hay arreglos de seguridad que nadie ejecuta?", False)
    guion = bateria or os.path.expanduser(
        "~/.claude/skills/audit-battery/scripts/reachability.py")
    if not os.path.exists(guion):
        r.porque_no = (f"no encuentro reachability.py en {guion}. Es la "
                       f"pregunta que encontró VULN-001; sin ella, Probe no la "
                       f"puede contestar.")
        return r
    cod, salida, err = _correr([sys.executable, guion, BACKEND])
    if cod == 127 or (not salida and err):
        r.porque_no = f"reachability.py falló: {err[:200]}"
        return r
    sin_cablear, no_alcanzables, modulos = [], None, None
    en_bloque = False
    for linea in salida.splitlines():
        if "ARREGLOS SIN CABLEAR" in linea:
            en_bloque = True
            continue
        if en_bloque and linea.strip().startswith("!"):
            # La cabecera del bloque es una fila de «!»: sin este filtro
            # entraba como un hallazgo vacío y la cuenta salía con uno de más.
            texto = linea.strip().strip("!").strip()
            if texto and "->" in texto:
                sin_cablear.append(texto)
        if linea.strip().startswith("---"):
            en_bloque = False
        if "NO alcanzables" in linea and ":" in linea:
            no_alcanzables = linea.split(":")[-1].strip()
        if linea.strip().startswith("módulos"):
            modulos = linea.split(":")[-1].strip()
    r.contestada = True
    r.cifras = {"modulos_del_arbol": modulos,
                "modulos_no_alcanzables": no_alcanzables,
                "simbolos_de_seguridad_sin_cablear": len(sin_cablear)}
    r.hallazgos = sin_cablear
    r.titular = (f"{len(sin_cablear)} símbolo(s) de seguridad en módulos que "
                 f"nadie alcanza; {no_alcanzables} de {modulos} módulos "
                 f"inalcanzables")
    return r


# ── 2. De dónde sale el dato de cada ruta ───────────────────────────────────

def pregunta_origen() -> Respuesta:
    r = Respuesta("¿De dónde sale el dato de cada ruta?", False)
    guion = os.path.join(BACKEND, "tools", "origen_datos.py")
    if not os.path.exists(guion):
        r.porque_no = f"no encuentro {guion}"
        return r
    cod, salida, err = _correr([sys.executable, guion, BACKEND, "--json"])
    try:
        datos = json.loads(salida)
    except json.JSONDecodeError:
        r.porque_no = f"origen_datos.py no dio JSON: {(err or salida)[:200]}"
        return r
    rutas = datos["rutas"]
    por_origen: dict[str, int] = {}
    for x in rutas:
        por_origen[x["origen"]] = por_origen.get(x["origen"], 0) + 1
    sin_clasificar = por_origen.get("NO SÉ", 0)
    clasificadas = len(rutas) - sin_clasificar
    reales = por_origen.get("CONSULTA", 0) + por_origen.get("MEMORIA VIVA", 0)
    r.contestada = True
    r.cifras = {"rutas": len(rutas), "clasificadas": clasificadas,
                "sin_clasificar_fuera_del_porcentaje": sin_clasificar,
                "muestran_algo_verdadero": reales,
                "por_origen": por_origen}
    r.hallazgos = [
        f"{x['metodo']} {x['camino']} ({x['fichero']}:{x['linea']}) — "
        f"{x['origen']}: {x['porque']}"
        for x in rutas
        if x["origen"] in ("SIMULADO", "MEMORIA SEMILLA", "CONSTANTE", "MAQUETA")
    ]
    pct = f"{100 * reales / clasificadas:.0f}%" if clasificadas else "NO SÉ"
    r.titular = (f"{pct} de las rutas clasificadas muestran algo verdadero "
                 f"({reales} de {clasificadas}; {sin_clasificar} sin "
                 f"clasificar, fuera del porcentaje)")
    return r


# ── 3. Lo que pide la interfaz contra lo que se sirve ───────────────────────

def pregunta_cruce() -> Respuesta:
    r = Respuesta("¿Lo que pide la interfaz lo sirve algo de verdad?", False)
    guion = os.path.join(BACKEND, "tools", "panel_a_panel.py")
    if not os.path.exists(guion):
        r.porque_no = f"no encuentro {guion}"
        return r
    if shutil.which("node") is None:
        r.porque_no = ("hace falta node para leer el frontend; sin él, esta "
                       "pregunta queda sin contestar, no aprobada")
        return r
    if not os.path.isdir(os.path.join(FRONTEND, "node_modules", "typescript")):
        r.porque_no = ("hace falta el typescript del frontend instalado "
                       "(npm install en mw-vision-app)")
        return r
    cod, salida, err = _correr(
        [sys.executable, guion, "--backend", BACKEND, "--frontend", FRONTEND,
         "--json"])
    try:
        datos = json.loads(salida)
    except json.JSONDecodeError:
        r.porque_no = f"panel_a_panel.py no dio JSON: {(err or salida)[:200]}"
        return r
    paneles = datos["paneles"]
    por_veredicto: dict[str, int] = {}
    for p in paneles:
        por_veredicto[p["veredicto"]] = por_veredicto.get(p["veredicto"], 0) + 1
    r.contestada = True
    r.cifras = {"llamadas_de_la_interfaz": len(paneles),
                "por_veredicto": por_veredicto,
                "rutas_que_nadie_pide": len(datos["rutas_que_nadie_pide"]),
                "llamadas_sin_resolver": len(datos["llamadas_sin_resolver"])}
    r.hallazgos = [
        f"{p['clase']} {p['camino']} <- {p['fichero']}:{p['linea']} — "
        f"{p['veredicto']}" for p in paneles if p["veredicto"] != "REAL"]
    reales = por_veredicto.get("REAL", 0)
    r.titular = (f"{reales} de {len(paneles)} llamadas de la interfaz llegan a "
                 f"dato real; {len(datos['rutas_que_nadie_pide'])} rutas que "
                 f"nadie pide")
    return r


# ── 4. La interfaz y sus propias cifras ─────────────────────────────────────

def pregunta_frontend() -> Respuesta:
    r = Respuesta("¿Se inventa la interfaz sus propias cifras?", False)
    guion = os.path.join(FRONTEND, "tools", "llamadas_ui.mjs")
    if not os.path.exists(guion):
        r.porque_no = f"no encuentro {guion}"
        return r
    if shutil.which("node") is None:
        r.porque_no = "hace falta node"
        return r
    cod, salida, err = _correr(["node", guion, os.path.join(FRONTEND, "src")],
                               cwd=FRONTEND)
    try:
        datos = json.loads(salida)
    except json.JSONDecodeError:
        r.porque_no = f"llamadas_ui.mjs no dio JSON: {(err or salida)[:200]}"
        return r
    sim = sorted({x["fichero"] for x in datos.get("simulaciones", [])})
    lit = sorted({x["fichero"] for x in datos.get("literales", [])})
    r.contestada = True
    r.cifras = {"ficheros_que_generan_cifras_al_azar": len(sim),
                "componentes_con_datos_escritos_dentro": len(lit),
                "llamadas_que_no_pude_resolver": len(datos.get("sin_resolver", []))}
    r.hallazgos = ([f"{f}: genera cifras con Math.random()" for f in sim] +
                   [f"{f}: pinta una lista de datos escrita dentro" for f in lit])
    r.titular = (f"{len(sim)} fichero(s) generan cifras al azar en el "
                 f"navegador; {len(lit)} pintan datos escritos dentro")
    return r


# ── Informe ─────────────────────────────────────────────────────────────────

def informar(respuestas: list[Respuesta]) -> None:
    print("=" * 78)
    print("MWH-PROBE")
    print("=" * 78)
    print("Cuatro preguntas que se contestan leyendo el código. Sin nota "
          "global: una")
    print("cifra única invita a promediar lo medido con lo no medido, y así se "
          "llega")
    print("a un 100%.")

    for r in respuestas:
        print()
        print("-" * 78)
        marca = "CONTESTADA" if r.contestada else "SIN CONTESTAR"
        print(f"[{marca}] {r.pregunta}")
        if not r.contestada:
            print(f"  No lo sé: {r.porque_no}")
            print("  Esto NO cuenta como aprobado ni como suspendido.")
            continue
        print(f"  {r.titular}")
        for k, v in r.cifras.items():
            print(f"    {k}: {v}")
        if r.hallazgos:
            print(f"  {len(r.hallazgos)} hallazgo(s):")
            for h in r.hallazgos[:12]:
                print(f"    · {h}")
            if len(r.hallazgos) > 12:
                print(f"    … y {len(r.hallazgos) - 12} más (usa --json)")

    con_hallazgos = sum(1 for r in respuestas if r.contestada and r.hallazgos)
    sin_contestar = sum(1 for r in respuestas if not r.contestada)
    print()
    print("=" * 78)
    print(f"{len(respuestas) - sin_contestar} de {len(respuestas)} preguntas "
          f"contestadas; {con_hallazgos} con hallazgos accionables; "
          f"{sin_contestar} sin contestar.")
    print("Lo que Probe NO mira: si la consulta devuelve algo, si el panel "
          "pinta lo que")
    print("el endpoint manda, y nada que necesite arrancar el sistema.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Nota del proyecto que se puede reproducir: cuatro "
                    "preguntas, cada cifra con su denominador, sin nota "
                    "global.")
    ap.add_argument("--bateria", default=None, metavar="RUTA",
                    help="ruta de reachability.py de la batería de auditoría")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(BACKEND):
        print(f"no encuentro el backend en {BACKEND}", file=sys.stderr)
        return 3

    respuestas = [pregunta_alcanzabilidad(args.bateria), pregunta_origen(),
                  pregunta_cruce(), pregunta_frontend()]

    if args.json:
        print(json.dumps({"respuestas": [asdict(r) for r in respuestas]},
                         ensure_ascii=False, indent=2))
    else:
        informar(respuestas)

    if any(r.contestada and r.hallazgos for r in respuestas):
        return 1
    if any(not r.contestada for r in respuestas):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
