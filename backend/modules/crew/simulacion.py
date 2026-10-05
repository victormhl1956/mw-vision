# -*- coding: utf-8 -*-
"""
Whether the agent-activity simulator may run, in one place.

Why this exists. `simulate_agent_updates()` generates token counts with
`random.randint(100, 600)`, multiplies them by a hardcoded cost table and writes
the result into `crew_state.total_cost` — which is then compared against
`crew_state.budget_limit` to stop the crew. Both entry points launched it
unconditionally in their lifespan, so every cost figure the command centre
displayed in production was a dice roll, and so was the budget guard that acted
on it.

Simulated state is worse than a constant. A constant is visible at a glance; a
simulator produces numbers that drift plausibly and are indistinguishable from
telemetry. That is precisely what makes an interface look alive when it is not.

So the simulator is now off unless someone asks for it, and when it is on, that
fact is reported by the API instead of being inferred from the numbers. Turning
it off does not break a demo: `MW_SIMULADOR=on` brings it back, and the
`simulated` flag lets the interface say so out loud.
"""

import os

VARIABLE = "MW_SIMULADOR"
_ENCENDIDO = {"on", "1", "true", "yes", "si", "sí"}


def simulacion_activa() -> bool:
    """
    True only when someone deliberately asked for simulated activity.

    Anything other than an explicit affirmative is off, including an empty
    string and a typo: the safe answer to "should this invent numbers?" is no.
    """
    return os.getenv(VARIABLE, "").strip().lower() in _ENCENDIDO


def aviso_simulacion() -> str:
    """One line for the startup log, whichever way it goes."""
    if simulacion_activa():
        return (f"[crew] {VARIABLE}=on: la actividad de los agentes y el coste "
                f"los genera un simulador. Los números NO son reales.")
    return (f"[crew] simulador apagado. Los contadores de coste quedan a cero "
            f"hasta que haya trabajo real; para volver a simular, "
            f"{VARIABLE}=on.")
