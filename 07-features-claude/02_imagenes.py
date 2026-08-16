"""Imágenes por URL y por base64."""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block, print_usage
from shared.utils import console

client = get_client()
ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)


response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {
                "type": "url",
                "url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
            }},
            {"type": "text", "text": "Describe esta imagen en una frase."},
        ],
    }],
)
print_block("Imagen por URL", extract_text(response))
print_usage(response)


imagenes = list(ASSETS.glob("*.png")) + list(ASSETS.glob("*.jpg"))

if not imagenes:
    console.print(f"\n[yellow]Pon una imagen en {ASSETS} para probar base64.[/yellow]")
else:
    ruta = imagenes[0]
    media_type = "image/png" if ruta.suffix == ".png" else "image/jpeg"
    datos = base64.standard_b64encode(ruta.read_bytes()).decode("utf-8")

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64", "media_type": media_type, "data": datos,
                }},
                {"type": "text", "text": "¿Qué ves? Sé específico."},
            ],
        }],
    )
    print_block(f"Imagen base64 ({ruta.name})", extract_text(response))
    print_usage(response)

# Formatos: JPEG, PNG, GIF, WebP. Máximo 2576 px en el lado largo.
# Las coordenadas que devuelve mapean 1:1 con los píxeles, sin factor de escala.
#
# Coste: una imagen a resolución completa puede gastar ~4784 tokens, unas 3x más
# que en modelos anteriores. Si no necesito ese detalle, reducir antes de enviar.
#
# El bloque de imagen va ANTES del de texto.
# Para consultas repetidas sobre la misma imagen: Files API y referenciar file_id.
