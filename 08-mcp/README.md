# 08 — Model Context Protocol (MCP)

Proyecto: construir un servidor MCP con herramientas, recursos y prompts, y un
cliente que lo consuma.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Introducción a MCP / clientes MCP | este README |
| Setup del proyecto | [`servidor/`](servidor/) y [`cliente/`](cliente/) |
| Definir herramientas con MCP | [`servidor/herramientas.py`](servidor/herramientas.py) |
| El server inspector | ver más abajo |
| Implementar un cliente | [`cliente/cliente.py`](cliente/cliente.py) |
| Definir recursos | [`servidor/recursos.py`](servidor/recursos.py) |
| Acceder a recursos | [`cliente/cliente.py`](cliente/cliente.py) |
| Definir prompts | [`servidor/prompts.py`](servidor/prompts.py) |
| Prompts en el cliente | [`cliente/cliente.py`](cliente/cliente.py) |

## Qué problema resuelve MCP

Sin MCP, cada integración es a medida: escribes el esquema de la herramienta, la
implementación y el pegamento, para cada aplicación que la vaya a usar. Con MCP
defines la capacidad **una vez** en un servidor, y cualquier cliente compatible
(Claude Desktop, Claude Code, tu propia app) la consume.

Es un protocolo, no una librería de Anthropic para Anthropic: es abierto.

## Las tres primitivas

| Primitiva | Quién la controla | Analogía |
|---|---|---|
| **Tools** | El modelo decide cuándo llamarlas | función / endpoint POST |
| **Resources** | La aplicación decide qué exponer | archivo / endpoint GET |
| **Prompts** | El usuario los invoca | plantilla o slash-command |

La confusión típica: meterlo todo como tool. Un dato que se lee sin efectos
secundarios es un **recurso**, no una herramienta.

## Estructura

```
08-mcp/
├── servidor/
│   ├── server.py         punto de entrada, registra todo
│   ├── herramientas.py   @mcp.tool()
│   ├── recursos.py       @mcp.resource()
│   └── prompts.py        @mcp.prompt()
└── cliente/
    └── cliente.py        conecta por stdio y convierte a tipos de la API
```

## El inspector

Antes de escribir el cliente, prueba el servidor a mano:

```bash
npx @modelcontextprotocol/inspector python 08-mcp/servidor/server.py
```

Abre una UI web donde ves las herramientas registradas, sus esquemas, y puedes
invocarlas con parámetros. Depurar aquí es mucho más rápido que hacerlo a
través del modelo.

## Tres formas de consumir MCP desde la API de Claude

1. **Helpers del SDK** (`anthropic.lib.tools.mcp`) — conectas al servidor MCP
   desde tu código y conviertes sus tools con `mcp_tool()` / `async_mcp_tool()`
   para pasarlas al tool runner. Es lo que hace el cliente de este módulo.
2. **MCP connector** (`mcp_servers` en la petición) — Anthropic se conecta
   directamente a un servidor MCP remoto por ti. Requiere el beta
   `mcp-client-2025-11-20` y **dos** parámetros: `mcp_servers` **y** una entrada
   `{"type": "mcp_toolset", "mcp_server_name": ...}` en `tools`. Faltando una,
   la petición se rechaza.
3. **Managed Agents** — el servidor MCP se declara en el agente y las
   credenciales van en un vault.

## Notas propias

<!-- Tus apuntes del módulo. -->
