"""LLM-as-judge: un modelo puntúa cada salida contra la rúbrica."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, Field

from shared import MODEL, get_client
from shared.utils import console

client = get_client()
DATA = Path(__file__).parent / "data"


class Veredicto(BaseModel):
    puntuacion: int = Field(description="De 1 a 5, donde 5 cumple el criterio por completo")
    cumple: bool
    justificacion: str = Field(description="Una o dos frases, citando la evidencia")


RUBRICA_JUEZ = """
Eres un evaluador estricto. Puntúa la salida contra el criterio de éxito.

<input_original>
{input}
</input_original>

<criterio_de_exito>
{criterio}
</criterio_de_exito>

<salida_a_evaluar>
{salida}
</salida_a_evaluar>

Puntúa solo contra el criterio indicado. No premies cosas que el criterio no
pide. Si la salida es correcta pero incumple el formato, no cumple.
"""


def graduar(caso: dict) -> dict:
    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": RUBRICA_JUEZ.format(
                    input=caso["input"],
                    criterio=caso["criterio_exito"],
                    salida=caso["salida"],
                ),
            }
        ],
        output_format=Veredicto,
    )
    return {"id": caso["id"], **response.parsed_output.model_dump()}


def main() -> None:
    archivo = DATA / "salidas_v1.json"
    datos = json.loads(archivo.read_text(encoding="utf-8"))

    veredictos = [graduar(caso) for caso in datos["resultados"]]

    aprobados = sum(1 for v in veredictos if v["cumple"])
    media = sum(v["puntuacion"] for v in veredictos) / len(veredictos)

    console.print(f"\n[bold]Resultados — prompt {datos['version_prompt']}[/bold]")
    console.print(f"  Aprobados : {aprobados}/{len(veredictos)}")
    console.print(f"  Media     : {media:.2f}/5\n")

    for v in veredictos:
        marca = "[green]OK[/green]" if v["cumple"] else "[red]FALLO[/red]"
        console.print(f"  {marca} {v['id']} ({v['puntuacion']}/5) — {v['justificacion']}")

    (DATA / "veredictos_v1.json").write_text(
        json.dumps(veredictos, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()

# Cosas a vigilar del juez:
# - Tiende a ser generoso. Por eso le exijo justificación con evidencia.
# - Si el juez es el mismo modelo que generó la salida, hay sesgo a favor.
# - Si le digo "reporta solo lo importante", filtra literal y el recall medido
#   baja aunque sí haya detectado los fallos. Mejor que reporte todo y filtro yo.
# - Antes de fiarme: puntúo 10 casos a mano y compruebo si coincide conmigo.
