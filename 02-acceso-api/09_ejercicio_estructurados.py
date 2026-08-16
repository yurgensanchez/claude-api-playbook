"""EJERCICIO — extraer datos estructurados de reseñas.

Lo que tengo que sacar:
  1. Modelo Pydantic con puntuación (1-5), sentimiento, aspectos positivos,
     aspectos negativos y si recomendaría.
  2. Las tres reseñas procesadas.
  3. Tabla resumen.
  4. Media de puntuación y aspectos negativos más repetidos.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel

from shared import MODEL, get_client
from shared.utils import console

client = get_client()

RESENAS = [
    "Llegó dos días tarde y la caja venía abollada, pero el producto funciona "
    "perfecto y el precio es imbatible. Lo volvería a comprar.",

    "Se rompió a la semana. Atención al cliente no responde. Un desastre.",

    "Cumple lo que promete. La batería dura menos de lo anunciado y la app es "
    "regular, aunque la construcción es sólida. Está bien por lo que cuesta.",
]


# TODO definir el modelo
class Resena(BaseModel):
    pass


def analizar(texto: str) -> Resena:
    # TODO messages.parse con output_format=Resena
    raise NotImplementedError


if __name__ == "__main__":
    resultados = [analizar(r) for r in RESENAS]

    # TODO tabla resumen (rich.table.Table)
    for r in resultados:
        console.print(r)

    # TODO media y aspectos negativos más frecuentes

# Para el sentimiento uso Literal, no str libre — Pydantic lo convierte en enum
# y el modelo no puede salirse:
#   sentimiento: Literal["positivo", "neutro", "negativo"]
