"""Un ciclo completo paso a paso, sin bucle, para ver la mecánica."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import TODAS_LAS_TOOLS, ejecutar_tool  # noqa: E402

client = get_client()

messages = [
    {"role": "user", "content": "¿En qué estado está mi pedido PED-5502?"}
]

# 1. El modelo pide la herramienta.
response = client.messages.create(
    model=MODEL, max_tokens=2048, tools=TODAS_LAS_TOOLS, messages=messages
)
print_block("Paso 1 — stop_reason", response.stop_reason)

# 2. Guardo response.content ENTERO, no extract_text(): si pierdo los bloques
#    tool_use, la API rechaza el tool_result del paso 4.
messages.append({"role": "assistant", "content": response.content})

# 3. Ejecuto cada herramienta pedida.
tool_results = []
for bloque in response.content:
    if bloque.type != "tool_use":
        continue

    resultado, es_error = ejecutar_tool(bloque.name, bloque.input)
    print_block(
        f"Paso 3 — ejecutando {bloque.name}",
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str),
        "red" if es_error else "green",
    )

    tool_results.append({
        "type": "tool_result",
        "tool_use_id": bloque.id,
        "content": json.dumps(resultado, ensure_ascii=False, default=str),
        "is_error": es_error,
    })

# 4. Todos los resultados en UN solo mensaje user.
messages.append({"role": "user", "content": tool_results})

# 5. Respuesta final.
final = client.messages.create(
    model=MODEL, max_tokens=2048, tools=TODAS_LAS_TOOLS, messages=messages
)
print_block("Paso 5 — respuesta final", extract_text(final))
print(f"stop_reason: {final.stop_reason}")

# Errores que ya me han costado tiempo:
# - guardar extract_text() en vez de response.content -> 400
# - olvidar un tool_result cuando hubo varios tool_use -> 400
# - mandar los tool_result en mensajes separados -> le enseño a no paralelizar
# - tragarme el error de la herramienta -> el modelo no puede corregir lo que no ve
