"""
Crew API Router
"""

from fastapi import APIRouter

from modules.crew.simulacion import simulacion_activa
from modules.crew.state import crew_state


router = APIRouter(prefix="/api")


@router.get("/crew")
async def get_crew_state():
    # El coste viaja con la etiqueta de si lo generó un simulador. Sin ella,
    # un número plausible es indistinguible de uno medido, y es el simulador
    # el que hacía que esta pantalla pareciera viva.
    return {**crew_state.model_dump(), "datos_simulados": simulacion_activa()}
