# 09 — Apps de Anthropic: Claude Code y Computer Use

Módulo mayoritariamente práctico-guiado, sin código propio en el repo. Aquí van
las notas y la configuración que sí conviene versionar.

## Lecciones

- [ ] Apps de Anthropic
- [ ] Setup de Claude Code
- [ ] Claude Code en acción
- [ ] Mejoras con servidores MCP

## Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude          # dentro de un repositorio
```

Disponible como CLI, app de escritorio (Mac/Windows), web (claude.ai/code) y
extensiones de IDE (VS Code, JetBrains).

Comandos que merece la pena conocer desde el principio:

| Comando | Para qué |
|---|---|
| `/init` | Genera un `CLAUDE.md` con la documentación del repo |
| `/config` | Modelo, tema y preferencias |
| `/mcp` | Gestiona servidores MCP conectados |
| `claude -p "..."` | Modo no interactivo, un turno y sale |
| `/code-review` | Revisión del diff actual |

## Conectar el servidor MCP del módulo 08

Este es el ejercicio con más valor del módulo: el servidor que construiste se
conecta a Claude Code y queda disponible como herramienta real.

```bash
claude mcp add catalogo -- python "<ruta>/08-mcp/servidor/server.py"
claude mcp list
```

Comprueba después con `/mcp` dentro de Claude Code que las tools aparecen.

## `CLAUDE.md`

Es el archivo de instrucciones que Claude Code lee en cada sesión. Lo que
conviene poner:

- arquitectura del proyecto y decisiones de diseño no obvias
- comandos reales (test, lint, build) — con la sintaxis exacta
- convenciones del repo que no se deducen del código

Lo que **no** conviene poner:

- conocimiento general de programación
- rutas y versiones hardcodeadas que se quedarán obsoletas
- narrativa histórica ("antes hacíamos X, luego cambiamos a Y")
- reglas escritas a partir de un único tropiezo de una sesión

## Computer Use

Claude toma capturas de pantalla y emite acciones de ratón/teclado; **el entorno
lo pones tú**. Está en beta y conviene ejecutarlo siempre en una VM o contenedor
aislado, nunca contra tu escritorio real.

Recomendaciones actuales: capturas a 1080p (buen equilibrio calidad/coste),
720p o 1366×768 si el coste importa mucho.

## Notas propias

<!-- Qué te ha resultado más útil, qué configuración has dejado montada. -->
