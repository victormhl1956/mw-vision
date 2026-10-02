#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿De dónde sale el dato de cada panel? Medido, no supuesto.

La etapa 1 del programa de MWH Phase 1 es la puerta que decide el resto: hay
que saber qué porcentaje de la interfaz muestra estado real. La parte que no
necesita arrancar nada se mide desde el código: si el endpoint que alimenta un
panel devuelve una constante, el panel es falso sea como sea la interfaz.

Por qué no basta el comprobador que yo mismo propuse. La regla era «fallar en
CI si una ruta de producción importa de fixtures/, mocks/ o seed/». En este
árbol NO EXISTE ninguno de esos tres directorios, así que esa regla saldría
verde con todos los paneles inventados: el dato falso no está importado, está
escrito dentro del handler. Un comprobador que no puede fallar no comprueba
nada.

Lo que mide, por ruta:

  CONSULTA    el handler llega a una fuente de verdad: base de datos, otro
              servicio, el sistema de ficheros, el estado de un proceso.
  CONSTANTE   devuelve un literal, o un literal de módulo. Panel falso.
  MAQUETA     nombres de dato de juguete (demo, sample, fake, dummy,
              placeholder) o un TODO/FIXME en el camino del retorno.
  NO SÉ       no pude resolverlo. No se cuenta como ninguna de las otras tres.

El porcentaje de la puerta se calcula SÓLO sobre las rutas que pude clasificar,
y el informe dice cuántas quedaron sin clasificar. Un porcentaje que esconde su
denominador es la forma más barata de mentir con una medición.

Modos:
  --medir       el informe y el número de la puerta (sale 0 siempre: es una
                medición, no un juicio)
  --comprobar   falla con 1 si alguna ruta de producción es CONSTANTE o
                MAQUETA. Esto sí es para CI.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict

CONSULTA = "CONSULTA"
# Estado que vive en el proceso y que algo ESCRIBE mientras funciona: real
# mientras el proceso viva, perdido al reiniciar. No es invento, pero tampoco
# es fuente de verdad.
MEMORIA_VIVA = "MEMORIA VIVA"
# Estado en memoria cuyo único escritor es la semilla literal del import. Esta
# es la categoría que nadie encuentra leyendo: el panel parece vivo porque pasa
# por un objeto, y el objeto nunca cambia. Una constante con pasos de más.
MEMORIA_SEMILLA = "MEMORIA SEMILLA"
# Estado que se mueve, y que lo mueve un generador de números aleatorios. Es la
# categoría más peligrosa de todas y la última que añadí, porque la encontré
# midiendo: una constante se ve a simple vista, pero un simulador produce
# números que derivan de forma plausible y son indistinguibles de telemetría.
SIMULADO = "SIMULADO"
CONSTANTE = "CONSTANTE"
MAQUETA = "MAQUETA"
NO_SE = "NO SÉ"
ORDEN = (CONSULTA, MEMORIA_VIVA, SIMULADO, MEMORIA_SEMILLA, CONSTANTE, MAQUETA,
         NO_SE)
# Lo que cuenta como «el panel muestra algo verdadero» para la puerta.
REAL = (CONSULTA, MEMORIA_VIVA)
INVENTADO = (SIMULADO, MEMORIA_SEMILLA, CONSTANTE, MAQUETA)

# Quién escribe: un módulo o una función cuyo nombre lo declara, o un cuerpo
# que usa el generador de aleatorios.
SIMULADORES = re.compile(
    r"(?<![A-Za-z0-9])(simulat\w*|simulad\w*|simulaci\w*|fake\w*|synthetic|"
    r"sintetic\w*|randomiz\w*|dummy)(?![A-Za-z0-9])", re.I)

EXCLUIR = ("venv", "node_modules", "__pycache__", ".git", "site-packages",
           "dist", "build", ".venv", "generated_reports")

# Un decorador de ruta: @app.get(...), @router.post(...), @app.websocket(...)
DECOR_RUTA = re.compile(
    r"^(app|router|api|v1|_app|[a-z_]*router)$", re.I)
VERBOS = {"get", "post", "put", "patch", "delete", "websocket", "head",
          "options"}

# Llegar a una fuente de verdad. No vale con importar la librería: hay que
# usarla en el camino del handler.
# Métodos cuyo nombre es ambiguo: `get` y `post` son peticiones HTTP sólo si el
# receptor es un cliente. `task.get("x")` es un diccionario. Sin esta
# distinción, cualquier handler que lea un campo de su petición parecía
# consultar una fuente de verdad.
AMBIGUOS = {"get", "post", "put", "request", "query", "select", "update",
            "pop", "add"}
RECEPTOR_CLIENTE = re.compile(
    r"(client|session|http|httpx|requests|aiohttp|api|conn|cx|cursor|db|"
    r"engine|pool|redis|urllib|socket)", re.I)

SENALES_CONSULTA = {
    # bases de datos
    "execute", "executemany", "fetchone", "fetchall", "fetchmany", "cursor",
    "connect", "query", "scalar", "scalars", "session", "select", "commit",
    # otros servicios
    "get", "post", "put", "request", "AsyncClient", "Client", "urlopen",
    # sistema de ficheros y procesos
    "open", "read_text", "read_bytes", "listdir", "scandir", "glob", "iglob",
    "stat", "getsize", "exists", "walk", "run", "check_output", "Popen",
    "getloadavg", "virtual_memory", "cpu_percent", "disk_usage",
}
# Nombres cuyo solo uso ya implica dato vivo.
MODULOS_CONSULTA = {"sqlite3", "psycopg2", "pymysql", "sqlalchemy", "httpx",
                    "requests", "aiohttp", "urllib", "subprocess", "psutil",
                    "redis", "pymongo", "pathlib", "shutil", "socket"}
# `os` entero estaba aquí, y eso hizo que cuatro rutas pasaran a CONSULTA sólo
# por leer una variable de entorno: la puerta subió de 52% a 65% sin que nada
# se cableara. Leer configuración NO es consultar un dato — os.path.join
# tampoco—. Los usos de os que sí son fuente de verdad (getsize, listdir,
# walk, exists) están nombrados uno a uno en SENALES_CONSULTA. Lo pilló el test
# que exige que el comprobador siga pudiendo fallar.
NUNCA_CONSULTA = {"getenv", "environ", "putenv", "setenv", "path", "sep",
                  "join", "dirname", "basename", "abspath", "normpath",
                  "splitext", "name", "getcwd"}

# Las fronteras son (?<![A-Za-z0-9]) en vez de \b porque el dato de juguete
# vive dentro de los nombres: _sample_metrics, FAKE_AGENTS, datos_demo. Con \b,
# el guión bajo es carácter de palabra y no había frontera que ver.
# Envoltorios puros: len(x), sum(x), round(x, 2) no son el origen del dato,
# son la forma de presentarlo. Si no se mira dentro, len(conexiones) sale
# «no sé de dónde viene» y un panel vivo se cuenta como desconocido.
ENVOLTORIOS = {"len", "sum", "sorted", "list", "dict", "set", "tuple", "str",
               "int", "float", "round", "max", "min", "abs", "any", "all",
               "bool", "reversed", "enumerate", "zip", "map", "filter",
               "next", "iter", "repr", "format", "json"}

MUTADORES = {"append", "extend", "insert", "update", "pop", "remove", "clear",
             "add", "discard", "setdefault", "popitem", "sort", "reverse"}

MAQUETA_PALABRAS = re.compile(
    r"(?<![A-Za-z0-9])(demo|sample|fake|dummy|placeholder|lorem|ipsum|mock|"
    r"stub|fixture|ejemplo|prueba|toy|hardcoded?|harcoded?)(?![A-Za-z0-9])",
    re.I)
PENDIENTE = re.compile(r"\b(TODO|FIXME|XXX|HACK|pendiente|por hacer)\b", re.I)


@dataclass
class Ruta:
    fichero: str
    linea: int
    metodo: str
    camino: str
    handler: str
    origen: str
    porque: str
    pistas: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Lectura del árbol
# ─────────────────────────────────────────────────────────────────────────────

def ficheros_python(raiz: str, incluir_pruebas: bool) -> list[str]:
    salida = []
    for base, dirs, nombres in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in EXCLUIR and not d.startswith(".")]
        for n in nombres:
            if not n.endswith(".py"):
                continue
            ruta = os.path.join(base, n)
            rel = os.path.relpath(ruta, raiz).replace("\\", "/")
            if not incluir_pruebas and es_prueba(rel):
                continue
            salida.append(ruta)
    return sorted(salida)


def es_prueba(rel: str) -> bool:
    partes = rel.split("/")
    return (any(p in ("tests", "test", "testing", "spec") for p in partes)
            or partes[-1].startswith("test_")
            or partes[-1].endswith("_test.py")
            or partes[-1].startswith("conftest"))


# ─────────────────────────────────────────────────────────────────────────────
# Clasificación
# ─────────────────────────────────────────────────────────────────────────────

def prefijos_de_router(arbol: ast.Module) -> dict[str, str]:
    """
    El prefijo de cada APIRouter del módulo: nombre -> "/api".

    FastAPI lo antepone a cada ruta del router, así que sin esto el camino que
    se mide no es el camino que sirve. En este árbol afecta a cinco ficheros:
    routers/agents.py declara «/agents» y atiende «/api/agents».

    Lo que esto NO cubre: un prefijo añadido al incluir el router
    (`include_router(r, prefix=...)`). Si aparece, el camino medido se quedará
    corto, y el cruce panel-a-panel lo delatará como «SIN RUTA».
    """
    salida: dict[str, str] = {}
    for n in arbol.body:
        if not isinstance(n, (ast.Assign, ast.AnnAssign)):
            continue
        valor = n.value
        if not (isinstance(valor, ast.Call)
                and isinstance(valor.func, ast.Name)
                and valor.func.id == "APIRouter"):
            continue
        prefijo = ""
        for k in valor.keywords:
            if k.arg == "prefix" and isinstance(k.value, ast.Constant) \
                    and isinstance(k.value.value, str):
                prefijo = k.value.value.rstrip("/")
        objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
        for t in objetivos:
            if isinstance(t, ast.Name):
                salida[t.id] = prefijo
    return salida


def decoradores_de_ruta(fn: ast.FunctionDef | ast.AsyncFunctionDef,
                        prefijos: dict[str, str] | None = None
                        ) -> list[tuple[str, str]]:
    """[(verbo, camino)] de los decoradores que declaran una ruta HTTP/WS."""
    salida = []
    for d in fn.decorator_list:
        llamada = d if isinstance(d, ast.Call) else None
        func = llamada.func if llamada else d
        if not isinstance(func, ast.Attribute) or func.attr.lower() not in VERBOS:
            continue
        duenyo = func.value
        nombre = duenyo.id if isinstance(duenyo, ast.Name) else (
            duenyo.attr if isinstance(duenyo, ast.Attribute) else "")
        if not DECOR_RUTA.match(nombre or ""):
            continue
        camino = ""
        if llamada and llamada.args and isinstance(llamada.args[0], ast.Constant) \
                and isinstance(llamada.args[0].value, str):
            camino = llamada.args[0].value
        if camino:
            prefijo = (prefijos or {}).get(nombre or "", "")
            if prefijo:
                camino = prefijo + ("" if camino == "/" else camino)
        salida.append((func.attr.lower(), camino or "(sin camino literal)"))
    return salida


class Rastro(ast.NodeVisitor):
    """Qué toca un cuerpo de función: fuentes de verdad, literales, pendientes."""

    def __init__(self, locales_literales: set[str] | None = None) -> None:
        self.consulta: list[str] = []
        self.llamadas_locales: list[str] = []
        self.partes_literales = 0
        self.raices_devueltas: set[str] = set()
        self.pendiente = False
        self.maqueta: list[str] = []
        # Variables locales del propio handler que nacen de un literal: lo que
        # se devuelva a través de ellas es tan literal como el literal.
        self.locales_literales = locales_literales or set()
        # name -> expresión que se le asignó, para poder seguirla.
        self.locales_asignadas: dict[str, ast.AST] = {}
        self._siguiendo: set[str] = set()

    def visit_Call(self, n: ast.Call) -> None:
        f = n.func
        if isinstance(f, ast.Attribute):
            if f.attr in SENALES_CONSULTA:
                raiz = f.value
                base = (raiz.id if isinstance(raiz, ast.Name)
                        else raiz.attr if isinstance(raiz, ast.Attribute) else "")
                # El verbo de un decorador de ruta no es una consulta: es la
                # declaración. Sin esto, cualquier @router.get contaba como
                # «llega a una fuente de verdad».
                if f.attr in NUNCA_CONSULTA:
                    pass
                elif f.attr in AMBIGUOS and not RECEPTOR_CLIENTE.search(base or ""):
                    # Un .get() sobre algo que no parece un cliente es un
                    # diccionario, no una petición.
                    pass
                elif not (f.attr.lower() in VERBOS and DECOR_RUTA.match(base or "")):
                    self.consulta.append(
                        f"{base}.{f.attr}()" if base else f".{f.attr}()")
        elif isinstance(f, ast.Name):
            if f.id in NUNCA_CONSULTA:
                self.llamadas_locales.append(f.id)
            elif f.id in SENALES_CONSULTA:
                self.consulta.append(f"{f.id}()")
            else:
                self.llamadas_locales.append(f.id)
        self.generic_visit(n)

    def visit_Attribute(self, n: ast.Attribute) -> None:
        if n.attr in NUNCA_CONSULTA:
            self.generic_visit(n)
            return
        if isinstance(n.value, ast.Name) and n.value.id in MODULOS_CONSULTA:
            self.consulta.append(f"{n.value.id}.{n.attr}")
        self.generic_visit(n)

    def visit_Return(self, n: ast.Return) -> None:
        v = n.value
        if v is None:
            return
        # Un dict literal no es una constante por ser literal: lo es si TODOS
        # sus valores lo son. {"conexiones": len(manager.active)} devuelve
        # estado vivo con forma de literal, y clasificarlo como constante fue
        # mi propio falso verde: tres de tres clasificaciones mal.
        self._mirar_devuelto(v)
        self.generic_visit(n)

    def _mirar_devuelto(self, v: ast.AST, profundidad: int = 0) -> None:
        if profundidad > 4:
            self.raices_devueltas.add("(demasiado anidado)")
            return
        if isinstance(v, ast.Constant):
            self.partes_literales += 1
            return
        if isinstance(v, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            hijos = (list(v.values) if isinstance(v, ast.Dict)
                     else list(v.elts))
            if not hijos:
                self.partes_literales += 1
                return
            for h in hijos:
                if h is not None:
                    self._mirar_devuelto(h, profundidad + 1)
            return
        if isinstance(v, ast.JoinedStr):
            for h in v.values:
                if isinstance(h, ast.FormattedValue):
                    self._mirar_devuelto(h.value, profundidad + 1)
            return
        if isinstance(v, ast.IfExp):
            self._mirar_devuelto(v.body, profundidad + 1)
            self._mirar_devuelto(v.orelse, profundidad + 1)
            return
        if isinstance(v, (ast.BinOp, ast.BoolOp, ast.Compare)):
            for h in ast.iter_child_nodes(v):
                if isinstance(h, ast.expr):
                    self._mirar_devuelto(h, profundidad + 1)
            return
        if isinstance(v, (ast.GeneratorExp, ast.ListComp, ast.SetComp,
                          ast.DictComp)):
            # sum(a.coste for a in agentes.values()): la fuente está en el
            # iterable, no en el sum.
            for gen in v.generators:
                self._mirar_devuelto(gen.iter, profundidad + 1)
            return
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) \
                and v.func.id in ENVOLTORIOS:
            if not v.args and not v.keywords:
                self.partes_literales += 1
                return
            for a in v.args:
                self._mirar_devuelto(a, profundidad + 1)
            for k in v.keywords:
                self._mirar_devuelto(k.value, profundidad + 1)
            return
        if isinstance(v, ast.Await):
            self._mirar_devuelto(v.value, profundidad + 1)
            return
        if isinstance(v, ast.Name):
            if v.id in self.locales_literales:
                self.partes_literales += 1
                return
            # Una variable local del handler: se sigue hasta lo que le
            # asignaron. Sin esto, `return {"coste": round(total, 4)}` donde
            # total = sum(...) sobre estado vivo salía NO SÉ.
            origen = self.locales_asignadas.get(v.id)
            if origen is not None and v.id not in self._siguiendo:
                self._siguiendo.add(v.id)
                self._mirar_devuelto(origen, profundidad + 1)
                self._siguiendo.discard(v.id)
                return
            self.raices_devueltas.add(v.id)
            return
        raiz = _nombre_raiz(v)
        if raiz:
            # `opciones.get("a", 0)` donde opciones es un literal local: el
            # resultado es tan literal como el literal. Sin esto, cualquier
            # acceso a un diccionario local salía como raíz sin resolver.
            if raiz in self.locales_literales:
                self.partes_literales += 1
                return
            origen = self.locales_asignadas.get(raiz)
            if origen is not None and raiz not in self._siguiendo:
                self._siguiendo.add(raiz)
                self._mirar_devuelto(origen, profundidad + 1)
                self._siguiendo.discard(raiz)
                return
            self.raices_devueltas.add(raiz)
        else:
            self.raices_devueltas.add("(no resuelto)")


def _locales_literales(fn) -> set[str]:
    """Variables del handler asignadas desde un literal."""
    salida = set()
    for n in ast.walk(fn):
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
            if isinstance(n.value, (ast.Dict, ast.List, ast.Tuple, ast.Set,
                                    ast.Constant)):
                for t in objetivos:
                    if isinstance(t, ast.Name):
                        salida.add(t.id)
    return salida


@dataclass
class Rastreo:
    consulta: list[str] = field(default_factory=list)
    partes_literales: int = 0
    raices: set[str] = field(default_factory=set)
    pendiente: bool = False
    maqueta: list[str] = field(default_factory=list)


def mirar_cuerpo(fn, fuente: str, locales: dict, visto: set[str],
                 nivel: int = 0) -> Rastreo:
    """
    Recorre el cuerpo y, dos niveles, las funciones locales que llama.

    Un handler que delega en un ayudante del mismo módulo no es una constante
    sólo porque su propio cuerpo no toque la base, ni es real sólo porque
    delegue.
    """
    r = Rastro(_locales_literales(fn))
    for n in ast.walk(fn):
        if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
            objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in objetivos:
                if isinstance(t, ast.Name) and t.id not in r.locales_asignadas:
                    r.locales_asignadas[t.id] = n.value
    for sentencia in fn.body:
        r.visit(sentencia)
    out = Rastreo(consulta=list(r.consulta),
                  partes_literales=r.partes_literales,
                  raices=set(r.raices_devueltas))
    segmento = ast.get_source_segment(fuente, fn) or ""
    out.pendiente = bool(PENDIENTE.search(segmento))
    # Sólo los nombres que este código DEFINE o DEVUELVE. Un parámetro de la
    # petición que se llame content_sample no hace falso al endpoint: el dato
    # lo trae quien llama. Mirar el texto entero marcaba de maqueta una ruta
    # que calculaba de verdad.
    sospechosos = (set(r.locales_asignadas) | set(r.raices_devueltas)
                   | set(r.llamadas_locales) | {fn.name})
    out.maqueta = sorted({m.group(0).lower() for nombre in sospechosos
                          for m in MAQUETA_PALABRAS.finditer(nombre)})
    if nivel < 2:
        for nombre in r.llamadas_locales:
            if nombre in visto or nombre not in locales:
                continue
            visto.add(nombre)
            hijo = mirar_cuerpo(locales[nombre], fuente, locales, visto,
                               nivel + 1)
            out.consulta += [f"{nombre}→{x}" for x in hijo.consulta]
            out.pendiente = out.pendiente or hijo.pendiente
            out.maqueta = sorted(set(out.maqueta) | set(hijo.maqueta))
            # Lo que devuelve el ayudante es lo que devuelve el handler.
            out.partes_literales += hijo.partes_literales
            out.raices |= hijo.raices
    return out


def clasificar(fn, fuente: str, locales: dict, estado: "EstadoModulo",
               mod=None, modulos: dict | None = None
               ) -> tuple[str, str, list[str]]:
    r = mirar_cuerpo(fn, fuente, locales, set())

    # El propio handler inventa números: eso manda sobre cualquier consulta que
    # también haga. El único POST que la interfaz llamaba salía CONSULTA y
    # dentro hacía `complexity = random.randint(1, 10)` para «simular el
    # enrutado del Coordinador Estratégico».
    if _funcion_simula(fn):
        return (SIMULADO,
                f"{fn.name}() genera sus propios números con random",
                r.maqueta)

    if r.consulta:
        # Toca una fuente de verdad. Si además huele a maqueta se dice, pero no
        # deja de ser consulta: puede ser una consulta con un nombre feo.
        return (CONSULTA, "llega a " + ", ".join(sorted(set(r.consulta))[:4]),
                r.maqueta)

    # Qué categoría tiene cada raíz devuelta. Lo desconocido no se vota.
    categorias: list[tuple[str, str]] = []
    sin_resolver: list[str] = []
    for raiz in sorted(r.raices):
        cat = estado.categoria(raiz)
        if cat is None and mod is not None and modulos is not None:
            # No está en este módulo: se sigue el import hasta donde se define.
            cat = resolver_fuera(raiz, mod, modulos, set())
        if cat:
            categorias.append(cat)
        else:
            sin_resolver.append(raiz)

    # Si algo del camino llega a una fuente de verdad, eso manda.
    if any(c == CONSULTA for c, _ in categorias):
        porque = next(p for c, p in categorias if c == CONSULTA)
        return CONSULTA, porque, r.maqueta

    # Un panel que mezcla estado simulado con cualquier otra cosa es simulado:
    # el número que se ve no se puede separar del inventado.
    if any(c == SIMULADO for c, _ in categorias):
        porque = next(p for c, p in categorias if c == SIMULADO)
        return SIMULADO, porque, r.maqueta

    # Un panel que devuelve estado vivo Y una semilla no es del todo real: se
    # queda con lo vivo, pero la semilla que viaja al lado queda dicha.
    if any(c == MEMORIA_VIVA for c, _ in categorias):
        porque = next(p for c, p in categorias if c == MEMORIA_VIVA)
        semillas = [p for c, p in categorias if c == MEMORIA_SEMILLA]
        if semillas:
            porque += f" — PERO devuelve también una semilla: {semillas[0]}"
        return MEMORIA_VIVA, porque, r.maqueta

    if r.maqueta:
        return (MAQUETA, "dato de juguete en el camino: " +
                ", ".join(r.maqueta[:5]), r.maqueta)

    if any(c == MEMORIA_SEMILLA for c, _ in categorias):
        porque = next(p for c, p in categorias if c == MEMORIA_SEMILLA)
        return MEMORIA_SEMILLA, porque, r.maqueta

    if not r.raices and r.partes_literales:
        return (CONSTANTE, "todo lo que devuelve está escrito en el código",
                r.maqueta)

    if r.pendiente and not sin_resolver:
        return MAQUETA, "el camino del retorno lleva un TODO/FIXME", r.maqueta

    detalle = (f"devuelve {', '.join(sin_resolver[:4])}, que no sé de dónde "
               f"viene") if sin_resolver else \
        ("no toca ninguna fuente de verdad que reconozca y no veo qué "
         "devuelve")
    return NO_SE, detalle, r.maqueta


@dataclass
class EstadoModulo:
    """
    Qué nombres de módulo hay, cómo nacen y quién les escribe.

    Sin esto no se puede distinguir un panel vivo de uno que sólo pasa por un
    objeto: `agents` puede ser un diccionario con tres entradas escritas a mano
    al importar, y si NADIE le escribe nunca, el endpoint que lo devuelve es
    tan constante como un literal, aunque parezca estado.
    """
    literales: set[str] = field(default_factory=set)      # nace de un literal
    construidos: set[str] = field(default_factory=set)    # nace de Clase(...)
    clase_de: dict[str, str] = field(default_factory=dict)  # nombre -> clase
    escritos: dict[str, list[str]] = field(default_factory=dict)  # quién escribe

    def anota_escritura(self, nombre: str, como: str) -> None:
        self.escritos.setdefault(nombre, [])
        if como not in self.escritos[nombre]:
            self.escritos[nombre].append(como)

    def categoria(self, nombre: str) -> tuple[str, str] | None:
        """(categoría, por qué) para un nombre de módulo, o None si no lo conozco."""
        nace_literal = nombre in self.literales
        nace_objeto = nombre in self.construidos
        if not nace_literal and not nace_objeto:
            return None
        escritores = self.escritos.get(nombre, [])
        if escritores:
            reales = [e for e in escritores if "[SIMULADOR]" not in e]
            if not reales:
                return (SIMULADO,
                        f"«{nombre}» se mueve, y lo mueve un simulador: "
                        f"{', '.join(escritores[:2])}")
            if len(reales) < len(escritores):
                simuladores = [e for e in escritores if "[SIMULADOR]" in e]
                return (SIMULADO,
                        f"«{nombre}» lo escriben código real y un simulador a "
                        f"la vez ({', '.join(simuladores[:1])}), así que lo que "
                        f"se ve no se puede separar de lo inventado")
            return (MEMORIA_VIVA,
                    f"estado en memoria que algo escribe ({', '.join(reales[:3])})")
        if nace_literal:
            return (MEMORIA_SEMILLA,
                    f"«{nombre}» se escribe una vez al importar y nada le "
                    f"escribe después: constante con pasos de más")
        return (MEMORIA_SEMILLA,
                f"«{nombre}» se construye al importar y nada le escribe "
                f"después: el panel no puede cambiar")


def _nombre_raiz(n: ast.AST) -> str | None:
    """El nombre de módulo en la raíz de una expresión: a.b.c() -> 'a'."""
    while True:
        if isinstance(n, ast.Name):
            return n.id
        if isinstance(n, (ast.Attribute, ast.Subscript)):
            n = n.value
            continue
        if isinstance(n, ast.Call):
            n = n.func
            continue
        return None


def _funcion_simula(fn) -> bool:
    """¿Esta función inventa los números que escribe?"""
    if SIMULADORES.search(fn.name):
        return True
    for n in ast.walk(fn):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                and n.value.id == "random":
            return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id in ("randint", "uniform", "choice", "randrange",
                                  "gauss", "shuffle"):
            return True
    return False


def _clase_se_muta(arbol: ast.Module, clase: str) -> str | None:
    """
    ¿Algún método de la clase escribe en su propio self?

    Sin esto, `manager = ConnectionManager()` parecía una semilla muerta aunque
    `connect()` haga `self.active_connections.append(...)`: el escritor es
    «self», no «manager», y mirar sólo los nombres de módulo no lo ve.
    """
    # El constructor NO cuenta: escribir self en __init__ es exactamente la
    # semilla. Si sólo escribe ahí, el objeto no puede cambiar nunca.
    CONSTRUCTORES = {"__init__", "__new__", "__post_init__"}
    for n in ast.walk(arbol):
        if not (isinstance(n, ast.ClassDef) and n.name == clase):
            continue
        metodos = [m for m in n.body
                   if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and m.name not in CONSTRUCTORES]
        for m in ast.walk(ast.Module(body=metodos, type_ignores=[])):
            if isinstance(m, (ast.Assign, ast.AugAssign)):
                objetivos = (m.targets if isinstance(m, ast.Assign)
                             else [m.target])
                for t in objetivos:
                    if isinstance(t, (ast.Attribute, ast.Subscript)) \
                            and _nombre_raiz(t) == "self":
                        return f"métodos de {clase} escriben en self"
            elif isinstance(m, ast.Call) and isinstance(m.func, ast.Attribute) \
                    and m.func.attr in MUTADORES \
                    and _nombre_raiz(m.func.value) == "self":
                return f"{clase}.{m.func.attr}() escribe en self"
    return None


def retratar_modulo(arbol: ast.Module) -> EstadoModulo:
    e = EstadoModulo()
    for n in arbol.body:
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
            valor = n.value
            for t in objetivos:
                if not isinstance(t, ast.Name):
                    continue
                if isinstance(valor, (ast.Dict, ast.List, ast.Tuple, ast.Set,
                                      ast.Constant)):
                    e.literales.add(t.id)
                elif isinstance(valor, ast.Call):
                    e.construidos.add(t.id)
                    clase = (valor.func.id if isinstance(valor.func, ast.Name)
                             else valor.func.attr
                             if isinstance(valor.func, ast.Attribute) else "")
                    if clase:
                        e.clase_de[t.id] = clase
    # Escrituras, con el nombre de quién las hace: hay que saber si el escritor
    # es un simulador aunque viva en el MISMO fichero. main.py tiene su propia
    # copia de simulate_agent_updates(), y mirar sólo los módulos ajenos la
    # dejaba pasar por estado vivo.
    for fn in ast.walk(arbol):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _funcion_simula(fn):
            continue
        marca = f".{fn.name}() [SIMULADOR]"
        for n in ast.walk(fn):
            if isinstance(n, (ast.Assign, ast.AugAssign)):
                objetivos = (n.targets if isinstance(n, ast.Assign)
                             else [n.target])
                for t in objetivos:
                    if isinstance(t, (ast.Subscript, ast.Attribute)):
                        raiz = _nombre_raiz(t)
                        if raiz and raiz != "self":
                            e.anota_escritura(raiz, marca)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in MUTADORES:
                raiz = _nombre_raiz(n.func.value)
                if raiz and raiz != "self":
                    e.anota_escritura(raiz, marca)

    for n in ast.walk(arbol):
        if isinstance(n, (ast.Assign, ast.AugAssign)):
            objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in objetivos:
                if isinstance(t, (ast.Subscript, ast.Attribute)):
                    raiz = _nombre_raiz(t)
                    if raiz:
                        e.anota_escritura(raiz, "asignación")
                elif isinstance(t, ast.Name) and isinstance(n, ast.AugAssign):
                    e.anota_escritura(t.id, "+=")
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in MUTADORES:
            raiz = _nombre_raiz(n.func.value)
            if raiz:
                e.anota_escritura(raiz, f".{n.func.attr}()")
    return e


@dataclass
class Modulo:
    """Un módulo del árbol, con lo que hace falta para seguirle un nombre."""
    punteado: str                       # modules.chat_processor.router
    fuente: str
    arbol: ast.Module
    estado: "EstadoModulo"
    funciones: dict
    # nombre local -> (módulo punteado destino, nombre allí). Lo que permite
    # salir del fichero: la mitad de los paneles devuelven algo importado, y
    # mirar sólo el módulo actual deja un tercio del árbol en NO SÉ.
    importado: dict
    # nombre del router -> su prefijo, que forma parte del camino servido.
    prefijos: dict = field(default_factory=dict)


def _punteado(raiz: str, ruta: str) -> str:
    rel = os.path.relpath(ruta, raiz).replace("\\", "/")
    rel = rel[:-3] if rel.endswith(".py") else rel
    if rel.endswith("/__init__"):
        rel = rel[: -len("/__init__")]
    return rel.replace("/", ".")


def _importaciones(arbol: ast.Module, propio: str) -> dict:
    """De dónde viene cada nombre importado, incluidos los relativos."""
    salida: dict = {}
    paquete = propio.rsplit(".", 1)[0] if "." in propio else ""
    for n in ast.walk(arbol):
        if isinstance(n, ast.ImportFrom):
            if n.level:
                # from . import x / from .storage import y
                base = paquete
                for _ in range(n.level - 1):
                    base = base.rsplit(".", 1)[0] if "." in base else ""
                destino = f"{base}.{n.module}" if n.module else base
            else:
                destino = n.module or ""
            for alias in n.names:
                if alias.name == "*":
                    continue
                salida[alias.asname or alias.name] = (destino, alias.name)
        elif isinstance(n, ast.Import):
            for alias in n.names:
                salida[alias.asname or alias.name.split(".")[0]] = (
                    alias.name, "")
    return salida


def indexar(raiz: str, incluir_pruebas: bool) -> tuple[dict, list[str]]:
    modulos: dict = {}
    fallos: list[str] = []
    for ruta in ficheros_python(raiz, incluir_pruebas):
        try:
            fuente = open(ruta, encoding="utf-8", errors="replace").read()
            arbol = ast.parse(fuente)
        except (OSError, SyntaxError) as e:
            fallos.append(f"{os.path.relpath(ruta, raiz)}: "
                          f"{type(e).__name__}: {e}")
            continue
        punteado = _punteado(raiz, ruta)
        modulos[punteado] = Modulo(
            punteado=punteado, fuente=fuente, arbol=arbol,
            estado=retratar_modulo(arbol),
            funciones={n.name: n for n in ast.walk(arbol)
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))},
            importado=_importaciones(arbol, punteado),
            prefijos=prefijos_de_router(arbol),
        )
        modulos[punteado].ruta = os.path.relpath(ruta, raiz).replace("\\", "/")

    # Segunda pasada: una clase que muta su self, y las escrituras que vienen
    # de OTRO módulo. `crew_state` se construye en modules/crew/state.py y lo
    # escribe main.py; mirando fichero a fichero parecía muerto.
    for mod in modulos.values():
        for nombre, clase in mod.estado.clase_de.items():
            porque = _clase_se_muta(mod.arbol, clase)
            if porque is None:
                destino = mod.importado.get(clase)
                if destino:
                    partes = destino[0].split(".")
                    for i in range(len(partes)):
                        otro = modulos.get(".".join(partes[i:]))
                        if otro is not None:
                            porque = _clase_se_muta(otro.arbol,
                                                    destino[1] or clase)
                            break
            if porque:
                mod.estado.anota_escritura(nombre, porque)

    for mod in modulos.values():
        for nombre, comos in _escrituras_a_importados(mod).items():
            destino = mod.importado.get(nombre)
            if not destino:
                continue
            partes = destino[0].split(".")
            for i in range(len(partes)):
                otro = modulos.get(".".join(partes[i:]))
                if otro is None:
                    continue
                allí = destino[1] or nombre
                if allí in otro.estado.literales or allí in otro.estado.construidos:
                    simulado = _es_simulador(mod)
                    for como in comos:
                        otro.estado.anota_escritura(
                            allí, f"{como} desde {mod.ruta}"
                            + (" [SIMULADOR]" if simulado else ""))
                break
    return modulos, fallos


def _es_simulador(mod: "Modulo") -> bool:
    """
    ¿Este módulo inventa los números que escribe?

    Dos señales: el nombre lo declara, o el cuerpo usa `random`. La segunda es
    la que importa, porque un simulador no siempre se llama simulador.
    """
    if SIMULADORES.search(mod.punteado) or SIMULADORES.search(mod.ruta):
        return True
    for n in ast.walk(mod.arbol):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                and n.value.id == "random":
            return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id in ("randint", "uniform", "choice", "random",
                                  "randrange", "gauss", "shuffle", "sample"):
            return True
    return False


def _escrituras_a_importados(mod: "Modulo") -> dict:
    """Escrituras de este módulo a nombres que trajo de fuera."""
    salida: dict = {}
    for n in ast.walk(mod.arbol):
        raices: list[tuple[str, str]] = []
        if isinstance(n, (ast.Assign, ast.AugAssign)):
            objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in objetivos:
                if isinstance(t, (ast.Subscript, ast.Attribute)):
                    r = _nombre_raiz(t)
                    if r:
                        raices.append((r, "asignación"))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in MUTADORES:
            r = _nombre_raiz(n.func.value)
            if r:
                raices.append((r, f".{n.func.attr}()"))
        for nombre, como in raices:
            if nombre in mod.importado:
                salida.setdefault(nombre, [])
                if como not in salida[nombre]:
                    salida[nombre].append(como)
    return salida


def resolver_fuera(nombre: str, mod: "Modulo", modulos: dict, visto: set,
                   nivel: int = 0) -> tuple[str, str] | None:
    """
    Clasifica un nombre que no está en el módulo actual, siguiéndolo hasta
    donde se define. Devuelve (categoría, por qué) o None si se pierde.
    """
    if nivel > 3:
        return None
    destino_nombre = mod.importado.get(nombre)
    if destino_nombre is None:
        return None
    destino, original = destino_nombre
    # El import puede venir con prefijos que no están en el árbol: se prueban
    # los sufijos (backend.src.x -> src.x -> x).
    candidatos = []
    partes = destino.split(".")
    for i in range(len(partes)):
        candidatos.append(".".join(partes[i:]))
    otro = next((modulos[c] for c in candidatos if c in modulos), None)
    if otro is None or (otro.punteado, original or nombre) in visto:
        return None
    visto.add((otro.punteado, original or nombre))
    buscado = original or nombre

    # ¿Es un dato de módulo allí?
    cat = otro.estado.categoria(buscado)
    if cat:
        categoria, porque = cat
        return categoria, f"{porque} [en {otro.ruta}]"

    # ¿Es una función? Entonces lo que importa es lo que ELLA toca.
    fn = otro.funciones.get(buscado)
    if fn is not None:
        r = mirar_cuerpo(fn, otro.fuente, otro.funciones, set())
        if r.consulta:
            return (CONSULTA,
                    f"{buscado}() en {otro.ruta} llega a "
                    f"{', '.join(sorted(set(r.consulta))[:3])}")
        for raiz_hija in sorted(r.raices):
            propia = otro.estado.categoria(raiz_hija)
            if propia:
                categoria, porque = propia
                return categoria, f"{buscado}(): {porque} [en {otro.ruta}]"
            fuera = resolver_fuera(raiz_hija, otro, modulos, visto, nivel + 1)
            if fuera:
                categoria, porque = fuera
                return categoria, f"{buscado}() -> {porque}"
        if r.maqueta:
            return (MAQUETA, f"{buscado}() en {otro.ruta}: dato de juguete "
                             f"({', '.join(r.maqueta[:3])})")
        if r.partes_literales and not r.raices:
            return (CONSTANTE,
                    f"{buscado}() en {otro.ruta} devuelve sólo literales")
        return None

    # ¿Una clase? Se mira si algún método suyo toca una fuente de verdad.
    for n in ast.walk(otro.arbol):
        if isinstance(n, ast.ClassDef) and n.name == buscado:
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    r = mirar_cuerpo(m, otro.fuente, otro.funciones, set())
                    if r.consulta:
                        return (CONSULTA,
                                f"{buscado}.{m.name}() en {otro.ruta} llega a "
                                f"{', '.join(sorted(set(r.consulta))[:3])}")
            return None
    return None


def medir(raiz: str, incluir_pruebas: bool) -> tuple[list[Ruta], list[str]]:
    modulos, fallos = indexar(raiz, incluir_pruebas)
    rutas: list[Ruta] = []
    for mod in modulos.values():
        for n in ast.walk(mod.arbol):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for verbo, camino in decoradores_de_ruta(n, mod.prefijos):
                origen, porque, pistas = clasificar(
                    n, mod.fuente, mod.funciones, mod.estado, mod, modulos)
                rutas.append(Ruta(mod.ruta, n.lineno, verbo.upper(), camino,
                                  n.name, origen, porque, pistas))
    return rutas, fallos


# ─────────────────────────────────────────────────────────────────────────────
# Informe
# ─────────────────────────────────────────────────────────────────────────────

def informar(rutas: list[Ruta], fallos: list[str], raiz: str) -> None:
    print("=" * 78)
    print(f"ORIGEN DEL DATO POR RUTA  ·  {raiz}")
    print("=" * 78)
    cuenta = {k: [r for r in rutas if r.origen == k] for k in ORDEN}
    clasificadas = len(rutas) - len(cuenta[NO_SE])
    print(f"rutas encontradas : {len(rutas)}")
    for k in ORDEN:
        print(f"{k:<18}: {len(cuenta[k])}")

    reales = sum(len(cuenta[k]) for k in REAL)
    if clasificadas:
        pct = 100 * reales / clasificadas
        print()
        print(f"PUERTA DE LA ETAPA 1: {pct:.0f}% de las rutas clasificadas "
              f"muestran algo verdadero")
        print(f"  ({reales} de {clasificadas}: {len(cuenta[CONSULTA])} por "
              f"consulta y {len(cuenta[MEMORIA_VIVA])} por estado vivo del "
              f"proceso; {len(cuenta[NO_SE])} sin clasificar, fuera del "
              f"porcentaje)")
        if cuenta[SIMULADO]:
            print()
            print(f"  !!! {len(cuenta[SIMULADO])} ruta(s) SIMULADAS: el número "
                  f"que muestran lo genera un simulador. Es peor que una "
                  f"constante — una constante se ve, un simulador produce "
                  f"números que derivan de forma plausible.")
        if cuenta[MEMORIA_VIVA]:
            print(f"  Aviso sobre las {len(cuenta[MEMORIA_VIVA])} de estado "
                  f"vivo: son verdad mientras el proceso viva y se pierden al "
                  f"reiniciar. Para Phase 1 habrá que persistirlas.")
        if pct >= 60:
            print("  >= 60%: el trabajo es cablear los paneles que faltan, "
                  "uno a uno.")
        elif pct >= 20:
            print("  20-60%: hay núcleo real; la rebanada vertical se "
                  "construye sobre lo que ya funciona.")
        else:
            print("  < 20%: la pregunta deja de ser «construir Phase 1» y "
                  "pasa a ser «qué backend existe de verdad».")
    else:
        print("\nNo pude clasificar ninguna ruta: el número de la puerta es "
              "NO SÉ.")

    for k in (SIMULADO, MEMORIA_SEMILLA, CONSTANTE, MAQUETA, NO_SE,
              MEMORIA_VIVA, CONSULTA):
        if not cuenta[k]:
            continue
        print(f"\n-- {k} --")
        for r in sorted(cuenta[k], key=lambda x: (x.fichero, x.linea)):
            print(f"  {r.metodo:<9} {r.camino}")
            print(f"            {r.fichero}:{r.linea} {r.handler}()")
            print(f"            {r.porque}")

    if fallos:
        print("\nFicheros que no pude leer:")
        for f in fallos:
            print(f"  - {f}")
    print("\nLo que esto NO mide: si la consulta devuelve algo, si la "
          "interfaz pinta lo que el endpoint manda, y los paneles que no pasan "
          "por una ruta HTTP. Para eso hace falta arrancarlo.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Mide de dónde sale el dato de cada ruta: consulta real, "
                    "constante, maqueta o NO SÉ.")
    ap.add_argument("raiz")
    ap.add_argument("--comprobar", action="store_true",
                    help="falla con 1 si alguna ruta de producción es "
                         "CONSTANTE o MAQUETA (para CI)")
    ap.add_argument("--incluir-pruebas", action="store_true",
                    help="no excluir tests/ (por defecto se excluyen)")
    ap.add_argument("--permitir", action="append", default=[], metavar="CAMINO",
                    help="ruta que se acepta como constante a propósito "
                         "(repetible); p.ej. /health")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.raiz):
        print(f"no es un directorio: {args.raiz}", file=sys.stderr)
        return 3

    rutas, fallos = medir(args.raiz, args.incluir_pruebas)

    if args.json:
        print(json.dumps({
            "raiz": args.raiz,
            "rutas": [asdict(r) for r in rutas],
            "fallos": fallos,
        }, ensure_ascii=False, indent=2))
    else:
        informar(rutas, fallos, args.raiz)

    if args.comprobar:
        malas = [r for r in rutas
                 if r.origen in INVENTADO and r.camino not in args.permitir]
        if malas:
            print(f"\nCI: {len(malas)} ruta(s) de producción no muestran "
                  f"nada verdadero.", file=sys.stderr)
            for r in malas:
                print(f"  {r.metodo} {r.camino}  ({r.fichero}:{r.linea}) "
                      f"— {r.porque}", file=sys.stderr)
            print("\nSi alguna es constante a propósito (un /health que sólo "
                  "dice 'estoy vivo'), decláralo con --permitir CAMINO. Lo que "
                  "no vale es que un panel de estado sea una constante y nadie "
                  "lo note.", file=sys.stderr)
            return 1
        print("\nCI: ninguna ruta de producción devuelve dato inventado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
