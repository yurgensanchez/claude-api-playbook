# Setup

## Requisitos

- Python 3.10 o superior (el curso usa `match/case` en algunos ejemplos)
- Una cuenta en [console.anthropic.com](https://console.anthropic.com) con crédito
- Git

## Instalación paso a paso

```bash
cd Building-with-the-Claude-API

python -m venv .venv
.venv\Scripts\activate            # Windows PowerShell / CMD
# source .venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

## API key

1. Entra a <https://console.anthropic.com/settings/keys> y crea una clave.
2. Copia `.env.example` a `.env`.
3. Pega la clave en `ANTHROPIC_API_KEY`.

`.env` está en `.gitignore`. **Nunca** hardcodees la clave en un `.py`.

### Alternativa: perfil OAuth

Si tienes el CLI `ant` instalado, `ant auth login` guarda un perfil que el SDK
recoge automáticamente y no necesitas variable de entorno. `ant auth status`
muestra qué credencial está activa. Ojo: una `ANTHROPIC_API_KEY` exportada
tiene prioridad sobre el perfil.

## Verificación

```bash
python -m shared.check
```

Debe imprimir `OK`, el modelo que respondió y el estado de las dependencias por módulo.

## Cómo ejecutar los ejercicios

Siempre desde la raíz del repositorio, para que `shared/` se resuelva como paquete:

```bash
python 02-acceso-api/01_primera_peticion.py
```

Si ves `ModuleNotFoundError: No module named 'shared'`, es que estás ejecutando
desde dentro de la carpeta del módulo. Vuelve a la raíz.

## Control de coste

- Los ejercicios usan `max_tokens` conservadores.
- Para tandas grandes (módulo 03, evals), cambia a `CLAUDE_MODEL_FAST` en `.env`.
- `shared.utils.count_tokens()` estima el coste de entrada antes de enviar.
- Revisa el gasto en <https://console.anthropic.com/settings/usage>.
