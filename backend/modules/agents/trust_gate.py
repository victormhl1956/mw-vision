"""
La compuerta que conecta la política de confianza de Hydra con los agentes.

Por qué existe. `src/hydra/trust_manager.py` codifica, desde el 2026-02-17, qué
modelo puede tocar qué clase de datos: VULN-007 dejó SENSITIVE y CRITICAL en
modelos locales exclusivamente, y VULN-010 exigió que una denegación por modelo
desconocido se registrara en vez de devolver False en silencio. La política era
correcta. **Ningún módulo del árbol importaba el archivo**, así que no se
aplicaba a nada: la tabla de agentes de `modules/agents/state.py` asignaba
modelos sin pasar por ninguna comprobación.

Este módulo es el cable. Lo llama el arranque de la app, de modo que una
configuración que contradiga la política detiene el servidor en vez de llegar a
producción.

Dos detalles que no son adorno:

  · `TrustManager(audit_logger=None)` era el valor por omisión, así que el
    arreglo de VULN-010 tampoco disparaba aunque el módulo se hubiese
    importado: sin auditor, la denegación seguía siendo silenciosa. Aquí el
    auditor real es obligatorio, no opcional.

  · La sensibilidad de cada agente es una declaración explícita en su
    configuración, con SAFE por omisión. No se deduce del nombre. Mientras
    nadie declare un agente SENSITIVE, la comprobación no cambia nada de lo
    que hay hoy; en cuanto alguien lo declare, la restricción se aplica desde
    el arranque.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Mapping

from src.hydra.trust_manager import TrustManager, TrustLevel
from src.security.audit_logger import get_audit_logger


def _gestor() -> TrustManager:
    # El auditor real, no None: de eso dependía el arreglo de VULN-010.
    return TrustManager(audit_logger=get_audit_logger())


def verificar_agentes(agentes: Mapping[str, object]) -> list[str]:
    """
    Comprueba cada agente configurado contra la política de confianza.

    Devuelve la lista de violaciones en texto legible; vacía si todo cumple.
    No lanza: la decisión de abortar o no es del llamador, que es quien sabe si
    está arrancando el servidor o respondiendo una consulta.
    """
    gestor = _gestor()
    violaciones: list[str] = []

    for clave, agente in agentes.items():
        modelo = getattr(agente, "model", None)
        nombre = getattr(agente, "name", clave)
        sensibilidad = getattr(agente, "sensitivity", "SAFE")
        sensibilidad = getattr(sensibilidad, "value", sensibilidad)

        if not modelo:
            violaciones.append(f"agente {clave} ({nombre}): sin modelo asignado")
            continue

        if not gestor.can_process_fragment(modelo, sensibilidad):
            nivel = TrustManager.MODEL_TRUST_LEVELS.get(modelo)
            if nivel is None:
                # can_process_fragment ya dejó el SECURITY_ALERT en el registro.
                violaciones.append(
                    f"agente {clave} ({nombre}): el modelo {modelo!r} no está en "
                    f"la política de confianza. Un modelo desconocido no se "
                    f"aprueba por omisión; añádelo a MODEL_TRUST_LEVELS con su "
                    f"nivel, o corrige el nombre.")
            else:
                permitidos = gestor.get_allowed_models(sensibilidad) or ["(ninguno)"]
                violaciones.append(
                    f"agente {clave} ({nombre}): declarado {sensibilidad} y "
                    f"asignado a {modelo!r}, que es {nivel.value}. "
                    f"Para {sensibilidad} sólo valen: {', '.join(permitidos)}.")

    return violaciones


def exigir_agentes_confiables(agentes: Mapping[str, object]) -> None:
    """
    Igual que `verificar_agentes`, pero aborta si hay violaciones.

    Falla cerrado a propósito. El precedente es VULN-001: aquel arreglo avisaba
    con un `warnings.warn` y en producción un aviso no va a ninguna parte, así
    que la autenticación quedó medio funcionando durante meses. Negarse a
    arrancar se ve.

    `MW_TRUST_GATE=off` lo degrada a aviso, para el caso en que haya que
    arrancar el servidor con una configuración que todavía no se ha decidido.
    Es una salida explícita y deja su propio rastro.
    """
    violaciones = verificar_agentes(agentes)
    if not violaciones:
        print(f"[trust] {len(agentes)} agente(s) conformes con la política de "
              f"confianza de Hydra")
        return

    detalle = "\n".join(f"  · {v}" for v in violaciones)
    get_audit_logger().log_event(
        event_type="SECURITY_ALERT", actor="trust_gate",
        action="validate_agent_models", resource="modules.agents.state.agents",
        result="DENIED" if os.getenv("MW_TRUST_GATE", "on") != "off" else "WARNED",
        metadata={"violaciones": violaciones},
    )

    if os.getenv("MW_TRUST_GATE", "on") == "off":
        print(f"[trust] AVISO — MW_TRUST_GATE=off, se arranca con "
              f"{len(violaciones)} violación(es):\n{detalle}", file=sys.stderr)
        return

    raise RuntimeError(
        "La configuración de agentes contradice la política de confianza de "
        f"Hydra:\n{detalle}\n"
        "Corrige el modelo o la sensibilidad declarada. Si necesitas arrancar "
        "igual mientras lo decides, pon MW_TRUST_GATE=off en el entorno — queda "
        "registrado en la auditoría."
    )
