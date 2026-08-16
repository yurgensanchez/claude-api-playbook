"""Servidor MCP — punto de entrada.

Probar con el inspector:
    npx @modelcontextprotocol/inspector python 08-mcp/servidor/server.py
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("catalogo")

# El registro se hace por import: cada módulo decora sus funciones sobre
# esta misma instancia.
import herramientas  # noqa: E402,F401
import prompts  # noqa: E402,F401
import recursos  # noqa: E402,F401


if __name__ == "__main__":
    # stdio: el cliente lanza este proceso y habla por stdin/stdout.
    # La alternativa es HTTP streamable para servidores remotos.
    mcp.run(transport="stdio")
