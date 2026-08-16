"""Ejecuto el prompt bajo evaluación sobre todo el dataset, en paralelo."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.client import MODEL_FAST, get_async_client
from shared.utils import console

DATA = Path(__file__).parent / "data"
CONCURRENCIA = 5  # ajustar según mi rate limit


# Esta es la variable que itero entre versiones.
PROMPT_BAJO_EVAL = """
Clasifica el siguiente ticket de soporte.

Devuelve únicamente un objeto JSON con las claves:
  categoria (string), prioridad ("baja"|"media"|"alta"), escalar (boolean).

Ticket:
{input}
"""

VERSION_PROMPT = "v1"


async def ejecutar_caso(client, semaforo, caso: dict) -> dict:
    async with semaforo:
        response = await client.messages.create(
            model=MODEL_FAST,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": PROMPT_BAJO_EVAL.format(input=caso["input"])}
            ],
        )
        salida = "".join(b.text for b in response.content if b.type == "text")

    return {
        "id": caso["id"],
        "input": caso["input"],
        "criterio_exito": caso["criterio_exito"],
        "salida": salida,
        "tokens_salida": response.usage.output_tokens,
    }


async def main() -> None:
    dataset = json.loads((DATA / "dataset.json").read_text(encoding="utf-8"))
    casos = dataset["casos"]

    client = get_async_client()
    semaforo = asyncio.Semaphore(CONCURRENCIA)

    console.print(f"Ejecutando {len(casos)} casos con concurrencia {CONCURRENCIA}...")
    resultados = await asyncio.gather(
        *(ejecutar_caso(client, semaforo, c) for c in casos)
    )

    destino = DATA / f"salidas_{VERSION_PROMPT}.json"
    destino.write_text(
        json.dumps(
            {"version_prompt": VERSION_PROMPT, "modelo": MODEL_FAST, "resultados": resultados},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    console.print(f"[green]Salidas guardadas en {destino}[/green]")


if __name__ == "__main__":
    asyncio.run(main())

# Guardo version_prompt y modelo en el archivo: sin eso no puedo comparar v1 vs v2.
# Para tandas grandes, la Batches API sale al 50%.
