"""JSON garantizado por schema, en vez de parsear texto libre."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, Field

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

TEXTO = (
    "Hola, soy Jane Doe (jane@empresa.com). Estamos evaluando el plan "
    "Enterprise para un equipo de 40 personas. Nos interesan sobre todo la API "
    "y los SDKs, y nos gustaría ver una demo la semana que viene."
)


# Ruta que uso por defecto: parse() + Pydantic, ya validado.
class Lead(BaseModel):
    nombre: str
    email: str
    plan: str = Field(description="Plan de interés mencionado")
    tamano_equipo: int
    intereses: list[str]
    quiere_demo: bool


response = client.messages.parse(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Extrae los datos del lead:\n\n{TEXTO}"}],
    output_format=Lead,
)

lead = response.parsed_output
print_block(
    "messages.parse() + Pydantic",
    f"nombre        : {lead.nombre}\n"
    f"email         : {lead.email}\n"
    f"plan          : {lead.plan}\n"
    f"tamaño equipo : {lead.tamano_equipo}\n"
    f"intereses     : {', '.join(lead.intereses)}\n"
    f"quiere demo   : {lead.quiere_demo}",
    "green",
)


# Misma idea sin Pydantic.
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Extrae los datos del lead:\n\n{TEXTO}"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string"},
                    "email": {"type": "string"},
                    "plan": {"type": "string"},
                    "quiere_demo": {"type": "boolean"},
                },
                "required": ["nombre", "email", "plan", "quiere_demo"],
                "additionalProperties": False,
            },
        }
    },
)

datos = json.loads(extract_text(response))
print_block("output_config.format", json.dumps(datos, indent=2, ensure_ascii=False))

# El prefill del turno assistant que enseña el curso da 400 hoy:
#   {"role": "assistant", "content": '{"nombre": "'}
# Con el schema además me ahorro las stop_sequences, el regex y los reintentos.
#
# El schema no soporta: recursividad, minimum/maximum, minLength/maxLength.
# additionalProperties: false es obligatorio en cada objeto.
