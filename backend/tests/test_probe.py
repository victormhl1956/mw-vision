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
