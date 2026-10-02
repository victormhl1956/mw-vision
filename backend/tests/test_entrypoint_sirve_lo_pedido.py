# -*- coding: utf-8 -*-
"""
Lo que la interfaz pide, ¿lo sirve la aplicación que de verdad arranca?

Por qué existe, y es el hallazgo que ninguna de las otras mediciones vio. El
cruce panel-a-panel empareja por camino sobre el CÓDIGO: si algún fichero del
árbol declara `/api/chat/search`, cuenta como servido. Pero mw-vision tiene tres
puntos de entrada que registran routers distintos, y PM2 arranca
`main_modular.py`, que sólo registraba cinco:

    /, /api, /api/agents, /api/crew, /api/security, /health

Seis rutas. El procesador de conversaciones —la memoria que acabo de cablear— y
el de YouTube daban **404 en producción** mientras el código existía, pasaba sus
tests y la interfaz los pedía. Es la clase de defecto de febrero en su versión
más escurridiza: no es que el arreglo no se importe, es que se importa en el
fichero que no arranca.

Lo encontré levantando la aplicación de verdad, no leyendo. Esto lo fija sin
necesidad de levantarla: `TestClient` construye la misma aplicación y su
`openapi()` dice exactamente qué sirve.
"""
import json
import os
import re
import shutil
import subprocess

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(os.path.dirname(BACKEND), "mw-vision-app")
EXTRACTOR = os.path.join(FRONTEND, "tools", "llamadas_ui.mjs")

# Caminos que la interfaz pide y que main_modular NO sirve. Cada línea es una
# pantalla rota en producción, con su consecuencia medida.
#
# Las cuatro son de `src/main.py`, y las cuatro sirven dato inventado —SIMULADO
# o MEMORIA SEMILLA—. Registrarlas en el entrypoint para poner este test verde
# sería meter rutas falsas en producción, que es justo lo contrario de lo que
# busca esta batería. Salen de aquí por una de dos puertas: o la interfaz deja
# de pedirlas, o alguien las implementa contra dato real.
#
# Consecuencia observada en el navegador el 2026-10-02: `crewStore.init()`
# revienta con «Failed to fetch stats», y la cabecera muestra ERROR.
EXENTAS: dict[str, str] = {
    "/api/stats": "sólo en src/main.py, y sirve estadísticas de una semilla de "
                  "tres agentes; su 404 rompe crewStore.init()",
    "/api/routing-history": "sólo en src/main.py, y es SIMULADO",
    "/api/agents/{param}": "sólo en src/main.py, y sirve la misma semilla",
    "/api/agents/{param}/execute": "sólo en src/main.py, y simula el enrutado "
                                   "con random.randint(1, 10)",
}


def _caminos_que_pide_la_interfaz() -> list[str]:
    if shutil.which("node") is None:
        pytest.skip("hace falta node para leer el frontend")
    if not os.path.isdir(os.path.join(FRONTEND, "node_modules", "typescript")):
        pytest.skip("hace falta el typescript del frontend instalado")
    p = subprocess.run(["node", EXTRACTOR, os.path.join(FRONTEND, "src")],
                       capture_output=True, text=True, cwd=FRONTEND)
    assert p.returncode == 0, p.stderr[:500]
    d = json.loads(p.stdout)
    # Sólo las HTTP: el WebSocket no sale en openapi.
    return sorted({l["camino"] for l in d["llamadas"] if l["clase"] == "http"})


def _caminos_que_sirve_el_entrypoint() -> set[str]:
    from fastapi.testclient import TestClient

    import main_modular
    esquema = TestClient(main_modular.app).get("/openapi.json").json()
    return set(esquema.get("paths", {}))


def _encaja(pedido: str, servidos: set[str]) -> bool:
    """
    `/api/agents/{param}` encaja con `/api/agents/{agent_id}`: el nombre del
    parámetro es del backend, el hueco es lo que el frontend sabe.
    """
    if pedido in servidos:
        return True
    patron = re.compile(
        "^" + re.sub(r"\{[^}]+\}", r"\\{[^}]+\\}", re.escape(pedido)
                     .replace(r"\{", "{").replace(r"\}", "}")) + "$")
    return any(patron.match(s) for s in servidos)


def test_el_entrypoint_de_pm2_sirve_todo_lo_que_la_interfaz_pide(monkeypatch):
    monkeypatch.setenv("HYDRA_SECRET_KEY", "0123456789abcdef0123456789abcdef")
    pedidos = _caminos_que_pide_la_interfaz()
    assert pedidos, "el extractor no encontró ninguna llamada HTTP"
    servidos = _caminos_que_sirve_el_entrypoint()

    faltan = [c for c in pedidos
              if c not in EXENTAS and not _encaja(c, servidos)]
    assert not faltan, (
        "main_modular.py —lo que arranca PM2— NO sirve rutas que la interfaz "
        "pide; en producción son 404 aunque el código exista y sus tests "
        "pasen:\n" + "\n".join(f"  {c}" for c in faltan) +
        "\n\nSirve: " + ", ".join(sorted(servidos)))


def test_la_memoria_esta_registrada_en_el_entrypoint(monkeypatch):
    """
    Por su nombre, porque es lo que se acaba de cablear y lo que más fácil se
    cae: el router del chat se registraba en main.py y no en main_modular.py.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", "0123456789abcdef0123456789abcdef")
    servidos = _caminos_que_sirve_el_entrypoint()
    for camino in ("/api/chat/conversations", "/api/chat/search",
                   "/api/chat/ingest"):
        assert camino in servidos, (
            f"{camino} no está en el entrypoint de PM2: la memoria vuelve a ser "
            f"404 en producción. Sirve: {sorted(servidos)}")


@pytest.mark.parametrize("camino,motivo", sorted(EXENTAS.items()))
def test_cada_exencion_sigue_siendo_cierta(camino, motivo, monkeypatch):
    """
    Una exención que ya no hace falta es una mentira que se queda. Si alguien
    registra la ruta o la interfaz deja de pedirla, esto lo dice y se borra la
    línea.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", "0123456789abcdef0123456789abcdef")
    assert len(motivo) > 25, f"{camino}: el motivo no explica la consecuencia"
    servidos = _caminos_que_sirve_el_entrypoint()
    if _encaja(camino, servidos):
        pytest.fail(
            f"{camino} YA lo sirve el entrypoint: borra su línea de EXENTAS.")
    if camino not in _caminos_que_pide_la_interfaz():
        pytest.fail(
            f"la interfaz ya no pide {camino}: borra su línea de EXENTAS.")


def test_la_comprobacion_puede_fallar(monkeypatch):
    """
    El contrapeso. Si el extractor se rompe y devuelve cero llamadas, el primer
    test pasaría con una lista vacía; y si `_encaja` encajara con todo, también.
    Esto exige que un camino inventado NO encaje.
    """
    monkeypatch.setenv("HYDRA_SECRET_KEY", "0123456789abcdef0123456789abcdef")
    servidos = _caminos_que_sirve_el_entrypoint()
    assert not _encaja("/api/esto-no-existe", servidos)
    assert not _encaja("/api/chat/{param}/inventado", servidos)
    # Y uno que sí tiene que encajar, con parámetro de nombre distinto.
    assert _encaja("/api/chat/conversations/{param}", servidos)
