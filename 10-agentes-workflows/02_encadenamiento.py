"""Cada paso alimenta al siguiente y hace UNA cosa."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel

from shared import extract_text, get_client
from shared.client import MODEL, MODEL_FAST
from shared.utils import console

client = get_client()

TRANSCRIPCION = """
[reunión de producto, 12 min]
Ana: el churn del plan Starter se ha ido al 4,8%. Hay que hacer algo este trimestre.
Luis: la mayoría se va en el mes 2. Creo que es onboarding, no precio.
Ana: ¿tenemos datos? Necesito saber si es onboarding antes de tocar nada.
Luis: puedo sacar el funnel de activación para el viernes.
Marta: si es onboarding, propongo un checklist guiado. Lo tengo diseñado.
Ana: vale. Luis saca los datos el viernes, y decidimos el lunes. Marta, no
     empieces a implementar hasta entonces.
Marta: entendido. Dejo el diseño listo por si acaso.
"""


class Extraccion(BaseModel):
    decisiones: list[str]
    tareas: list[str]
    preguntas_abiertas: list[str]


def paso_1_extraer(texto: str) -> Extraccion:
    # Extraer es mecánico: aquí no necesito el modelo caro.
    return client.messages.parse(
        model=MODEL_FAST,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Extrae decisiones, tareas y preguntas abiertas:\n\n{texto}",
        }],
        output_format=Extraccion,
    ).parsed_output


class Tarea(BaseModel):
    descripcion: str
    responsable: str
    fecha_limite: str
    bloqueada_por: str


class Plan(BaseModel):
    tareas: list[Tarea]


def paso_2_asignar(extraccion: Extraccion, texto: str) -> Plan:
    return client.messages.parse(
        model=MODEL,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": (
                f"<transcripcion>{texto}</transcripcion>\n\n"
                f"<tareas_detectadas>{extraccion.tareas}</tareas_detectadas>\n\n"
                "Para cada tarea, identifica responsable, fecha límite y de qué "
                "depende. Usa 'sin definir' cuando la transcripción no lo diga: "
                "no lo inventes."
            ),
        }],
        output_format=Plan,
    ).parsed_output


def paso_3_redactar(plan: Plan) -> str:
    lineas = "\n".join(
        f"- {t.descripcion} | {t.responsable} | {t.fecha_limite} | depende de: {t.bloqueada_por}"
        for t in plan.tareas
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": (
                f"Convierte este plan en un email de seguimiento para el equipo.\n"
                f"Tono directo, sin relleno. Máximo 150 palabras.\n\n{lineas}"
            ),
        }],
    )
    return extract_text(response)


if __name__ == "__main__":
    console.print("[bold]Paso 1 — extracción[/bold]")
    extraccion = paso_1_extraer(TRANSCRIPCION)
    console.print(extraccion)

    console.print("\n[bold]Paso 2 — asignación[/bold]")
    plan = paso_2_asignar(extraccion, TRANSCRIPCION)
    for t in plan.tareas:
        console.print(f"  {t.descripcion} -> {t.responsable} ({t.fecha_limite})")

    console.print("\n[bold]Paso 3 — redacción[/bold]")
    console.print(paso_3_redactar(plan))

# Por qué encadeno en vez de una sola llamada:
#   1. Cada paso se evalúa por separado: sé CUÁL falla.
#   2. Modelos distintos por paso: barato para extraer, bueno para razonar.
#   3. Puedo validar entre pasos y cortar antes de gastar en el siguiente.
#   4. Un paso se puede paralelizar sin tocar los demás.
# A cambio: más latencia y más código.
