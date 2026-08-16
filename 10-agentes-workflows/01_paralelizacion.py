"""N tareas independientes a la vez. Lo que gano es latencia."""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.client import MODEL, get_async_client
from shared.utils import console

client = get_async_client()

CODIGO = '''
def procesar_pagos(pedidos):
    total = 0
    for p in pedidos:
        if p["estado"] == "pendiente":
            total += p["importe"] * 1.21
            p["estado"] = "cobrado"
            db.execute(f"UPDATE pedidos SET estado='cobrado' WHERE id={p['id']}")
    return total
'''

REVISORES = {
    "Seguridad": "Revisa exclusivamente vulnerabilidades de seguridad.",
    "Corrección": "Revisa exclusivamente bugs de lógica y casos límite.",
    "Rendimiento": "Revisa exclusivamente problemas de rendimiento.",
    "Estilo": "Revisa exclusivamente legibilidad y convenciones de Python.",
}


async def revisar(nombre: str, instruccion: str) -> tuple[str, str]:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=f"{instruccion} Máximo tres hallazgos, uno por línea. Si no hay, dilo.",
        messages=[{"role": "user", "content": f"```python\n{CODIGO}\n```"}],
    )
    texto = "".join(b.text for b in response.content if b.type == "text")
    return nombre, texto


async def main() -> None:
    inicio = time.perf_counter()
    resultados = await asyncio.gather(
        *(revisar(n, i) for n, i in REVISORES.items())
    )
    duracion = time.perf_counter() - inicio

    for nombre, hallazgos in resultados:
        console.print(f"\n[bold cyan]{nombre}[/bold cyan]")
        console.print(hallazgos)

    console.print(
        f"\n[dim]{len(REVISORES)} revisiones en {duracion:.1f}s "
        f"(en serie habrían sido ~{duracion * len(REVISORES):.0f}s)[/dim]"
    )


if __name__ == "__main__":
    asyncio.run(main())

# Aplica cuando: varias perspectivas sobre el mismo input, el mismo análisis
# sobre N inputs, o votación (misma pregunta varias veces, me quedo con la mayoría).
#
# No aplica si el paso 2 necesita la salida del paso 1: eso es encadenamiento (02_).
#
# Con muchas tareas, meter un asyncio.Semaphore por el rate limit. Para lotes
# grandes sin prisa, la Batches API sale al 50%.
