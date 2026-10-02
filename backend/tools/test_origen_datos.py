#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas del medidor de origen de datos.

Cada caso es un fichero de rutas donde yo sé la respuesta correcta. Si el
medidor no acierta en estos, su número de la puerta no vale nada — y un número
de puerta equivocado manda el programa entero por el camino que no es.
"""
import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
HERRAMIENTA = os.path.join(AQUI, "origen_datos.py")
FALLOS: list[str] = []
HECHAS = 0


def comprobar(nombre, condicion, detalle=""):
    global HECHAS
    HECHAS += 1
    if not condicion:
        FALLOS.append(f"{nombre}: {detalle}" if detalle else nombre)


CASOS = {
    # ── consultas de verdad ────────────────────────────────────────────────
    "consulta_sqlite.py": ('''
import sqlite3
from fastapi import APIRouter
router = APIRouter()

@router.get("/api/piezas")
async def piezas():
    cx = sqlite3.connect("osint.db")
    filas = cx.execute("SELECT COUNT(*) FROM pieces").fetchone()
    return {"total": filas[0]}
''', {"/api/piezas": "CONSULTA"}),

    "consulta_por_ayudante.py": ('''
import sqlite3
from fastapi import FastAPI
app = FastAPI()

def _contar():
    # el handler delega: no por eso es una constante
    return sqlite3.connect("x.db").execute("SELECT 1").fetchone()[0]

@app.get("/api/stats")
def stats():
    return {"n": _contar()}
''', {"/api/stats": "CONSULTA"}),

    "consulta_otro_servicio.py": ('''
import httpx
from fastapi import APIRouter
router = APIRouter()

@router.get("/api/costos")
async def costos():
    async with httpx.AsyncClient() as c:
        r = await c.get("http://localhost:8477/v1/costos")
    return r.json()
''', {"/api/costos": "CONSULTA"}),

    "consulta_ficheros.py": ('''
import os
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/disco")
def disco():
    return {"mb": os.path.getsize("osint.db") / 1048576}
''', {"/api/disco": "CONSULTA"}),

    # ── constantes: paneles falsos ─────────────────────────────────────────
    "constante_literal.py": ('''
from fastapi import APIRouter
router = APIRouter()

@router.get("/api/crew")
def crew():
    return {"agents": 7, "active": 7, "status": "operational"}
''', {"/api/crew": "CONSTANTE"}),

    "constante_de_modulo.py": ('''
from fastapi import FastAPI
app = FastAPI()

AGENTES = [{"id": "a1", "name": "Scout"}, {"id": "a2", "name": "Analyst"}]

@app.get("/api/agents")
def agents():
    return AGENTES
''', {"/api/agents": "MEMORIA SEMILLA"}),

    # ── maquetas ───────────────────────────────────────────────────────────
    "maqueta_nombre.py": ('''
from fastapi import APIRouter
router = APIRouter()

def _sample_metrics():
    return {"cpu": 12, "ram": 44}

@router.get("/api/metrics")
def metrics():
    return _sample_metrics()
''', {"/api/metrics": "MAQUETA"}),

    "maqueta_todo.py": ('''
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/needs")
def needs():
    # TODO: conectar con el modelo de trabajo
    return []
''', {"/api/needs": "CONSTANTE"}),

    # ── un .get() no es una petición, y un handler que tira el dado simula ─
    # Los dos defectos que escondían el único POST que la interfaz llamaba:
    # `task.get("x")` contaba como petición HTTP, y el handler hacía
    # `random.randint(1, 10)` para «simular el enrutado».
    "dado_y_dict.py": ('''
import random
from fastapi import FastAPI
app = FastAPI()

@app.post("/api/ejecutar")
def ejecutar(tarea: dict):
    complejidad = random.randint(1, 10)
    return {"consulta": tarea.get("tarea", "manual"), "complejidad": complejidad}

@app.get("/api/solo-dict")
def solo_dict():
    opciones = {"a": 1}
    return {"valor": opciones.get("a", 0)}
''', {"/api/ejecutar": "SIMULADO", "/api/solo-dict": "CONSTANTE"}),

    "cliente_si_cuenta.py": ('''
import httpx
from fastapi import FastAPI
app = FastAPI()

cliente = httpx.Client()

@app.get("/api/remoto")
def remoto():
    return cliente.get("http://localhost:8477/v1/costos").json()
''', {"/api/remoto": "CONSULTA"}),

    # ── el prefijo del APIRouter forma parte del camino ────────────────────
    # routers/agents.py declara «/agents» y atiende «/api/agents». Sin el
    # prefijo, el cruce con la interfaz no encontraba la ruta que de verdad
    # sirve cada panel, y cinco ficheros del árbol llevan prefijo.
    "con_prefijo.py": ('''
import sqlite3
from fastapi import APIRouter
router = APIRouter(prefix="/api")

@router.get("/agentes")
def agentes():
    return sqlite3.connect("x.db").execute("SELECT 1").fetchall()

@router.get("/")
def raiz():
    return {"ok": True}
''', {"/api/agentes": "CONSULTA", "/api": "CONSTANTE"}),

    "prefijo_profundo.py": ('''
from fastapi import APIRouter
router = APIRouter(prefix="/api/chat/", tags=["x"])

LISTA = [{"a": 1}]

@router.get("/platforms")
def plataformas():
    return LISTA
''', {"/api/chat/platforms": "MEMORIA SEMILLA"}),

    # ── leer configuración NO es consultar un dato ─────────────────────────
    # Añadir una etiqueta honesta («¿esto es simulado?») hizo que cuatro rutas
    # pasaran a CONSULTA sólo por llamar a os.getenv, y la puerta subió 13
    # puntos sin que nada se cableara. Una medición que mejora porque se le
    # añade una etiqueta no mide nada.
    "configuracion_no_es_dato.py": ('''
import os
from fastapi import FastAPI
app = FastAPI()

BANDERAS = {"modo": "demo"}

@app.get("/api/bandera")
def bandera():
    return {**BANDERAS, "simulado": os.getenv("MW_SIMULADOR") == "on",
            "ruta": os.path.join("a", "b")}
''', {"/api/bandera": "MEMORIA SEMILLA"}),

    # ── estado en memoria: vivo, semilla, y el literal con valores vivos ───
    "memoria_viva.py": ('''
from fastapi import FastAPI
app = FastAPI()

metricas = {"conexiones": 0, "rechazos": 0}

@app.get("/api/metricas")
def metricas_endpoint():
    return {"metricas": metricas}

@app.websocket("/ws2")
async def ws2(socket):
    metricas["conexiones"] += 1
''', {"/api/metricas": "MEMORIA VIVA"}),

    "memoria_semilla.py": ('''
from fastapi import FastAPI
app = FastAPI()

class Estado:
    def __init__(self): self.corriendo = False

estado = Estado()

@app.get("/api/estado")
def estado_endpoint():
    return {"corriendo": estado.corriendo}
''', {"/api/estado": "MEMORIA SEMILLA"}),

    "literal_con_valores_vivos.py": ('''
from fastapi import FastAPI
app = FastAPI()

conexiones = []

@app.get("/api/seguridad")
def seguridad():
    # Un dict literal cuyos VALORES son estado vivo no es una constante.
    # Clasificarlo así fue mi propio falso verde al medir mw-vision.
    return {"activas": len(conexiones), "limite": 100}

@app.websocket("/ws3")
async def ws3(socket):
    conexiones.append(socket)
''', {"/api/seguridad": "MEMORIA VIVA"}),

    # ── websocket y camino no literal ──────────────────────────────────────
    "websocket.py": ('''
import sqlite3
from fastapi import FastAPI
app = FastAPI()

@app.websocket("/ws")
async def ws(socket):
    sqlite3.connect("x.db").execute("SELECT 1")
''', {"/ws": "CONSULTA"}),
}


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="prueba-origen-")
    for nombre, (codigo, _) in CASOS.items():
        with open(os.path.join(tmp, nombre), "w", encoding="utf-8") as f:
            f.write(codigo)

    p = subprocess.run([sys.executable, HERRAMIENTA, tmp, "--json"],
                       capture_output=True, text=True)
    datos = json.loads(p.stdout)
    por_camino = {r["camino"]: r for r in datos["rutas"]}

    esperado = {}
    for _, (_, mapa) in CASOS.items():
        esperado.update(mapa)

    faltan = [c for c in esperado if c not in por_camino]
    comprobar("encuentra todas las rutas esperadas", not faltan,
              f"faltan {faltan}; encontró {sorted(por_camino)}")
    comprobar("ningún fichero ilegible", not datos["fallos"],
              str(datos["fallos"]))

    for camino, quiero in esperado.items():
        r = por_camino.get(camino)
        comprobar(f"{camino} es {quiero}",
                  r is not None and r["origen"] == quiero,
                  f"salió {r['origen'] if r else '(no encontrada)'} — "
                  f"{r['porque'] if r else ''}")

    # ── los tests NO se cuentan por defecto ───────────────────────────────
    os.makedirs(os.path.join(tmp, "tests"), exist_ok=True)
    with open(os.path.join(tmp, "tests", "test_rutas.py"), "w",
              encoding="utf-8") as f:
        f.write('''
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/solo-en-test")
def falsa():
    return {"x": 1}
''')
    p2 = subprocess.run([sys.executable, HERRAMIENTA, tmp, "--json"],
                        capture_output=True, text=True)
    d2 = json.loads(p2.stdout)
    comprobar("tests/ se excluye por defecto",
              not any(r["camino"] == "/api/solo-en-test" for r in d2["rutas"]),
              str([r["camino"] for r in d2["rutas"]]))
    p3 = subprocess.run([sys.executable, HERRAMIENTA, tmp, "--json",
                         "--incluir-pruebas"], capture_output=True, text=True)
    d3 = json.loads(p3.stdout)
    comprobar("y se incluye si se pide",
              any(r["camino"] == "/api/solo-en-test" for r in d3["rutas"]))

    # ── el modo CI falla, y el permiso explícito lo deja pasar ────────────
    p4 = subprocess.run([sys.executable, HERRAMIENTA, tmp, "--comprobar"],
                        capture_output=True, text=True)
    comprobar("el modo CI falla con constantes presentes", p4.returncode == 1,
              f"{p4.returncode} / {p4.stderr[:200]}")
    comprobar("y nombra las rutas culpables", "/api/crew" in p4.stderr,
              p4.stderr[:300])

    solo_sano = tempfile.mkdtemp(prefix="prueba-origen-sano-")
    with open(os.path.join(solo_sano, "r.py"), "w", encoding="utf-8") as f:
        f.write(CASOS["consulta_sqlite.py"][0])
    p5 = subprocess.run([sys.executable, HERRAMIENTA, solo_sano, "--comprobar"],
                        capture_output=True, text=True)
    comprobar("el modo CI pasa cuando todo consulta", p5.returncode == 0,
              f"{p5.returncode} / {p5.stdout[-200:]} {p5.stderr[:200]}")

    solo_constante = tempfile.mkdtemp(prefix="prueba-origen-cte-")
    with open(os.path.join(solo_constante, "r.py"), "w", encoding="utf-8") as f:
        f.write(CASOS["constante_literal.py"][0])
    p6 = subprocess.run([sys.executable, HERRAMIENTA, solo_constante,
                         "--comprobar", "--permitir", "/api/crew"],
                        capture_output=True, text=True)
    comprobar("--permitir deja pasar una constante declarada",
              p6.returncode == 0, f"{p6.returncode} / {p6.stderr[:200]}")

    # ── la puerta: el porcentaje y su denominador ─────────────────────────
    p7 = subprocess.run([sys.executable, HERRAMIENTA, tmp],
                        capture_output=True, text=True)
    comprobar("la puerta cuenta consulta Y estado vivo",
              "por consulta y" in p7.stdout and "estado vivo" in p7.stdout,
              p7.stdout[:700])
    comprobar("y avisa de que el estado vivo se pierde al reiniciar",
              "se pierden al reiniciar" in p7.stdout, p7.stdout[:900])
    comprobar("el informe da el número de la puerta",
              "PUERTA DE LA ETAPA 1" in p7.stdout, p7.stdout[:300])
    comprobar("y dice cuántas quedaron sin clasificar",
              "sin clasificar" in p7.stdout, p7.stdout[:600])
    comprobar("y dice qué no mide",
              "Lo que esto NO mide" in p7.stdout, p7.stdout[-300:])

    # ── un directorio vacío no inventa un porcentaje ──────────────────────
    vacio = tempfile.mkdtemp(prefix="prueba-origen-vacio-")
    p8 = subprocess.run([sys.executable, HERRAMIENTA, vacio],
                        capture_output=True, text=True)
    comprobar("sin rutas, el número de la puerta es NO SÉ",
              "NO SÉ" in p8.stdout and "PUERTA DE LA ETAPA 1" not in p8.stdout,
              p8.stdout[:400])

    print(f"{HECHAS} comprobaciones, {len(FALLOS)} fallos")
    for f in FALLOS:
        print(f"  FALLO {f}")
    return 1 if FALLOS else 0


def test_el_medidor_acierta_en_los_casos_conocidos():
    """
    La herramienta que mide si los paneles son reales tiene que acertar en
    casos donde la respuesta se sabe. Un medidor equivocado manda el programa
    por el camino que no es: su primera version decia «100% verdadero» porque
    contaba el propio decorador @router.get como una consulta, y daba por real
    el unico POST que la interfaz llama porque `task.get(...)` parecia HTTP.
    """
    assert main() == 0, "el medidor fallo en sus propios casos conocidos"


if __name__ == "__main__":
    sys.exit(main())
