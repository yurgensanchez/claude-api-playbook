# 01 — Introducción

Módulo teórico. No hay código; sirve para fijar vocabulario antes de empezar.

## Lecciones

- [ ] Bienvenida al curso
- [ ] Panorama de los modelos de Claude

## Familias de modelos

| Familia | Para qué | Modelo actual |
|---|---|---|
| **Opus** | Trabajo agéntico largo, código complejo, razonamiento profundo | `claude-opus-5` |
| **Sonnet** | Equilibrio calidad/coste para producción de alto volumen | `claude-sonnet-5` |
| **Haiku** | Tareas simples, clasificación, latencia mínima | `claude-haiku-4-5` |

Los IDs no llevan sufijo de fecha (salvo Haiku, que también acepta
`claude-haiku-4-5-20251001`). Inventarse un ID devuelve 404.

## Conceptos que hay que tener claros antes del módulo 02

- **La API es sin estado.** No hay "sesión": en cada petición mandas el
  historial completo de la conversación.
- **Todo pasa por un endpoint**, `POST /v1/messages`. Tools, structured outputs
  y thinking son parámetros de esa misma llamada, no APIs distintas.
- **La respuesta es una lista de bloques**, no una cadena. `response.content`
  puede traer bloques `text`, `thinking`, `tool_use`... Por eso nunca se lee
  `response.content[0].text` a ciegas.
- **`stop_reason`** dice por qué paró el modelo: `end_turn`, `max_tokens`,
  `tool_use`, `refusal`. Es lo primero que hay que mirar en un bucle agéntico.
- **Los tokens no son palabras.** Para contarlos se usa
  `client.messages.count_tokens()`, nunca `tiktoken` (es de OpenAI y subestima).

## Descubrir capacidades desde código

En vez de memorizar tablas, la Models API responde en vivo:

```python
from shared import get_client

m = get_client().models.retrieve("claude-opus-5")
print(m.display_name, m.max_input_tokens, m.max_tokens)
print(m.capabilities["image_input"]["supported"])
```

## Notas propias

<!-- Escribe aquí lo que te llame la atención de las lecciones. -->
