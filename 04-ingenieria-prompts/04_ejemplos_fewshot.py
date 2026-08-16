"""Los ejemplos son la señal más fuerte del prompt."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

ENTRADA = "El botón de exportar no hace nada en Firefox, en Chrome sí funciona."


ZERO_SHOT = f"""
Convierte el reporte del usuario en un título de issue técnico.

Reporte: {ENTRADA}
"""

FEW_SHOT = f"""
Convierte el reporte del usuario en un título de issue técnico.

<ejemplos>
<ejemplo>
  <reporte>La app se cierra sola cuando subo una foto grande</reporte>
  <titulo>Crash al subir imágenes por encima del límite de tamaño</titulo>
</ejemplo>
<ejemplo>
  <reporte>No me llegan los emails de recuperación de contraseña</reporte>
  <titulo>Los emails de reset de contraseña no se entregan</titulo>
</ejemplo>
<ejemplo>
  <reporte>El buscador tarda muchísimo desde ayer por la tarde</reporte>
  <titulo>Degradación de latencia en el endpoint de búsqueda</titulo>
</ejemplo>
</ejemplos>

Reporte: {ENTRADA}
"""

print_block("Zero-shot", extract_text(
    client.messages.create(
        model=MODEL, max_tokens=256,
        messages=[{"role": "user", "content": ZERO_SHOT}],
    )
), "yellow")

print_block("Few-shot", extract_text(
    client.messages.create(
        model=MODEL, max_tokens=256,
        messages=[{"role": "user", "content": FEW_SHOT}],
    )
), "green")

# Al elegir ejemplos:
# - Variados. Si los tres son de crashes, la salida tira a crashes.
# - Con la longitud y el registro que quiero, porque el modelo los imita.
# - Al menos uno difícil; los fáciles enseñan poco.
# - Tres o cuatro bastan. Un único ejemplo "de oro" congela ese formato.
#
# Si vienen de un modelo anterior, revisarlos al migrar: pueden estar enseñando
# un formato que ya no quiero.
