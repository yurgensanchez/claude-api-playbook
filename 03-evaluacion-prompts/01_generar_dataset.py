"""Genero el dataset de evaluación con el modelo y lo guardo en data/."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel

from shared import get_client
from shared.client import MODEL
from shared.utils import console

client = get_client()
DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)


class CasoDePrueba(BaseModel):
    id: str
    input: str
    criterio_exito: str
    dificultad: str  # facil | media | dificil


class Dataset(BaseModel):
    casos: list[CasoDePrueba]


TAREA = (
    "Un prompt que recibe la descripción de un ticket de soporte y devuelve "
    "un JSON con: categoria, prioridad (baja/media/alta) y si requiere "
    "escalado a ingeniería."
)

GENERADOR = f"""
Vas a construir un dataset de evaluación para esta tarea:

<tarea>
{TAREA}
</tarea>

Genera 12 casos de prueba. Cubre:
- casos fáciles y sin ambigüedad
- casos ambiguos donde la categoría no es obvia
- casos límite: input muy corto, input contradictorio, input fuera de dominio

Para cada caso, el criterio de éxito debe ser verificable — describe qué tiene
que contener la salida, no si "está bien".
"""


def main() -> None:
    response = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": GENERADOR}],
        output_format=Dataset,
    )

    dataset = response.parsed_output
    destino = DATA / "dataset.json"
    destino.write_text(
        json.dumps(dataset.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    console.print(f"[green]{len(dataset.casos)} casos guardados en {destino}[/green]")
    for caso in dataset.casos[:3]:
        console.print(f"  [{caso.dificultad}] {caso.input[:70]}...")


if __name__ == "__main__":
    main()

# Esto es un punto de partida, no el dataset final: hay que revisarlo a mano.
# El modelo genera casos demasiado parecidos entre sí y esquiva los incómodos.
# Los que de verdad valen salen de fallos reales en producción.
