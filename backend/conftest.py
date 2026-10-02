# -*- coding: utf-8 -*-
"""
Configuración común de la batería.

Lo único que hace, y hace falta: apartar la memoria del proyecto de los tests.
`modules/chat_processor/router.py` guardaba en `backend/chat_processor.db` por
constante de módulo, así que cada ejecución de la batería escribía ahí. De las
26 conversaciones que había el 2026-10-02, 25 eran «Conversación de prueba» de
mis propias ejecuciones: nadie podía distinguir lo que se decidió de lo que se
comprobó.

Se aparta aquí y no en cada test porque el router lee la variable AL IMPORTARSE,
y conftest se ejecuta antes que cualquier import de test.
"""
import os
import tempfile

_MEMORIA_DE_PRUEBA = os.path.join(
    tempfile.mkdtemp(prefix="mw-chat-tests-"), "chat_processor.db")
os.environ["MW_CHAT_DB"] = _MEMORIA_DE_PRUEBA
