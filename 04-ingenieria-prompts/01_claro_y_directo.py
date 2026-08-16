"""Mismo objetivo, dos prompts. La diferencia está en la ambigüedad."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

INFORME = """
Q3 cerró con 2,4 M€ de ingresos, un 12 % por encima de Q2. El churn subió del
3,1 % al 4,8 %, concentrado en el plan Starter. El equipo de ventas cerró 47
cuentas nuevas frente a las 61 del trimestre anterior, aunque el ticket medio
creció un 31 %. El coste de infraestructura subió un 40 % tras la migración.
"""

VAGO = f"Mira este informe y dime qué te parece.\n\n{INFORME}"

CLARO = f"""
Analiza el informe trimestral y responde estas tres preguntas, en este orden:

1. ¿Cuál es la señal más preocupante, y por qué?
2. ¿Qué métrica compensa esa señal?
3. ¿Qué haría falta saber para decidir si actuar?

Una respuesta por pregunta, máximo tres frases cada una. Cita las cifras
concretas del informe. No propongas acciones todavía.

<informe>
{INFORME}
</informe>
"""

print_block("Prompt vago", extract_text(
    client.messages.create(
        model=MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": VAGO}],
    )
), "yellow")

print_block("Prompt claro", extract_text(
    client.messages.create(
        model=MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": CLARO}],
    )
), "green")

# En el claro fijo: tarea, entregable, orden, longitud, exigencia de citar
# cifras y un límite de alcance ("no propongas acciones todavía").
# Son decisiones que alguien tiene que tomar. Si no las tomo yo, las toma el modelo.
