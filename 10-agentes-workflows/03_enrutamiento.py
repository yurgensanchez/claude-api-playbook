"""Un clasificador barato decide la ruta. Lo que gano es coste."""

import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel

from shared import extract_text, get_client
from shared.client import MODEL, MODEL_FAST
from shared.utils import console

client = get_client()


class Ruta(BaseModel):
    categoria: Literal["facturacion", "tecnico", "comercial", "otro"]
    urgencia: Literal["baja", "media", "alta"]
    justificacion: str


def enrutar(consulta: str) -> Ruta:
    return client.messages.parse(
        model=MODEL_FAST,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                "Clasifica esta consulta de cliente por categoría y urgencia.\n\n"
                f"<consulta>{consulta}</consulta>"
            ),
        }],
        output_format=Ruta,
    ).parsed_output


RUTAS = {
    "facturacion": {
        "modelo": MODEL_FAST,
        "system": (
            "Eres del equipo de facturación. Respondes sobre cobros, facturas y "
            "reembolsos. Nunca prometes un reembolso sin verificar la política."
        ),
    },
    "tecnico": {
        "modelo": MODEL,   # el caro: aquí sí hace falta razonar
        "system": (
            "Eres ingeniero de soporte. Diagnosticas antes de proponer solución. "
            "Si faltan datos para diagnosticar, los pides en vez de adivinar."
        ),
    },
    "comercial": {
        "modelo": MODEL_FAST,
        "system": "Eres del equipo comercial. Cualificas y propones siguiente paso.",
    },
    "otro": {
        "modelo": MODEL_FAST,
        "system": "Responde brevemente y redirige al canal adecuado.",
    },
}


def atender(consulta: str) -> str:
    ruta = enrutar(consulta)
    config = RUTAS[ruta.categoria]

    console.print(
        f"  [dim]-> {ruta.categoria} / urgencia {ruta.urgencia} "
        f"/ modelo {config['modelo']}[/dim]"
    )

    response = client.messages.create(
        model=config["modelo"],
        max_tokens=1024,
        system=config["system"],
        messages=[{"role": "user", "content": consulta}],
    )
    return extract_text(response)


if __name__ == "__main__":
    CONSULTAS = [
        "Me habéis cobrado dos veces la cuota de marzo.",
        "La API me devuelve 429 aunque estoy muy por debajo de mi límite. "
        "Empezó ayer tras desplegar un cambio en el cliente.",
        "¿Tenéis descuento por volumen a partir de 50 licencias?",
    ]

    for consulta in CONSULTAS:
        console.print(f"\n[bold green]Consulta:[/bold green] {consulta}")
        console.print(f"[cyan]{atender(consulta)}[/cyan]")

# Sin router, el 100% va al modelo caro. Con router, solo las técnicas.
# Si el 70% de mis consultas son facturación y comercial, el ahorro es real y la
# calidad no baja: esas rutas no necesitaban el modelo grande.
#
# Requisito: el router tiene que acertar. Evaluarlo por separado (módulo 03) con
# un dataset de consultas etiquetadas antes de fiarme.
