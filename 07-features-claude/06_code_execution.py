"""Code execution: escribe y ejecuta Python en un contenedor de Anthropic."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client
from shared.utils import console

client = get_client()

SALIDAS = Path(__file__).parent / "salidas"
SALIDAS.mkdir(exist_ok=True)

CODE_EXECUTION = {"type": "code_execution_20260521", "name": "code_execution"}


response = client.messages.create(
    model=MODEL,
    max_tokens=4096,
    tools=[CODE_EXECUTION],
    messages=[{
        "role": "user",
        "content": (
            "Calcula la media, la mediana y la desviación típica de "
            "[12, 7, 3, 21, 15, 8, 19, 4, 11, 16]. Enséñame el código."
        ),
    }],
)

for bloque in response.content:
    if bloque.type == "text":
        console.print(bloque.text)
    elif bloque.type == "server_tool_use":
        console.print(f"\n[dim]ejecutando: {bloque.name}[/dim]")
    elif bloque.type == "bash_code_execution_tool_result":
        resultado = bloque.content
        if resultado.type == "bash_code_execution_result":
            if resultado.return_code == 0:
                console.print(f"[green]stdout:[/green]\n{resultado.stdout}")
            else:
                console.print(f"[red]stderr:[/red]\n{resultado.stderr}")
        else:
            console.print(f"[red]error de herramienta: {resultado.error_code}[/red]")


console.print("\n[bold]Análisis de un CSV[/bold]")

csv = SALIDAS / "ventas.csv"
csv.write_text(
    "mes,ingresos,pedidos\n"
    "enero,42000,310\nfebrero,38500,287\nmarzo,51200,402\n"
    "abril,47800,371\nmayo,55100,428\njunio,49300,395\n",
    encoding="utf-8",
)

subido = client.beta.files.upload(
    file=(csv.name, csv.open("rb"), "text/csv"),
    betas=["files-api-2025-04-14"],
)

response = client.messages.create(
    model=MODEL,
    max_tokens=8000,
    extra_headers={"anthropic-beta": "files-api-2025-04-14"},
    tools=[CODE_EXECUTION],
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": (
                "Analiza estas ventas: calcula el ticket medio por mes y genera "
                "un gráfico de líneas con la evolución de ingresos. Guárdalo como PNG."
            )},
            {"type": "container_upload", "file_id": subido.id},
        ],
    }],
)


for bloque in response.content:
    if bloque.type == "text":
        console.print(bloque.text)
    elif bloque.type == "bash_code_execution_tool_result":
        resultado = bloque.content
        if resultado.type != "bash_code_execution_result" or not resultado.content:
            continue
        for ref in resultado.content:
            if ref.type != "bash_code_execution_output":
                continue
            meta = client.beta.files.retrieve_metadata(ref.file_id)
            contenido = client.beta.files.download(ref.file_id)

            # basename obligatorio: el nombre viene del contenedor.
            nombre = os.path.basename(meta.filename)
            if not nombre or nombre in (".", ".."):
                continue
            destino = SALIDAS / nombre
            contenido.write_to_file(str(destino))
            console.print(f"[green]guardado:[/green] {destino}")

client.beta.files.delete(subido.id, betas=["files-api-2025-04-14"])

# Contenedor: 1 CPU, 5 GiB RAM, 5 GiB disco, SIN internet.
# Python 3.11 con pandas, numpy, scipy, sklearn, matplotlib, openpyxl, pillow,
# pypdf, python-docx, python-pptx, sympy... y pip disponible en runtime.
#
# Los contenedores persisten 30 días y se pueden reutilizar para conservar
# archivos y paquetes:
#   container_id = response.container.id
#   client.messages.create(container=container_id, ...)
#
# Coste: gratis junto a web search / web fetch; si no, 0,05 $/hora tras 1.550
# horas gratuitas al mes por organización.
