"""PDF inline vs Files API (subir una vez, consultar muchas)."""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block, print_usage
from shared.utils import console

client = get_client()
ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

pdfs = list(ASSETS.glob("*.pdf"))
if not pdfs:
    console.print(f"[yellow]Pon un PDF en {ASSETS} para ejecutar esto.[/yellow]")
    sys.exit(0)

ruta = pdfs[0]
console.print(f"PDF: {ruta.name} ({ruta.stat().st_size // 1024} KB)\n")


datos = base64.standard_b64encode(ruta.read_bytes()).decode("utf-8")

response = client.messages.create(
    model=MODEL,
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {
                "type": "base64", "media_type": "application/pdf", "data": datos,
            }},
            {"type": "text", "text": "Resume este documento en 5 bullets."},
        ],
    }],
)
print_block("PDF inline (base64)", extract_text(response))
print_usage(response)


# Files API: evito reenviar megabytes en cada petición.
subido = client.beta.files.upload(
    file=(ruta.name, ruta.open("rb"), "application/pdf"),
    betas=["files-api-2025-04-14"],
)
console.print(f"\n[green]Subido:[/green] {subido.id} ({subido.size_bytes} bytes)\n")

PREGUNTAS = [
    "¿Cuál es la conclusión principal?",
    "¿Qué cifras concretas aparecen?",
]

for pregunta in PREGUNTAS:
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=2048,
        betas=["files-api-2025-04-14"],
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": pregunta},
                {"type": "document", "source": {"type": "file", "file_id": subido.id}},
            ],
        }],
    )
    print_block(pregunta, extract_text(response))

client.beta.files.delete(subido.id, betas=["files-api-2025-04-14"])
console.print("[dim]Archivo eliminado.[/dim]")

# Inline: 32 MB por petición, 600 páginas. El base64 sin saltos de línea.
# Files API: 500 MB por archivo, 100 GB por organización. Subir/listar/borrar es
# gratis; el contenido usado en un mensaje se factura como tokens de entrada.
# No está disponible en Bedrock ni Vertex AI.
