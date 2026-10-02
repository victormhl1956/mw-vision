# -*- coding: utf-8 -*-
"""
Probe tiene que poder decir «no lo sé», y no puede dar una nota.

Por qué. El informe consolidado de DEEPEX puntúa este repositorio con «Security
100%». Lo que DEEPEX recibe para puntuar es un objeto de metadatos —líneas de
código, cuenta de ficheros por nombre de carpeta y una descripción escrita a
mano— y ni una línea de código; la descripción además declara «FastAPI +
PostgreSQL» y el backend usa SQLite. El 100% se mantuvo durante los ocho meses en
que /ws no autenticaba a nadie.

Dos propiedades hacen que eso no pueda repetirse, y las dos se comprueban aquí:

  · una pregunta que no se pudo contestar sale como SIN CONTESTAR y el código de
    salida lo refleja. Nunca se convierte en un punto a favor.
  · no hay nota global. Una cifra única invita a promediar lo medido con lo no
    medido, y ese promedio ES el 100%.
"""
import json
import os
import re
import subprocess
import sys

import pytest

# backend/tests/ -> backend/ -> la raíz del repo, donde vive probe.py.
BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.dirname(BACKEND)
PROBE = os.path.join(RAIZ, "probe.py")


def _correr(*args):
    return subprocess.run([sys.executable, PROBE, *args],
                          capture_output=True, text=True, cwd=RAIZ)


def test_probe_se_ejecuta_y_contesta_algo():
    p = _correr()
    assert p.returncode in (0, 1, 2), f"{p.returncode} / {p.stderr[:300]}"
    assert "MWH-PROBE" in p.stdout
    assert "CONTESTADA" in p.stdout


def test_una_pregunta_sin_herramienta_sale_sin_contestar():
    """
    La propiedad que a DEEPEX le faltaba. Si falta la batería, Probe no puede
    contestar la primera pregunta — la que encontró VULN-001 — y lo dice.
    """
    p = _correr("--bateria", os.path.join(RAIZ, "no_existe_reachability.py"))
    assert "SIN CONTESTAR" in p.stdout, p.stdout[:600]
    assert "No lo sé" in p.stdout
    assert "NO cuenta como aprobado" in p.stdout


def test_sin_contestar_no_puede_salir_con_cero():
    """
    Un «no lo sé» no puede ser indistinguible de un «todo bien» para quien lea
    sólo el código de salida, que es lo que haría un CI.
    """
    p = _correr("--bateria", os.path.join(RAIZ, "no_existe_reachability.py"))
    assert p.returncode != 0, (
        "Probe salió con 0 teniendo una pregunta sin contestar: así es como un "
        "CI verde esconde que no se midió nada.")


def test_probe_no_da_una_nota_global():
    """
    Ninguna cifra que pretenda resumir el proyecto entero. Esto es una
    comprobación de texto a propósito: es la forma más directa de impedir que
    alguien añada «Overall score» en un mal día.
    """
    p = _correr()
    prohibido = ("overall score", "puntuación global", "nota global:",
                 "score:", "calificación")
    minuscula = p.stdout.lower()
    for frase in prohibido:
        # «sin nota global» y «Sin nota global» están permitidos: son la
        # explicación de por qué no hay nota.
        apariciones = [m.start() for m in re.finditer(re.escape(frase),
                                                      minuscula)]
        for i in apariciones:
            contexto = minuscula[max(0, i - 30):i]
            assert "sin " in contexto or "no hay" in contexto, (
                f"«{frase}» aparece como una nota, no como su negación: "
                f"...{minuscula[max(0, i - 60):i + 60]}...")


def test_cada_cifra_viene_con_su_denominador():
    """
    «47% real» sin decir sobre cuántas, y cuántas quedaron sin clasificar, no es
    una medida: es una impresión con decimales.
    """
    p = _correr("--json")
    datos = json.loads(p.stdout)
    contestadas = [r for r in datos["respuestas"] if r["contestada"]]
    assert contestadas, "ninguna pregunta contestada: no hay nada que comprobar"
    for r in contestadas:
        assert r["cifras"], f"«{r['pregunta']}» no trae ninguna cifra"
        assert r["titular"], f"«{r['pregunta']}» no trae titular"
    # La pregunta del origen del dato es la que lleva porcentaje: su denominador
    # y las no clasificadas tienen que estar explícitos.
    origen = next((r for r in contestadas
                   if "origen" in r["pregunta"].lower() or
                   "de dónde" in r["pregunta"].lower()), None)
    if origen is not None:
        for clave in ("clasificadas", "sin_clasificar_fuera_del_porcentaje"):
            assert clave in origen["cifras"], (
                f"la medida con porcentaje no declara «{clave}»")


def test_probe_dice_lo_que_no_mira():
    """Un informe sin alcance declarado es la mitad de un informe."""
    p = _correr()
    assert "Probe NO mira" in p.stdout, p.stdout[-400:]


# ── Portabilidad: Probe tiene que poder medir otro proyecto, o decir que no ──

def test_probe_apuntado_a_otro_proyecto_no_inventa_veredicto(tmp_path):
    """
    La prueba que de verdad importa para usar Probe en VeraVadis o en los blogs.
    Un proyecto vacío no tiene nada que medir, y eso NO puede salir como un
    aprobado: las cuatro preguntas tienen que quedar sin contestar.
    """
    p = _correr("--proyecto", str(tmp_path))
    assert "SIN CONTESTAR" in p.stdout, p.stdout[:600]
    assert "CONTESTADA]" not in p.stdout.replace("SIN CONTESTAR]", ""), (
        "Probe contestó alguna pregunta sobre un proyecto vacío")
    assert p.returncode == 2, (
        f"salió con {p.returncode}: un proyecto donde no se midió nada no "
        f"puede salir con 0")


def test_el_descubrimiento_no_elige_entre_varios_frontends():
    """
    La lección de los sensores, aplicada a Probe. mw-vision tiene DOS proyectos
    de node con package.json y src/ — CLAUDE_DESKTOP_REVIEW y mw-vision-app — y
    mi primera versión se quedaba con el primero por orden alfabético, que es
    inventar un criterio. Ahora declara la duda y nombra las candidatas.
    """
    p = _correr()  # sin --frontend
    assert "SIN DECIDIR" in p.stdout, p.stdout[:500]
    assert "mw-vision-app" in p.stdout
    # Y con la respuesta dada, mide.
    q = _correr("--frontend", os.path.join(RAIZ, "mw-vision-app"))
    assert "SIN DECIDIR" not in q.stdout
    assert q.stdout.count("[CONTESTADA]") == 4, q.stdout[:800]


def test_un_filtro_que_no_examino_nada_no_es_un_aprobado(tmp_path):
    """
    El falso verde más sutil de hacer una herramienta portable: el medidor del
    frontend busca paneles en components/ y views/. Un proyecto que guarde su
    interfaz en otro sitio daría «0 ficheros inventan cifras», que se lee como
    un aprobado y significa «no miré en ningún sitio».
    """
    (tmp_path / "package.json").write_text('{"name":"x"}', encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    # Un componente fuera de components/ y views/, con una lista de datos
    # dentro: si el filtro lo ignorara en silencio, saldría un 0 limpio.
    (src / "Panel.tsx").write_text(
        "export const filas = [{a:1},{a:2}]\nexport default () => null\n",
        encoding="utf-8")
    p = _correr("--proyecto", str(tmp_path), "--frontend", str(tmp_path))
    bloque = p.stdout.split("¿Se inventa")[-1]
    assert "SIN CONTESTAR" in p.stdout and "no examinó ni un" in bloque, (
        "Probe dio por buena una medición que no examinó ningún fichero:\n" +
        bloque[:500])
