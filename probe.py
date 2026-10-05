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

# Probe nació cableado a la disposición de mw-vision: `AQUI/backend` y
# `AQUI/mw-vision-app`. Eso es el mismo defecto que le reprocho a DEEPEX
# —una herramienta que sólo corre donde se escribió— un nivel más suave: no
# una letra de unidad, pero sí un proyecto único. Si Probe ha de servir para
# VeraVadis y para los blogs, tiene que apuntarse a otro sitio y, cuando lo
# que busca no está, decir que no lo sabe en vez de inventar un veredicto.
OMITIR = {"venv", ".venv", "node_modules", "__pycache__", ".git", "dist",
          "build", "site-packages", "generated_reports", ".next", "coverage"}


def _hay_rutas_python(d: str) -> bool:
    """¿Hay al menos un decorador de ruta HTTP/WS en este árbol?"""
    import re as _re
    patron = _re.compile(r"@\s*\w+\s*\.\s*(get|post|put|patch|delete|websocket)\s*\(")
    vistos = 0
    for base, dirs, nombres in os.walk(d):
        dirs[:] = [x for x in dirs if x not in OMITIR and not x.startswith(".")]
        for n in nombres:
            if not n.endswith(".py"):
                continue
            vistos += 1
            if vistos > 4000:
                return False
            try:
                with open(os.path.join(base, n), encoding="utf-8",
                          errors="replace") as fh:
                    if patron.search(fh.read()):
                        return True
            except OSError:
                continue
    return False


def descubrir_backend(raiz: str) -> str | None:
    """El árbol Python que sirve rutas: lo declarado, lo convencional, o nada."""
    for candidato in ("backend", "api", "server", "src", "."):
        d = os.path.normpath(os.path.join(raiz, candidato))
        if os.path.isdir(d) and _hay_rutas_python(d):
            return d
    return None


# Candidatos de frontend que el descubrimiento encontró pero no supo decidir.
# Lo lee el informe para poder nombrarlos.
FRONTEND_AMBIGUO: list[str] = []


def descubrir_frontend(raiz: str) -> str | None:
    """
    Un proyecto de node con fuentes, o None si hay más de uno.

    Mi primera versión se quedaba con el primero por orden alfabético, y en
    mw-vision eso eligió `CLAUDE_DESKTOP_REVIEW` en vez de `mw-vision-app`:
    los dos tienen package.json y src/, y «el primero» no es un criterio.
    Es la misma lección que los sensores de las tuberías — cuando varias
    candidatas encajan, no se elige, se declara la duda — y aquí no elegir
    cuesta una línea de `--frontend`.
    """
    global FRONTEND_AMBIGUO
    candidatos = []
    if os.path.isfile(os.path.join(raiz, "package.json")) \
            and os.path.isdir(os.path.join(raiz, "src")):
        candidatos.append(raiz)
    try:
        for n in sorted(os.listdir(raiz)):
            d = os.path.join(raiz, n)
            if n in OMITIR or not os.path.isdir(d):
                continue
            if os.path.isfile(os.path.join(d, "package.json")) \
                    and os.path.isdir(os.path.join(d, "src")):
                candidatos.append(d)
    except OSError:
        return None
    # Un backend de Python con package.json no es el frontend.
    candidatos = [d for d in candidatos
                  if os.path.normpath(d) != os.path.normpath(BACKEND or "")]
    if len(candidatos) == 1:
        FRONTEND_AMBIGUO = []
        return candidatos[0]
    FRONTEND_AMBIGUO = candidatos
    return None


# Se rellenan en main() a partir de --proyecto. Que sean globales es deliberado:
# las cuatro preguntas los leen, y pasarlos por parámetro a todas sólo movería
# el cableado de sitio.
PROYECTO = AQUI
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

def _medidor(nombre: str) -> str | None:
    """
    Dónde está un medidor: junto a Probe, en el backend medido, o en ninguno.

    Mirar junto a Probe primero permite llevarse la carpeta a otro proyecto;
    mirar en el backend permite que cada proyecto traiga su propia versión.
    """
    for d in (os.path.join(AQUI, "tools"), AQUI,
              os.path.join(BACKEND or "", "tools"), BACKEND or ""):
        if not d:
            continue
        p = os.path.join(d, nombre)
        if os.path.isfile(p):
            return p
    return None


def pregunta_alcanzabilidad(bateria: str | None) -> Respuesta:
    r = Respuesta("¿Hay arreglos de seguridad que nadie ejecuta?", False)
    if not BACKEND:
        r.porque_no = ("no encontré árbol Python que medir. Pásalo con "
                       "--backend.")
        return r
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
    if not BACKEND:
        r.porque_no = ("no encontré ningún árbol Python que sirva rutas en este "
                       "proyecto. Pásalo con --backend, o esta pregunta no "
                       "aplica aquí.")
        return r
    guion = _medidor("origen_datos.py")
    if guion is None:
        r.porque_no = ("no encuentro origen_datos.py ni junto a Probe ni en el "
                       "backend; pásalo con --medidores RUTA")
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
    if not BACKEND or not FRONTEND:
        falta = "backend" if not BACKEND else "frontend"
        detalle = ""
        if falta == "frontend" and FRONTEND_AMBIGUO:
            detalle = (" Encontré varios y no elijo: " +
                       ", ".join(os.path.basename(d)
                                 for d in FRONTEND_AMBIGUO) + ".")
        r.porque_no = (f"no encontré el {falta} de este proyecto, así que no "
                       f"puedo cruzar los dos lados. Pásalo con "
                       f"--{falta}.{detalle}")
        return r
    guion = _medidor("panel_a_panel.py")
    if guion is None:
        r.porque_no = "no encuentro panel_a_panel.py; pásalo con --medidores"
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
    if not FRONTEND:
        if FRONTEND_AMBIGUO:
            r.porque_no = (
                "encontré " + str(len(FRONTEND_AMBIGUO)) + " proyectos de node "
                "con fuentes y ninguno es mejor candidato que otro: " +
                ", ".join(os.path.basename(d) for d in FRONTEND_AMBIGUO) +
                ". Dime cuál con --frontend; elegir el primero por orden "
                "alfabético sería inventar un criterio.")
        else:
            r.porque_no = ("no encontré ningún proyecto de node con fuentes en "
                           "este árbol. Pásalo con --frontend, o esta pregunta "
                           "no aplica aquí.")
        return r
    # El extractor necesita un `typescript` que resolver, y lo resuelve desde
    # SU propia ubicación (createRequire), no desde el proyecto medido. Así que
    # puede vivir en otro proyecto y medir este: se busca primero dentro del
    # medido —que es lo ideal, cada proyecto con su versión— y si no está, el
    # que venga con Probe.
    guion = None
    for d in (os.path.join(FRONTEND, "tools"),
              os.path.join(AQUI, "mw-vision-app", "tools"),
              os.path.join(AQUI, "tools")):
        p = os.path.join(d, "llamadas_ui.mjs")
        if os.path.isfile(p):
            guion = p
            break
    if guion is None:
        r.porque_no = ("no encuentro llamadas_ui.mjs ni en el proyecto medido "
                       "ni junto a Probe")
        return r
    prestado = not guion.startswith(os.path.abspath(FRONTEND))
    if shutil.which("node") is None:
        r.porque_no = "hace falta node"
        return r
    fuentes = os.path.join(FRONTEND, "src")
    if not os.path.isdir(fuentes):
        r.porque_no = f"no encuentro las fuentes en {fuentes}"
        return r
    cod, salida, err = _correr(["node", guion, fuentes],
                               cwd=os.path.dirname(os.path.dirname(guion)))
    try:
        datos = json.loads(salida)
    except json.JSONDecodeError:
        r.porque_no = f"llamadas_ui.mjs no dio JSON: {(err or salida)[:200]}"
        return r
    sim = sorted({x["fichero"] for x in datos.get("simulaciones", [])})
    lit = sorted({x["fichero"] for x in datos.get("literales", [])})
    examinados = datos.get("ficheros_de_panel_examinados")
    carpetas = ", ".join(datos.get("carpetas_de_panel", []))
    if examinados == 0:
        # «0 componentes con datos escritos dentro» cuando no se examinó ningún
        # componente no es un aprobado: es que la herramienta buscó donde este
        # proyecto no guarda su interfaz.
        r.porque_no = (f"el medidor busca paneles en {carpetas} y este proyecto "
                       f"no tiene ninguno ahí, así que no examinó ni un "
                       f"fichero. El «0» que saldría no sería un aprobado.")
        return r
    r.contestada = True
    r.cifras = {"ficheros_de_panel_examinados": examinados,
                "ficheros_que_generan_cifras_al_azar": len(sim),
                "componentes_con_datos_escritos_dentro": len(lit),
                "llamadas_que_no_pude_resolver": len(datos.get("sin_resolver", []))}
    r.hallazgos = ([f"{f}: genera cifras con Math.random()" for f in sim] +
                   [f"{f}: pinta una lista de datos escrita dentro" for f in lit])
    r.titular = (f"{len(sim)} fichero(s) generan cifras al azar en el "
                 f"navegador; {len(lit)} pintan datos escritos dentro")
    if prestado:
        # Decirlo importa: el medidor prestado trae sus propios criterios de
        # «componente» y «vista», que pueden no encajar con otro proyecto.
        r.cifras["medidor_prestado_de"] = os.path.relpath(guion, AQUI)
    return r


# ── Informe ─────────────────────────────────────────────────────────────────

def informar(respuestas: list[Respuesta]) -> None:
    print("=" * 78)
    print("MWH-PROBE")
    print("=" * 78)
    print(f"proyecto : {PROYECTO}")
    print(f"backend  : {BACKEND or 'no encontrado'}")
    if FRONTEND:
        print(f"frontend : {FRONTEND}")
    elif FRONTEND_AMBIGUO:
        print(f"frontend : SIN DECIDIR entre "
              f"{', '.join(os.path.basename(d) for d in FRONTEND_AMBIGUO)}")
    else:
        print("frontend : no encontrado")
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
    ap.add_argument("--proyecto", default=AQUI, metavar="RUTA",
                    help="raíz del proyecto a medir (def.: donde vive Probe)")
    ap.add_argument("--backend", default=None, metavar="RUTA",
                    help="árbol Python que sirve rutas, si el descubrimiento "
                         "falla")
    ap.add_argument("--frontend", default=None, metavar="RUTA",
                    help="proyecto de node con las fuentes de la interfaz")
    ap.add_argument("--bateria", default=None, metavar="RUTA",
                    help="ruta de reachability.py de la batería de auditoría")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raiz = os.path.abspath(args.proyecto)
    if not os.path.isdir(raiz):
        print(f"no existe el proyecto: {raiz}", file=sys.stderr)
        return 3

    global BACKEND, FRONTEND, PROYECTO
    PROYECTO = raiz
    BACKEND = (os.path.abspath(args.backend) if args.backend
               else descubrir_backend(raiz))
    FRONTEND = (os.path.abspath(args.frontend) if args.frontend
                else descubrir_frontend(raiz))
    if args.backend and not os.path.isdir(BACKEND):
        print(f"--backend no es un directorio: {BACKEND}", file=sys.stderr)
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
