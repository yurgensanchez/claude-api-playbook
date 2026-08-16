"""Cliente MCP: conecta por stdio y convierte las primitivas a tipos de la API.

Requiere:  pip install "anthropic[mcp]"   (Python 3.10+)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from anthropic.lib.tools.mcp import async_mcp_tool, mcp_message, mcp_resource_to_content
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from shared.client import MODEL, get_async_client
from shared.utils import console

SERVIDOR = Path(__file__).resolve().parent.parent / "servidor" / "server.py"


async def main() -> None:
    client = get_async_client()

    parametros = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVIDOR)],
        cwd=str(SERVIDOR.parent),  # para que los imports del servidor resuelvan
    )

    async with stdio_client(parametros) as (read, write):
        async with ClientSession(read, write) as mcp_client:
            await mcp_client.initialize()

            tools = await mcp_client.list_tools()
            recursos = await mcp_client.list_resources()
            plantillas = await mcp_client.list_prompts()

            console.print("[bold]El servidor expone:[/bold]")
            console.print(f"  tools    : {[t.name for t in tools.tools]}")
            console.print(f"  recursos : {[str(r.uri) for r in recursos.resources]}")
            console.print(f"  prompts  : {[p.name for p in plantillas.prompts]}\n")

            # 1. Tools con el tool runner.
            console.print("[bold cyan]1. Tools[/bold cyan]")
            runner = client.beta.messages.tool_runner(
                model=MODEL,
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": "¿Tenéis stock del TCL-001? Si hay más de 20, resérvame 3.",
                }],
                tools=[async_mcp_tool(t, mcp_client) for t in tools.tools],
            )
            async for mensaje in runner:
                for bloque in mensaje.content:
                    if bloque.type == "text":
                        console.print(bloque.text)
                    elif bloque.type == "tool_use":
                        console.print(f"[dim]-> {bloque.name}({bloque.input})[/dim]")

            # 2. Un recurso como contexto.
            console.print("\n[bold cyan]2. Recursos[/bold cyan]")
            recurso = await mcp_client.read_resource("catalogo://politicas/devoluciones")

            respuesta = await client.beta.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        mcp_resource_to_content(recurso),
                        {"type": "text", "text": "Resume esta política en una frase."},
                    ],
                }],
            )
            for bloque in respuesta.content:
                if bloque.type == "text":
                    console.print(bloque.text)

            # 3. Un prompt del servidor.
            console.print("\n[bold cyan]3. Prompts[/bold cyan]")
            prompt = await mcp_client.get_prompt(
                name="revisar_disponibilidad", arguments={"sku": "MON-010"}
            )

            respuesta = await client.beta.messages.create(
                model=MODEL,
                max_tokens=2048,
                messages=[mcp_message(m) for m in prompt.messages],
                tools=[async_mcp_tool(t, mcp_client) for t in tools.tools],
            )
            for bloque in respuesta.content:
                if bloque.type == "text":
                    console.print(bloque.text)


if __name__ == "__main__":
    asyncio.run(main())

# Helpers del SDK:
#   async_mcp_tool / mcp_tool        tool MCP -> tool de la API
#   mcp_message                      mensaje de prompt MCP -> MessageParam
#   mcp_resource_to_content          recurso MCP -> bloque de contenido
#   mcp_resource_to_file             recurso MCP -> archivo para la Files API
# Lanzan UnsupportedMCPValueError si el valor no tiene equivalente.
#
# tool_runner es síncrono aunque el cliente sea async: devuelve el runner, no
# una corrutina. Se itera con async for.
